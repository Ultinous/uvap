import argparse
from typing import Dict

import cv2
import numpy as np
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position, draw_nice_text
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message

COLOR_ORANGE = (10, 95, 255)
COLOR_GREY = (97, 97, 97)
TITLE_REG = "DEMO: Registration"
TITLE_REID = "DEMO: Reidentification"
REG_CAMERA_ID = "0"
REID_CAMERA_ID = "1"
REID_TOPIC_ID = "99"


class Registration:
  def __init__(self, inner_id, time):
      self.inner_id = inner_id
      self.time = time


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Basic Reidentification demo using two cameras: 
           Camera0 for object registration and Camera1 for reidentification.
           
           Plays a video from a jpeg topic,
           visualizes head detection with an orange bounding box around a head
           and writes the dwell time and ID (derived from the reid MS ID) above the heads.
           
           Displays ('-d') or stores ('-o') the result of this demo in kafka topics.

           Required topics:
           - <prefix>.cam.0.original.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.1.original.Image.jpg
           - <prefix>.cam.1.dets.ObjectDetectionRecord.json
           - <prefix>.cam.1.reids.ReidRecord.json
           """
        , formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("prefix", help="Prefix of topics (base|skeleton).", type=str)
    parser.add_argument('-d', "--display", action='store_true')
    parser.add_argument('-o', '--output', help='write output image into kafka topic', action='store_true')
    args = parser.parse_args()

    if not args.display and not args.output:
        parser.error("Missing argument: -d (display output) or -o (write output to kafka) is needed")

    if args.output:
        producer = Producer({'bootstrap.servers': args.broker})

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    image_reg_topic = f"{args.prefix}.cam.{REG_CAMERA_ID}.original.Image.jpg"
    image_reid_topic = f"{args.prefix}.cam.{REID_CAMERA_ID}.original.Image.jpg"
    detection_reg_topic = f"{args.prefix}.cam.{REG_CAMERA_ID}.dets.ObjectDetectionRecord.json"
    detection_reid_topic = f"{args.prefix}.cam.{REID_CAMERA_ID}.dets.ObjectDetectionRecord.json"
    frameinfo_reg_topic = f"{args.prefix}.cam.{REG_CAMERA_ID}.frameinfo.FrameInfoRecord.json"
    frameinfo_reid_topic = f"{args.prefix}.cam.{REID_CAMERA_ID}.frameinfo.FrameInfoRecord.json"
    reid_topic = f"{args.prefix}.cam.{REID_TOPIC_ID}.reids.ReidRecord.json"
    output_reg_topic_name = f"{args.prefix}.cam.{REG_CAMERA_ID}.reids.Image.jpg"
    output_reid_topic_name = f"{args.prefix}.cam.{REID_CAMERA_ID}.reids.Image.jpg"

    # read message, draw and display them
    consumer = TimeOrderedGeneratorWithTimeout(
        broker=args.broker,
        groupid="detection",
        topics_infos=[
            TopicInfo(image_reg_topic),
            TopicInfo(image_reid_topic),
            TopicInfo(detection_reg_topic),
            TopicInfo(detection_reid_topic),
            TopicInfo(frameinfo_reg_topic),
            TopicInfo(frameinfo_reid_topic),
            TopicInfo(reid_topic, drop=False),
        ],
        latency_ms=500,
        commit_interval_sec=None,
        group_by_time=True
    )

    registrations: Dict[str, int] = {}
    i = 0
    inner_id = 0
    scaling = 1.0
    for msgs in consumer.getMessages():
        for time, v in message_list_to_frame_structure(msgs).items():
            message = v.get(args.prefix, {})
            reid_records = message[REID_TOPIC_ID].get("reid", {})

            for topic_key, topic_message in filter(lambda t: t[0] != REID_TOPIC_ID, message.items()):
                img = topic_message.get("image", {})
                if not isinstance(img, np.ndarray):
                    continue

                head_detections = topic_message.get("head_detection", {})
                # Set the image scale
                shape_orig = head_detections.pop("image", {})
                if shape_orig:
                    scaling = img.shape[1] / shape_orig["frame_info"]["columns"]

                # Processing the detections
                for detection_key, detection_record in head_detections.items():
                    object_detection_record = detection_record["bounding_box"]
                    color = COLOR_GREY
                    key_to_display = ""
                    
                    # Reidentification received
                    if topic_key == REID_CAMERA_ID:
                        reid_records_for_det = reid_records.get(detection_key, ())
                        for reid_record in filter(lambda r: "reid_event" in r, reid_records_for_det):
                            # We only use the first identified face now
                            reid_key = reid_record["reid_event"]["match_list"][0]["id"]["first_detection_key"]
                            registered_id = registrations.get(reid_key, None)
                            if registered_id:
                                color = COLOR_ORANGE
                                detection_time = reid_record["reid_event"]["match_list"][0]["id"]["first_detection_time"]
                                dwell_time = time - int(detection_time)
                                key_to_display = f"id: {registered_id}; dwell time: {dwell_time}ms"
                            else:
                                inner_id += 1
                                registrations[reid_key] = inner_id

                    # draw text above bounding box
                    img = draw_nice_text(
                        canvas=img,
                        text=key_to_display,
                        bounding_box=object_detection_record["bounding_box"],
                        color=color,
                        scale=scaling
                    )

                    # draw bounding_box
                    img = draw_nice_bounding_box(
                        canvas=img,
                        bounding_box=object_detection_record["bounding_box"],
                        color=color,
                        scaling=scaling
                    )

                # draw ultinous logo
                img = draw_overlay(
                    canvas=img,
                    overlay=overlay,
                    position=Position.BOTTOM_RIGHT,
                    scale=scaling
                )

                # produce output topic
                if args.output:
                    out_topic = output_reg_topic_name if topic_key == REG_CAMERA_ID else output_reid_topic_name
                    producer.produce(out_topic, value=encode_image_to_message(img), timestamp=time)
                    producer.poll(0)
                    if i % 100 == 0:
                        producer.flush()
                    i += 1

                # display #
                if args.display:
                    cv2.imshow(TITLE_REG if topic_key == REG_CAMERA_ID else TITLE_REID, img)

        k = cv2.waitKey(33)
        if k == 113:  # The 'q' key to stop
            break
        elif k == -1:  # normally -1 returned,so don't print it
            continue
        else:
            print(f"Press 'q' key for EXIT!")


if __name__ == "__main__":
    main()
