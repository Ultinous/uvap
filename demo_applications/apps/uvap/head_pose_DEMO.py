import numpy as np
import argparse
import cv2

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.uvap.graphics import draw_overlay, Position, draw_head_pose
from utils.uvap.uvap import message_list_to_frame_structure


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Play video from a jpeg topic
           and visualize the head pose with 3 diff color lines 
           [see: The yaw, pitch, and roll angles in the human head motion]
           
           Required topics:
           - <prefix>.cam.0.lowres.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.0.poses.HeadPose3DRecord.json
           """
        , formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("prefix", help="Prefix of topics (base|skeleton).", type=str)
    parser.add_argument('-f', "--full_screen", action='store_true')
    args = parser.parse_args()

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    image_topic = f"{args.prefix}.cam.0.lowres.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    pose_topic = f"{args.prefix}.cam.0.poses.HeadPose3DRecord.json"

    # handle full screen
    window_name = "DEMO: Head pose"
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
            TopicInfo(pose_topic),
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
                        pose_record = v[args.prefix]["0"]["head_detection"][head_detection]["head_pose"]
                        if "pose" in pose_record:
                            img = draw_head_pose(
                                img,
                                pose_record["pose"],
                                object_detection_record["bounding_box"],
                            )

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
