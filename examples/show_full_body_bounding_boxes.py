import cv2
import numpy as np
import json
from utils.kafka.TimeOrderedConsumer import TimeOrderedConsumer, ConsumerType, TopicInfo, OFFSET_END

# Configuration data
TopicDetection="example.cam.fb_crops.ObjectDetectionRecord.json"
TopicImage="example.cam.lowres.Image.jpg"
TopicFrameInfo="example.cam.frameinfo.FrameInfoRecord.json"
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
  ,TopicInfo(topic=TopicFrameInfo, begin=begin)
  ,TopicInfo(topic=TopicDetection, begin=begin)
]
consumer = TimeOrderedConsumer(Server, GroupId, topic_infos, ConsumerType.live)

# display bounding boxes on the video stream
for msgs in groupByTimeConsumer(consumer):

  for msg in msgs:
    if msg.topic().endswith(".jpg"):
      img = cv2.imdecode(np.fromstring(msg.value(), dtype=np.uint8),-1)

  for msg in msgs:
    if msg.topic().endswith("FrameInfoRecord.json"):
      rec = json.loads(msg.value().decode('utf-8'))
      cols = rec['columns']
      rows = rec['rows']

  for msg in msgs:
    if msg.topic().endswith("ObjectDetectionRecord.json"):
      rec = json.loads(msg.value().decode('utf-8'))
      if 'bounding_box' in rec:
        bb = rec['bounding_box']
        x = max(0, bb['x'])
        y = max(0, bb['y'])
        w = min(cols - x, bb['width'])
        h = min(rows - y, bb['height'])
        if w > 0 and h > 0:
          cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

  cv2.imshow('display',img)
  cv2.waitKey(1)

