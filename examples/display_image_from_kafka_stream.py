import cv2
import numpy as np
from utils.kafka.TimeOrderedConsumer import TimeOrderedConsumer, ConsumerType, TopicInfo, OFFSET_END

# Configuration data
TopicImage="example.cam.lowres.Image.jpg"
Server="example_server"
GroupId='group_id'

# server connection
begin = OFFSET_END
topic_infos = [TopicInfo(topic=TopicImage, begin=begin)]
consumer = TimeOrderedConsumer(Server, GroupId, topic_infos, ConsumerType.live)

# read messages and display
for msg in consumer.getMessages():
  #print(msg.timestamp()[1],msg.topic())
  img = cv2.imdecode(np.fromstring(msg.value(), dtype=np.uint8),-1)
  cv2.imshow('display',img)
  cv2.waitKey(1)


