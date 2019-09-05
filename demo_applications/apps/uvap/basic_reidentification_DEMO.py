import argparse
import cv2
import numpy as np
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position, draw_nice_text
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message


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
    parser.add_argument('-o', '--output', help='write output image into kafka topic', action='store_true')
    args = parser.parse_args()

    if not args.display and not args.output:
        parser.error("Missing argument: -d (display output) or -o (write output to kafka) is needed")

    if args.output:
        producer = Producer({'bootstrap.servers': args.broker})

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    image_topic = f"{args.prefix}.cam.0.original.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    reid_topic = f"{args.prefix}.cam.{REID_TOPIC_ID}.reids.ReidRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.reids.Image.jpg"

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
            TopicInfo(reid_topic, drop=False),
        ],
        500,
        None,
        True
    )

    i = 0
    stored_ids = {}
    for msgs in consumer.getMessages():
        for time, v in message_list_to_frame_structure(msgs).items():

            reid_records = v[args.prefix][REID_TOPIC_ID].get("reid", {})
            img = v[args.prefix]["0"]["image"]
            if type(img) == np.ndarray:

                for key in v[args.prefix]["0"]["head_detection"]:
                    object_detection_record = v[args.prefix]["0"]["head_detection"][key]["bounding_box"]

                    color = COLOR_GREY
                    reid_record = reid_records.get(key)
                    if reid_record:
                        color = COLOR_ORANGE
                        reid_key = reid_record["reg_refs"][0]["subject"]["key"]

                        key_to_display = stored_ids.get(reid_key, None)
                        if key_to_display is None:
                            key_to_display = len(stored_ids) + 1
                            stored_ids[reid_key] = key_to_display

                        # user id
                        img = draw_nice_text(
                            canvas=img,
                            text=str(key_to_display),
                            bounding_box=object_detection_record["bounding_box"],
                            color=color
                        )

                    # draw bounding_box
                    img = draw_nice_bounding_box(
                        canvas=img,
                        bounding_box=object_detection_record["bounding_box"],
                        color=color
                    )

                # draw ultinous logo
                img = draw_overlay(canvas=img, overlay=overlay, position=Position.BOTTOM_RIGHT)

                # produce output topic
                if args.output:
                    producer.produce(output_topic_name, value=encode_image_to_message(img), timestamp=time)
                    producer.poll(0)
                    if i % 100 == 0:
                        producer.flush()
                    i += 1

                # display
                if args.display:
                    cv2.imshow(window_name, img)
        k = cv2.waitKey(33)
        if k == 113:  # The 'q' key to stop
            break
        elif k == -1:  # normally -1 returned,so don't print it
            continue
        else:
            print(f"Press 'q' key for EXIT!")


if __name__ == "__main__":
    main()
