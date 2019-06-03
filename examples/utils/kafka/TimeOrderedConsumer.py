import sys
from confluent_kafka import Consumer, TopicPartition, KafkaError, OFFSET_END
from enum import Enum

# Create the kafka consumer with the given parameters and process the message queue

class ConsumerType(Enum):
  batch = 1
  live = 2


class OffsetType(Enum):
  offset = 1
  timestamp = 2

class TopicTooLongException(Exception):
  pass

class TopicInfo:
  def __init__(self, topic, begin=0, end=OFFSET_END, partition=0, offset_type=OffsetType.offset):
    if len(topic) > 200:
      raise TopicTooLongException('Kafka does not support topic names longer then 255 char.Topic provided: '+topic)
    self.topic = topic
    self.begin = begin
    self.end = end
    self.partition = partition
    self.offset_type = offset_type


# topics = [topic_name,begin,end,offset_type={offset,time}]
class TimeOrderedConsumer:
  '''
  topic_infos: list of TopicInfos
  consumer_type: ConsumerType.live or ConsumerType.batch
  '''

  def __init__(self, server, group_id, topic_infos, consumer_type=ConsumerType.live, min_queue_size=5000,
               max_queue_size=10000):
    self.consumer_type = consumer_type
    self.min_queue_size = min_queue_size
    self.max_queue_size = max_queue_size
    self.queues = {}
    self.paused = {}
    self.eof = {}
    self.num_of_eofs = 0
    self.consumer = Consumer({'bootstrap.servers': server, 'group.id': group_id})
    self.assingments = {}
    self.consumer_types = {}
    self.end_offsets = {}
    for topic_info in topic_infos:
      tp = TopicPartition(topic=topic_info.topic, partition=topic_info.partition, offset=topic_info.begin)
      if topic_info.offset_type == OffsetType.timestamp:
        tp = self.consumer.offsets_for_times([tp])[0]
      self.consumer_types[topic_info.topic] = topic_info.offset_type
      self.end_offsets[topic_info.topic] = topic_info.end
      self.assingments[topic_info.topic] = tp
      self.queues[topic_info.topic] = []
      self.paused[topic_info.topic] = False
      self.eof[topic_info.topic] = False
    self.consumer.assign(list(self.assingments.values()))
    self.poll = True
    self.timeout = 0.0

  def getMessages(self):
    while True:
      # select msg with oldest timestamp to emit
      emit_topic = None
      min_t = sys.maxsize
      for topic, q in self.queues.items():
        if len(q) == 0:
          if self.poll:
            emit_topic = None
            break
        else:
          t = q[0].timestamp()[1]
          if t < min_t:
            min_t = t
            emit_topic = topic

      # emit if possible
      if emit_topic == None:
        if not self.poll:
          break
      else:
        # emit and resume if queue is too low
        ret = self.queues[emit_topic].pop(0)
        if len(self.queues[emit_topic]) < self.min_queue_size and self.paused[emit_topic]:
          self.consumer.resume([self.assingments[emit_topic]])
          self.paused[emit_topic] = False
        if self.consumer_type == ConsumerType.batch:
          if len(self.queues[emit_topic]) == 0 and self.eof[emit_topic]:
            del self.queues[emit_topic]
        yield ret

      # get new message
      if self.poll:
        msg = self.consumer.poll(self.timeout)
        if msg == None:
          self.timeout = 0.1
          continue
        if msg.error():
          self.timeout = 0.1
          if msg.error().code() == KafkaError._PARTITION_EOF:
            self._pauseConsumer(msg.topic())
          continue

        # insert message to queue, pause the topic if its queue is full
        t = msg.topic()
        self.timeout = 0
        if self.consumer_type == ConsumerType.batch and self.end_offsets[t] != OFFSET_END and \
                (self.consumer_types[t] == OffsetType.timestamp and msg.timestamp()[1] > self.end_offsets[t] or
                 self.consumer_types[t] == OffsetType.offset and msg.offset() > self.end_offsets[t]):
          self._pauseConsumer(t)
        else:
          self.queues[t].append(msg)
          if len(self.queues[t]) >= self.max_queue_size and not self.paused[t]:
            self.consumer.pause([self.assingments[t]])
            self.paused[t] = True

  def _pauseConsumer(self, topic):
    if self.consumer_type == ConsumerType.batch:
      self.eof[topic] = True
      self.num_of_eofs += 1
      self.consumer.pause([self.assingments[topic]])
      if len(self.queues[topic]) == 0 and topic in self.queues:
        del self.queues[topic]
      if self.num_of_eofs >= len(self.consumer.assignment()):
        self.poll = False
