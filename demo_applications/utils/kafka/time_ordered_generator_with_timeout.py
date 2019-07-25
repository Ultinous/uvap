import time
import logging
from collections import deque
from typing import List, Deque
from enum import Enum
from confluent_kafka import Consumer, TopicPartition, OFFSET_END, OFFSET_BEGINNING, OFFSET_STORED, KafkaError
from utils.generator_interface import GeneratorInterface
from utils.heartbeat import HeartBeat

class BeginFlag(Enum):
    """ Start consuming messages from the beginnig of the steams."""
    BEGINNING = 0
    """ Continue from the last committed offset. If there is no committed it will run from the end of the stream."""
    CONTINUE = 1
    """ It will start reading from the end of the streams."""
    LIVE = 2

class EndFlag(Enum):
    """ The generator will never stop. Will work on live streams. """
    NEVER = 0
    """ The generator will stop at the end of the stream. """
    END_OF_PARTITION = 1

def getSystemTimestamp():
    return int(time.time() * 1000)

class MessageExtension:
    """
    Technical wrapper around kafka message. Stores the system timestamp for each kafka message when it was received.
    """
    def __init__(self, msg):
        self.message = msg
        self.ts = getSystemTimestamp()
        logging.debug(
            'New message added to queue {} at system time {} with event time: {} diff: {}'
            .format(
                self.message.topic()
                , self.ts
                , self.message.timestamp()[1]
                , self.ts - self.message.timestamp()[1]
            )
        )

class TopicInfo:
    def __init__(self, topic, partition = 0, drop = True):
      """
      :param topic: Name of the topic.
      :param partition: Partition number.
      :param drop: False: we do not drop any message. True: we drop messages arrived after the timestamp was served.
      """
      if len(topic) > 200:
          raise Exception('Kafka does not support topic names longer then 255 char.Topic provided: ' + topic)
      self.topic = topic
      self.partition = partition
      self.drop = drop

class Topic:
    """
    Wrapper around the topics. Stores a queue for the messages read from the kafka broker.
    Invariants: A topics is paused only when exceeds the number if max limits.
                The topics will be restarted (unpaused) when the number of messages are below min_limit.
                The topics will be stopped:
                    1) END_OF_PARTITION: if they reach the highest offset taken at construction time.
                    2) TIMESTAMP: if the generator reached the given timestamp.
                The self.stopped is false if and only if the TopicPartition for this topic is paused for this consumer.
                self.last_message_ts stored the last emitted message timestamp.
                self.end_of_partition is true if and only if the last message was EOF.
    """
    def __init__(
        self
        , topic
        , consumer
        , partition
        , end_offset = None
        , drop = True
        , min_limit = 1000
        , max_limit = 100000
    ):
        self.paused = False
        self.partition = partition
        self.min_limit = min_limit
        self.max_limit = max_limit
        self.queue: Deque[MessageExtension] = deque()
        self.end_offset = end_offset
        self.last_message_ts = None
        self.drop = drop
        self.consumer_ref = consumer
        self.topic_name = topic
        self.stopped = False
        self.end_of_partition = False
        self.first_eop_reached = False

    def add_message(self, msg):
        if self.stopped:
            logging.debug('Topic {} stopped.'.format(self.topic_name))
            return
        if self.last_message_ts is not None and self.drop and msg.timestamp()[1] <= self.last_message_ts:
            logging.info(
                'Drop from topic {} at system time {} for the event time {}. Last timestamp for this topic was {}.'
                'If you wish not to drop messages turn drop=False in the constructor.'
                .format(
                    self.topic_name
                    , getSystemTimestamp()
                    , msg.timestamp()[1]
                    , self.last_message_ts
                )
            )
        else:
            self.queue.append(MessageExtension(msg))
        if self.end_offset is not None and msg.offset() == self.end_offset:
            logging.debug('On topic {} we reached the end offset {}.'.format(self.topic_name, self.end_offset))
            self.stop_topic()
        if len(self.queue) > self.max_limit and not self.paused:
            self.pause_topic()

    def pause_topic(self):
        if not self.paused:
            logging.info('Topic {} paused.'.format(self.topic_name))
            self.paused = True
            self.consumer_ref.pause([TopicPartition(topic = self.topic_name, partition = self.partition)])

    def stop_topic(self):
        self.stopped = True
        self.pause_topic()
        logging.debug('Topic {} stopped.'.format(self.topic_name))

    def get_messages(self, timestamp):
        ret = []
        while len(self.queue) > 0 and self.queue[0].message.timestamp()[1] <= timestamp:
            ret.append(self.queue.popleft().message)
        if len(self.queue) < self.min_limit and self.paused and not self.stopped:
            logging.debug('Resume reading on topic: {}'.format(self.topic_name))
            self.paused = False
            self.consumer_ref.resume([TopicPartition(topic=self.topic_name, partition=self.partition)])
        self.last_message_ts = timestamp
        return ret

    def can_be_emitted(self, event_ts):
        if self.paused or self.end_of_partition:
            return True
        if len(self.queue) == 0:
            return False
        if event_ts < self.queue[0].message.timestamp()[1]:
            return True
        elif event_ts == self.queue[0].message.timestamp()[1]:
            return self.first_eop_reached
        else:
            # This shouldn't happen but who knows.
            return True

class TimeOrderedGeneratorWithTimeout(GeneratorInterface):
    """
    A general generator which can read multiple topics and merge their messages in time order.
    A message must be emitted at (arrival_system_time + latency_ms).
    In batch mode (until reaching the first EOP on each stream) the generator will not discard any messages.
    """
    def __init__(
        self
        , broker
        , groupid
        , topics_infos: List[TopicInfo]
        , latency_ms
        , commit_interval_sec = None
        , group_by_time = False
        , begin_timestamp = None
        , begin_flag = None
        , end_timestamp = None
        , end_flag = None
        , heartbeat_interval_ms = -1
    ):
        """
        :param broker: Broker to connect to.
        :param groupid: Group id of the consumer.
        :param topics_infos: [TopicInfo()] - list of TopicInfo objects.
        :param latency_ms: (integer >=0) Latency to wait before serving a message.
                            After this messages with lower or equal timestamps will be discarded.
        :param commit_interval_sec: How many seconds to wait between commits.-1 does not commit with the given group id.
        :param group_by_time: Group messages with the same timestamp. This will yield a list of messages.
        :param begin_timestamp: Timestamp of the kafka messages where the generator will start.
        :param begin_flag: BEGINNING, CONTINUE, LIVE - CONTINUE will continue from the last committed offset.
                            If there was no committed offset will start from the end of the stream.
        :param end_timestamp: Timestamp where to end the reading.
        :param end_flag: NEVER, END_OF_PARTITION
        :param heartbeat_interval_ms: -1 does not produce heartbeat. After every interval will produce a HeartBeat typed
                                        message with the timestamp.
        """
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
            {
                'bootstrap.servers': broker
                , 'group.id': groupid
                , 'enable.auto.commit': False
                , 'auto.offset.reset': 'latest'
                , 'enable.partition.eof': True
            }
        )
        self.tps = []
        self.queues = {}
        self.messages_to_be_committed = {}
        self.begin_timestamp = begin_timestamp
        for ti in topics_infos:
            topic_name = ti.topic
            self.messages_to_be_committed[topic_name] = {'last_msg': None, 'committed': True}
            if begin_timestamp is not None:
                self.tps.extend(self.consumer.offsets_for_times([TopicPartition(topic_name, partition = ti.partition, offset = begin_timestamp)]))
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
                self.queues[topic_name] = Topic(
                    topic_name
                    , self.consumer
                    , end_offset = end_offset
                    , partition = ti.partition
                    , drop = ti.drop
                )
        self.consumer.assign(self.tps)
        self.last_commit = time.time()
        self.running = True
        self.heartbeat_interval_ms = heartbeat_interval_ms
        self.next_hb = None

    def stopGenerator(self):
        self.running = False

    def _serve_messages(self, message_to_serve):
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

    def _serve_heartbeat(self, current_timestamp_ms):
        if self.next_hb is None:
            if self.begin_timestamp is not None:
                self.next_hb = self.begin_timestamp
            else:
                self.next_hb = current_timestamp_ms
        while self.next_hb <= current_timestamp_ms:
            yield HeartBeat(self.next_hb)
            self.next_hb += self.heartbeat_interval_ms

    def _can_serve(self):
        min_ets = min([q.queue[0].message.timestamp()[1] for q in self.queues.values() if len(q.queue) > 0], default = -1)
        if min_ets == -1:
            return None
        deadline = getSystemTimestamp() - self.latency_ms
        if all([q.can_be_emitted(min_ets) for q in self.queues.values()]) and \
              any([q.queue[0].ts < deadline for q in self.queues.values()
                if len(q.queue) > 0 and q.queue[0].message.timestamp()[1] == min_ets]):
            return min_ets
        else:
            return None

    def getMessages(self):
        while self.running:
            if all([v.stopped for v in self.queues.values()]):
                message_to_serve = []
                for q in self.queues.values():
                    message_to_serve.extend(q.queue)
                message_to_serve = [m.message for m in message_to_serve]
                message_to_serve.sort(key=lambda x: x.timestamp()[1])
                while len(message_to_serve) > 0:
                    ts = message_to_serve[0].timestamp()[1]
                    serve_it = []
                    while len(message_to_serve) > 0 and message_to_serve[0].timestamp()[1] == ts:
                        serve_it.append(message_to_serve.pop(0))
                        if not self.heartbeat_interval_ms == -1:
                            yield from self._serve_heartbeat(ts)
                        yield from self._serve_messages(serve_it)
                logging.debug('Exiting from generator.')
                break
            msg = self.consumer.poll(0.001)
            if msg is not None:
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        if msg.topic() in self.queues:
                            self.queues[msg.topic()].first_eop_reached = True
                            self.queues[msg.topic()].end_of_partition = True
                    else:
                        logging.error('Unhandle error: {}'.format(msg.error()))
                        break
                else:
                    self.queues[msg.topic()].end_of_partition = False
                    if self.end_ts is not None and msg.timestamp()[1] > self.end_ts:
                        self.queues[msg.topic()].stop_topic()
                    else:
                        self.queues[msg.topic()].add_message(msg)
            while self.running:
                event_ts_to_serve = self._can_serve()
                if event_ts_to_serve is None:
                    if self.end_flag == EndFlag.NEVER and self.heartbeat_interval_ms != -1 \
                      and any([q.end_of_partition for q in self.queues.values()]):
                        if self.next_hb is None:
                            self.next_hb = getSystemTimestamp()-self.latency_ms
                        yield from self._serve_heartbeat(getSystemTimestamp() - self.latency_ms)
                    break
                if self.heartbeat_interval_ms != -1:
                    yield from self._serve_heartbeat(event_ts_to_serve)
                message_to_serve = []
                for q in self.queues.values():
                    message_to_serve.extend(q.get_messages(event_ts_to_serve))
                yield from self._serve_messages(message_to_serve)
                if self.end_ts is not None and self.end_ts <= event_ts_to_serve:
                    self.running = False
        self.consumer.close()
