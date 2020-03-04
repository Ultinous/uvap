import argparse
import numpy as np
import cv2
import time
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.kafka.time_ordered_generator_with_timeout import BeginFlag, EndFlag
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message

current_milli_time = lambda: int(round(time.time() * 1000))


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays a video from a jpeg topic and visualizes the head detection with an orange bounding box around a head.
           Displays ('-d') or stores ('-o') the result of this demo in the kafka topic.
           
           Required topics:
           - <prefix>.cam.0.original.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
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
    end_flag = None
    if args.video_file:
        begin_flag = BeginFlag.BEGINNING
        end_flag = EndFlag.END_OF_PARTITION

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    image_topic = f"{args.prefix}.cam.0.original.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    frameinfo_topic = f"{args.prefix}.cam.0.frameinfo.FrameInfoRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.head_detection.Image.jpg"

    # handle full screen
    window_name = "DEMO: Head detection"
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
            TopicInfo(frameinfo_topic)
        ],
        100,
        None,
        True,
        begin_flag=begin_flag,
        end_flag=end_flag
    )
    i = 0
    scaling = 1.0
    for msgs in consumer.getMessages():
        for time, v in message_list_to_frame_structure(msgs).items():
            img = v[args.prefix]["0"]["image"]
            if type(img) == np.ndarray:

                # Set the image scale
                shape_orig = v[args.prefix]["0"]["head_detection"].pop("image", {})
                if shape_orig:
                    scaling = img.shape[1] / shape_orig["frame_info"]["columns"]

                # draw bounding_box
                for head_detection in v[args.prefix]["0"]["head_detection"]:
                    object_detection_record = v[args.prefix]["0"]["head_detection"][head_detection]["bounding_box"]
                    if object_detection_record["type"] == "PERSON_HEAD":
                        img = draw_nice_bounding_box(
                            canvas=img,
                            bounding_box=object_detection_record["bounding_box"],
                            color=(10, 95, 255),
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
                    producer.produce(output_topic_name, value=encode_image_to_message(img), timestamp=time)
                    producer.poll(0)
                    if i % 100 == 0:
                        producer.flush()
                        i = 0
                    i += 1

                # display
                if args.display:
                    cv2.imshow(window_name, img)
        k = cv2.waitKey(33)
        if k == 113:  # The 'q' key to stop
            if args.video_file:
                exit(130)
            else:
                break
        elif k == -1:  # normally -1 returned,so don't print it
            continue
        else:
            print(f"Press 'q' key for EXIT!")


if __name__ == "__main__":
    main()
