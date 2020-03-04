import argparse
from json import loads
from pathlib import Path
from typing import List

import cv2
import numpy as np
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import BeginFlag, EndFlag # FIXME check_imports.sh cannot handle long lines
from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.uvap.graphics import draw_nice_bounding_box, draw_nice_text, draw_polyline, draw_ultinous_logo
from utils.uvap.uvap import encode_image_to_message, message_list_to_frame_structure


COLOR_ORANGE = (10, 95, 255)
COLOR_GREY = (97, 97, 97)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)


def init_parser():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays a video from a jpeg topic and visualizes the head detection with
           - an orange bounding box when the detection passed the detection filter;
           - an grey bounding box when the detection not passed the detection filter;
           Displays ('-d') or stores ('-o') the result of this demo in the kafka topic.

           Required topics:
           - <prefix>.cam.0.original.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.0.filtered_dets.ObjectDetectionRecord.json
           """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("prefix", help="Prefix of topics (base|skeleton).", type=str)
    parser.add_argument("config", help="Path to service config.", type=str)
    parser.add_argument('-f', "--full_screen", action='store_true')
    parser.add_argument('-d', "--display", action='store_true')
    parser.add_argument('-v', "--video_file", action='store_true')
    parser.add_argument('-o', '--output', help='write output image into kafka topic', action='store_true')
    return parser


def parse_config_data(args, parser):
    config_file = Path(args.config)

    if not config_file.is_file():
        parser.error(f"{args.config} does not exist.")

    with open(config_file) as f:
        ms_config_json = loads(f.read())

    return ms_config_json["config_data"]


def parse_areas(config_data, config_data_key):
    ret = []
    if config_data_key in config_data.keys():
        for area in config_data[config_data_key]:
            ret.append([(vertex["x"], vertex["y"]) for vertex in area["vertices"]])
    return ret


def parse_detection_types(config_data):
    detection_types = []
    if "detection_types" in config_data.keys():
        detection_types = config_data["detection_types"]

    if "PERSON_FULL_BODY" in detection_types:
        print("PERSON_FULL_BODY detection type is not handled")
        if len(detection_types) == 1:
            exit(2)
        detection_types.remove("PERSON_FULL_BODY")
    return detection_types


def draw_bounding_box(object_detection_record, detection_types: List[str], img: np.array, scaling, color) -> np.array:
    if object_detection_record["type"] in detection_types:
        img = draw_nice_bounding_box(
            canvas=img,
            bounding_box=object_detection_record["bounding_box"],
            color=color,
            scaling=scaling
        )
        img = draw_nice_text(
            canvas=img,
            text=str(object_detection_record["detection_confidence"]),
            bounding_box=object_detection_record["bounding_box"],
            color=color,
            scale=scaling
        )
    return img


def draw_areas(areas, img: np.array, color) -> np.array:
    for area in areas:
        img = draw_polyline(
            canvas=img,
            points=area,
            color=color,
            is_closed=True
        )
    return img


def main():
    parser = init_parser()
    args = parser.parse_args()
    config_data = parse_config_data(
        args=args,
        parser=parser
    )
    positive_areas = parse_areas(config_data, "positive_areas")
    negative_areas = parse_areas(config_data, "negative_areas")
    detection_types = parse_detection_types(config_data)

    if not args.display and not args.output:
        parser.error("Missing argument: -d (display output) or -o (write output to kafka) is needed")

    if args.output:
        producer = Producer({'bootstrap.servers': args.broker})

    begin_flag = None
    end_flag = None
    if args.video_file:
        begin_flag = BeginFlag.BEGINNING
        end_flag = EndFlag.END_OF_PARTITION

    output_topic_name = f"{args.prefix}.cam.0.filtered_dets.Image.jpg"

    # handle full screen
    window_name = "DEMO: Filtered detection"
    if args.full_screen:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # read message, draw and display them
    consumer = TimeOrderedGeneratorWithTimeout(
        broker=args.broker,
        groupid="detection",
        topics_infos=[
            TopicInfo(f"{args.prefix}.cam.0.original.Image.jpg"),  # image_topic
            TopicInfo(f"{args.prefix}.cam.0.filtered_dets.ObjectDetectionRecord.json"),  # filtered_detection_topic
            TopicInfo(f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json")  # detection_topic
        ],
        latency_ms=100,
        group_by_time=True,
        begin_flag=begin_flag,
        end_flag=end_flag
    )
    i = 0
    scaling = 1.0
    for msgs in consumer.getMessages():
        for time, v in message_list_to_frame_structure(msgs).items():
            frame_info = v[args.prefix]["0"]
            img = frame_info["image"]
            if type(img) == np.ndarray:
                # Set the image scale
                shape_orig = frame_info["head_detection"].pop("image", {})
                if shape_orig:
                    scaling = img.shape[1] / shape_orig["frame_info"]["columns"]

                # draw bounding_box
                for head_detection in frame_info["head_detection"]:
                    img = draw_bounding_box(
                        object_detection_record=frame_info["head_detection"][head_detection]["bounding_box"],
                        detection_types=detection_types,
                        img=img,
                        scaling=scaling,
                        color=COLOR_GREY
                    )

                for head_detection in frame_info["filtered_head_detection"]:
                    img = draw_bounding_box(
                        object_detection_record=
                        frame_info["filtered_head_detection"][head_detection]["filtered_bounding_box"],
                        detection_types=detection_types,
                        img=img,
                        scaling=scaling,
                        color=COLOR_ORANGE
                    )

                draw_areas(areas=positive_areas, img=img, color=COLOR_GREEN)
                draw_areas(areas=negative_areas, img=img, color=COLOR_RED)

                draw_ultinous_logo(canvas=img, scale=scaling)

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
