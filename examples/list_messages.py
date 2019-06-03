import time
from utils.kafka.TimeOrderedConsumer import TimeOrderedConsumer, ConsumerType, TopicInfo, OFFSET_END


# Configuration  data
TopicFVector="example.cam.fvecs.FeatureVectorRecord.json"
TopicImage="example.cam.lowres.Image.jpg"
Server="example_server"
GroupId='group_id'

# server connection
begin = OFFSET_END
topic_infos = [
   TopicInfo(topic=TopicFVector, begin=begin)
  ,TopicInfo(topic=TopicImage, begin=begin)
]
consumer = TimeOrderedConsumer(Server, GroupId, topic_infos, ConsumerType.live)

# print messages to console
for msg in consumer.getMessages():
  epoch=msg.timestamp()[1]
  timestamp=time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(epoch/1000))
  print(timestamp,msg.topic())

