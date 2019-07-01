from collections import deque
from confluent_kafka import Consumer, TopicPartition, OFFSET_END, OFFSET_BEGINNING, OFFSET_STORED
import time
from typing import List
import logging
from enum import Enum


class BeginFlag(Enum):
    BEGINNING = 0
    CONTINUE = 1
    LIVE = 2


class EndFlag(Enum):
    NEVER = 0
    END_OF_PARTITION = 1


def getSystemTimestamp():
    return int(time.time() * 1000)


class MessageExtension:
    def __init__(self, msg):
        self.message = msg
        self.ts = getSystemTimestamp()
        logging.debug('New message added to queue {} at system time {} with event time: {} diff: {}'
                      .format(self.message.topic(), self.ts, self.message.timestamp()[1],
                              self.ts - self.message.timestamp()[1]))


class TopicInfo:
    def __init__(self, topic, partition=0, drop=True):
        if len(topic) > 200:
            raise Exception('Kafka does not support topic names longer then 255 char.Topic provided: ' + topic)
        self.topic = topic
        self.partition = partition
        self.drop = drop


class Topic:
    def __init__(self, topic, consumer, partition, end_offset=None, drop=True, min_limit=1000, max_limit=10000):
        self.paused = False
        self.partition = partition
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.queue = deque()
        self.end_offset = end_offset
        self.last_message_ts = None
        self.drop = drop
        self.consumer_ref = consumer
        self.topic_name = topic
        self.stopped = False

    def add_message(self, msg):
        if self.last_message_ts is not None and self.drop and msg.timestamp()[1] <= self.last_message_ts:
            logging.info(
                'Drop from topic {} at system time {} for the event time {}. Last timestamp for this topic was {}.'
                'If you wish not to drop messages turn drop=False in the constructor.'
                .format(msg.topic(), getSystemTimestamp(), msg.timestamp()[1], self.last_message_ts))
        else:
            self.queue.append(MessageExtension(msg))
        if self.end_offset is not None and msg.offset() == self.end_offset:
            self.stop_topic()
        if len(self.queue) > self.max_limit and not self.paused:
            self.paused = True
            self.consumer_ref.pause([TopicPartition(topic=self.topic_name, partition=self.partition)])

    def pause_topic(self):
        if not self.paused:
            self.paused = True
            self.consumer_ref.pause([TopicPartition(topic=self.topic_name, partition=self.partition)])

    def stop_topic(self):
        self.stopped = True
        self.pause_topic()

    def get_messages(self, timestamp):
        ret = []
        while len(self.queue) > 0 and self.queue[0].message.timestamp()[1] <= timestamp:
            ret.append(self.queue.popleft().message)
        if len(self.queue) < self.min_limit and self.paused and not self.stopped:
            self.paused = False
            self.consumer_ref.resume([TopicPartition(topic=self.topic_name, partition=self.partition)])
        self.last_message_ts = timestamp
        return ret


class TimeOrderedGeneratorWithTimeout:
    def __init__(self, broker, groupid, topics_infos: List[TopicInfo], latency_ms, commit_interval_sec=None,
                 group_by_time=False, begin_timestamp=None, begin_flag=None, end_timestamp=None, end_flag=None):
        if begin_timestamp is not None and begin_flag is not None:
            raise Exception('You can set the begin timestamp and a flag in the same time.')
        if end_timestamp is not None and end_flag is not None:
            raise Exception('You can set the end timestamp and a flag in the same time.')
        if begin_timestamp is not None and end_timestamp is not None and begin_timestamp >= end_timestamp:
            raise Exception('The begin timestamp is larger then the end timestamp.')
        if begin_flag is not None and end_flag is not None and \
                begin_flag == BeginFlag.LIVE and end_flag == EndFlag.END_OF_PARTITION:
            raise Exception('You can not start in live and process until the end of the streams.')
        if end_flag is not None and not (end_flag == EndFlag.END_OF_PARTITION or end_flag == EndFlag.NEVER):
            raise Exception('Unknow end flag: {} . Please use the given enum to use proper end flag.'.format(end_flag))
        self.end_ts = end_timestamp
        self.end_flag = end_flag
        self.commit_interval_sec = commit_interval_sec
        self.latency_ms = latency_ms
        self.group_by_time = group_by_time
        self.consumer = Consumer(
            {'bootstrap.servers': broker,
             'group.id': groupid,
             'enable.auto.commit': False,
             'auto.offset.reset': 'latest',
             'enable.partition.eof': False})
        self.tps = []
        self.queues = {}
        self.messages_to_be_committed = {}
        for ti in topics_infos:
            topic_name = ti.topic
            self.messages_to_be_committed[topic_name] = {'last_msg': None, 'committed': True}
            if begin_timestamp is not None:
                self.tps.extend(self.consumer.offsets_for_times(
                    [TopicPartition(topic_name, partition=ti.partition, offset=begin_timestamp)]))
            elif begin_flag is not None:
                if begin_flag == BeginFlag.BEGINNING:
                    self.tps.append(TopicPartition(topic_name, partition=ti.partition, offset=OFFSET_BEGINNING))
                elif begin_flag == BeginFlag.CONTINUE:
                    self.tps.append(TopicPartition(topic_name, partition=ti.partition, offset=OFFSET_STORED))
                elif begin_flag == BeginFlag.LIVE:
                    self.tps.append(TopicPartition(topic_name, partition=ti.partition, offset=OFFSET_END))
                else:
                    raise Exception('Unknown begin flag. Please use the enum to provide proper begin flag.')
            else:
                self.tps.append(TopicPartition(topic_name, partition=ti.partition, offset=OFFSET_END))
            end_offset = None
            if end_flag is not None and end_flag == EndFlag.END_OF_PARTITION:
                end_offset = self.consumer.get_watermark_offsets(TopicPartition(topic_name, 0))[1] - 1
            if end_offset is None or end_offset >= 0:
                self.queues[topic_name] = Topic(topic_name, self.consumer, end_offset=end_offset,
                                                partition=ti.partition, drop=ti.drop)
        self.consumer.assign(self.tps)
        self.last_commit = time.time()
        self.running = True

    def stop_generator(self):
        self.running = False

    def getMessage(self):
        next_dead_line = None
        while self.running:
            if all([v.stopped for v in self.queues.values()]):
                break
            new_msgs = self.consumer.consume(10000, 0.001)
            while self.running and any([not msg.error() for msg in new_msgs]):
                for msg in new_msgs:
                    if self.end_ts is not None and msg.timestamp()[1] > self.end_ts:
                        self.queues[msg.topic()].stop_topic()
                    else:
                        self.queues[msg.topic()].add_message(msg)
                new_msgs = self.consumer.consume(10000, 0.001)
            for err in new_msgs:
                logging.error('KafkaError: {}'.format(err.error()))
            while self.running and (next_dead_line is None or next_dead_line <= getSystemTimestamp()):
                min_event_ts = \
                    min([q.queue[0].message.timestamp()[1] for q in self.queues.values() if len(q.queue) > 0],
                        default=None)
                if min_event_ts is None:
                    break
                min_systm_ts = min([q.queue[0].ts for q in self.queues.values()
                                    if len(q.queue) > 0 and q.queue[0].message.timestamp()[1] == min_event_ts])
                next_dead_line = min_systm_ts + self.latency_ms
                if next_dead_line > getSystemTimestamp():
                    break
                message_to_serve = []
                for q in self.queues.values():
                    message_to_serve.extend(q.get_messages(min_event_ts))
                if self.commit_interval_sec is not None and self.group_by_time:
                    for msg in message_to_serve:
                        self.messages_to_be_committed[msg.topic()]['last_msg'] = msg
                        self.messages_to_be_committed[msg.topic()]['committed'] = False

                # serve messages
                if self.group_by_time:
                    yield message_to_serve
                else:
                    for msg in message_to_serve:
                        self.messages_to_be_committed[msg.topic()]['last_msg'] = msg
                        self.messages_to_be_committed[msg.topic()]['committed'] = False
                        yield msg
                        if not self.running:
                            break

                # commit messages when they were delivered
                current_time = time.time()
                if self.commit_interval_sec is not None and (
                        current_time - self.last_commit) > self.commit_interval_sec:
                    for k in self.messages_to_be_committed.keys():
                        if not self.messages_to_be_committed[k]['committed']:
                            self.consumer.commit(self.messages_to_be_committed[k]['last_msg'])
                            self.messages_to_be_committed[k]['committed'] = True
                    self.last_commit = current_time
        self.consumer.close()
