import argparse
import numpy as np
import cv2

from utils.uvap.graphics import draw_overlay, Position, draw_nice_bounding_box
from utils.kafka.time_ordered_generator_with_timeout import TopicInfo, TimeOrderedGeneratorWithTimeout
from utils.uvap.uvap import message_list_to_frame_structure


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Play video from a jpeg topic
           and visualize the head detection with an orange bounding box around a head].
           
           Required topics:
           - <prefix>.cam.0.lowres.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           """
        , formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("prefix", help="Prefix of topics (base|skeleton).", type=str)
    parser.add_argument('-f', "--full_screen", action='store_true')
    args = parser.parse_args()

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    image_topic = args.prefix + ".cam.0.lowres.Image.jpg"
    detection_topic = args.prefix + ".cam.0.dets.ObjectDetectionRecord.json"

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
            TopicInfo(detection_topic)
        ],
        100,
        None,
        True
    )

    for msgs in consumer.getMessage():
        for time, v in message_list_to_frame_structure(msgs).items():
            img = v[args.prefix]["0"]["image"]
            if type(img) == np.ndarray:
                # draw bounding_box
                for head_detection in v[args.prefix]["0"]["head_detection"]:
                    object_detection_record = v[args.prefix]["0"]["head_detection"][head_detection]["bounding_box"]
                    if object_detection_record["type"] == "PERSON_HEAD":
                        img = draw_nice_bounding_box(img, object_detection_record["bounding_box"], (10, 95, 255))

                # draw ultinous logo
                img = draw_overlay(img, overlay, Position.BOTTOM_RIGHT)

                # display
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
