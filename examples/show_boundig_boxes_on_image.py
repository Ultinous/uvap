import cv2
import numpy as np
import json
from utils.kafka.TimeOrderedConsumer import TimeOrderedConsumer, ConsumerType, TopicInfo, OFFSET_END

# Configuration data
TopicDetection="example.cam.dets.ObjectDetectionRecord.json"
TopicImage="example.cam.lowres.Image.jpg"
Server="example_server"
GroupId='group_id'


# collect messages based on timestamp
def groupByTimeConsumer(consumer):
  rec = []
  for msg in consumer.getMessages():
    if len(rec)==0:
      rec = [msg]
    else:
      if msg.timestamp()[1] != rec[0].timestamp()[1]:
        yield rec
        rec = [msg]
      else:
        rec.append(msg)
  if len(rec)>0:
    yield rec

# server connection
begin = OFFSET_END
topic_infos = [
  TopicInfo(topic=TopicImage, begin=begin)
  ,TopicInfo(topic=TopicDetection, begin=begin)
]
consumer = TimeOrderedConsumer(Server, GroupId, topic_infos, ConsumerType.live)

# display bounding boxes on the video stream
for msgs in groupByTimeConsumer(consumer):

  for msg in msgs:
    if msg.topic().endswith(".jpg"):
      img = cv2.imdecode(np.fromstring(msg.value(), dtype=np.uint8),-1)

  for msg in msgs:
    if msg.topic().endswith(".json"):
      rec = json.loads(msg.value().decode('utf-8'))
      if 'bounding_box' in rec:
        bb = rec['bounding_box']
        x = bb['x']
        y = bb['y']
        w = bb['width']
        h = bb['height']
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

  cv2.imshow('display',img)
  cv2.waitKey(1)

