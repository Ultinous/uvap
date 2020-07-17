import numpy as np
import argparse
import cv2
import time
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.kafka.time_ordered_generator_with_timeout import BeginFlag, EndFlag
from utils.uvap.graphics import draw_overlay, Position, draw_head_pose, draw_simple_text
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message
from utils.generator.heartbeat import HeartBeat


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays video from a jpeg topic, and visualize the head pose records with 3 diff color lines.
           [see: The yaw, pitch, and roll angles in the human head motion]
           Displays ('-d') or stores ('-o') the result of this demo in the kafka topic.
           
           Required topics:
           - <prefix>.cam.0.original.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.0.poses.HeadPose3DRecord.json
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
    pose_topic = f"{args.prefix}.cam.0.poses.HeadPose3DRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.head_pose.Image.jpg"
    frameinfo_topic = f"{args.prefix}.cam.0.frameinfo.FrameInfoRecord.json"

    # handle full screen
    window_name = "DEMO: Head pose"
    if args.full_screen:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Write notification if no message is received for this long
    notification_delay_sec = 10

    # read message, draw and display them
    consumer = TimeOrderedGeneratorWithTimeout(
        args.broker,
        "detection",
        [
            TopicInfo(image_topic),
            TopicInfo(detection_topic),
            TopicInfo(pose_topic),
            TopicInfo(frameinfo_topic),
        ],
        100,
        None,
        True,
        begin_flag=begin_flag,
        end_flag=end_flag,
        heartbeat_interval_ms=heartbeat_interval_ms
    )
    i = 0
    scaling = 1.0
    img_dimensions = (768, 1024)
    last_image_ts = None
    for msgs in consumer.getMessages():
        if not isinstance(msgs, HeartBeat):
            for ts, v in message_list_to_frame_structure(msgs).items():
                img = v[args.prefix]["0"]["image"]
                if type(img) != np.ndarray:
                    continue
                last_image_ts = int(time.time())

                # Set the image scale
                img_dimensions=(img.shape[0], img.shape[1])
                shape_orig = v[args.prefix]["0"]["head_detection"].pop("image", {})
                if shape_orig:
                    scaling = img.shape[1] / shape_orig["frame_info"]["columns"]

                # draw bounding_box
                for head_detection in v[args.prefix]["0"]["head_detection"]:
                    object_detection_record = v[args.prefix]["0"]["head_detection"][head_detection]["bounding_box"]
                    if object_detection_record["type"] != "PERSON_HEAD":
                        continue
                    pose_record = v[args.prefix]["0"]["head_detection"][head_detection]["head_pose"]
                    if "pose" in pose_record:
                        img = draw_head_pose(
                            canvas=img,
                            pose=pose_record["pose"],
                            bounding_box=object_detection_record["bounding_box"],
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
