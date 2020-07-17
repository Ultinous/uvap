import argparse
import cv2
import numpy as np
import time
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.kafka.time_ordered_generator_with_timeout import BeginFlag, EndFlag
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position, draw_nice_text, draw_simple_text
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message
from utils.generator.heartbeat import HeartBeat

COLOR_ORANGE = (10, 95, 255)
COLOR_GREY = (97, 97, 97)
REID_TOPIC_ID = "99"
TITLE = "DEMO: Reidentification"


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays a video from a jpeg topic,
           visualizes head detection with an orage bounding box around a head 
           and writes the IDs given by reid MS above the heads.
           Displays ('-d') or stores ('-o') the result of this demo in the kafka topic.
           Required topics:
           - <prefix>.cam.0.original.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.99.reids.ReidRecord.json
           """
        , formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("prefix", help="Prefix of topics (base|skeleton).", type=str)
    parser.add_argument('-f', "--full_screen", action='store_true')
    parser.add_argument('-d', "--display", action='store_true')
    parser.add_argument('-v', "--video_file", action='store_true')
    parser.add_argument('-o', '--output', help='write output image into kafka topic', action='store_true')
    args = parser.parse_args()

    if not args.display and not args.output:
        parser.error("Missing argument: -d (display output) or -o (write output to kafka) is needed")

    if args.output:
        producer = Producer({'bootstrap.servers': args.broker})

    begin_flag = None
    end_flag = EndFlag.NEVER
    if args.video_file:
        begin_flag = BeginFlag.BEGINNING
        end_flag = EndFlag.END_OF_PARTITION
    heartbeat_interval_ms = 1000

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    image_topic = f"{args.prefix}.cam.0.original.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    reid_topic = f"{args.prefix}.cam.{REID_TOPIC_ID}.reids.ReidRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.reidentification.Image.jpg"
    frameinfo_topic = f"{args.prefix}.cam.0.frameinfo.FrameInfoRecord.json"

    # Write notification if no message is received for this long
    notification_delay_sec = 10

    # handle full screen
    window_name = TITLE
    if args.full_screen:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # read message, draw and display them
    consumer = TimeOrderedGeneratorWithTimeout(
        args.broker,
        "detection",
        [
            TopicInfo(image_topic),
            TopicInfo(detection_topic),
            TopicInfo(reid_topic),
            TopicInfo(frameinfo_topic)
        ],
        500,
        None,
        True,
        begin_flag=begin_flag,
        end_flag=end_flag,
        heartbeat_interval_ms=heartbeat_interval_ms
    )

    i = 0
    stored_ids = {}
    scaling = 1.0
    img_dimensions = (768, 1024)
    last_image_ts = None
    for msgs in consumer.getMessages():
        if not isinstance(msgs, HeartBeat):
            for ts, v in message_list_to_frame_structure(msgs).items():
                message = v.get(args.prefix, {})
                img = message["0"].get("image", {})
                if type(img) != np.ndarray:
                    continue
                last_image_ts = int(time.time())
                reid_records = message[REID_TOPIC_ID].get("reid", {})
                head_detections = message["0"].get("head_detection", {})

                # Set the image scale
                img_dimensions=(img.shape[0], img.shape[1])
                shape_orig = head_detections.pop("image", {})
                if shape_orig:
                    scaling = img.shape[1] / shape_orig["frame_info"]["columns"]

                # Processing detections
                for detection_key, detection_record in head_detections.items():
                    object_detection_record = detection_record["bounding_box"]

                    color = COLOR_GREY
                    reid_records_for_det = reid_records.get(detection_key, ())
                    for reid_record in filter(lambda r: "reid_event" in r, reid_records_for_det):
                        color = COLOR_ORANGE
                        reid_key = reid_record["reid_event"]["match_list"][0]["id"]["first_detection_key"]
                        key_to_display = stored_ids.get(reid_key, None)
                        if key_to_display is None:
                            key_to_display = len(stored_ids) + 1
                            stored_ids[reid_key] = key_to_display

                        # user id
                        img = draw_nice_text(
                            canvas=img,
                            text=str(key_to_display),
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
                    producer.produce(output_topic_name, value=encode_image_to_message(img), timestamp=ts)
                    producer.poll(0)
                    if i % 100 == 0:
                        producer.flush()
                    i += 1

                # display
                if args.display:
                    cv2.imshow(window_name, img)

        # Write notification until the first message is received
        # (output topic is not updated to ensure kafka timestamp consistency)
        elif args.display and (last_image_ts is None or last_image_ts + notification_delay_sec < int(time.time())):
            img = np.zeros((*img_dimensions, 3), np.uint8)
            text = "Waiting for input Kafka topics to be populated. \n" \
                "Please make sure that MGR and other necessary services are running."
            img = draw_simple_text(canvas=img, text=text, color=(10, 95, 255))
            cv2.imshow(window_name, img)

        k = cv2.waitKey(33)
        if k == 113:  # The 'q' key to stop
            if args.video_file:
                exit(130)
            break
        elif k == -1:  # normally -1 returned,so don't print it
            continue
        else:
            print(f"Press 'q' key for EXIT!")


if __name__ == "__main__":
    main()
