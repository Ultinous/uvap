import argparse
import json
import time
from collections import defaultdict, deque
from itertools import cycle
from json import JSONDecodeError
from pathlib import Path
from typing import DefaultDict, Any, List, Tuple, Dict

import cv2
import javaproperties
import numpy as np
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.kafka.time_ordered_generator_with_timeout import BeginFlag, EndFlag
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position, draw_polyline, draw_simple_text
from utils.uvap.graphics import PASS_EVENT_CHARS, TYPE_TO_COLOR
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message
from utils.generator.heartbeat import HeartBeat

track_colors = cycle(TYPE_TO_COLOR.values())
pass_colors = cycle(((0, 0, 255), (255, 0, 0), (255, 0, 0)))


def parse_config_data(args, parser):
    config_file = Path(args.config)

    if not config_file.is_file():
        parser.error(f"{args.config} does not exist.")

    with open(config_file) as f:
        ms_config_json = json.loads(f.read())

    return ms_config_json["config_data"]


class ColoredPolyLine:
    MAX_SIZE = 30

    def __init__(self, color: tuple, points: List[Tuple[int, int]] = None) -> None:
        self.color = color
        self.points = points or []

    def add_point(self, point: tuple):
        self.points.append(point)
        if len(self.points) > ColoredPolyLine.MAX_SIZE:
            self.points = self.points[-ColoredPolyLine.MAX_SIZE:]

    def draw(self, img: np.array, scaling):
        draw_polyline(
            canvas=img,
            points=self.points,
            color=self.color,
            scaling=scaling
        )


class PassLine(ColoredPolyLine):

    def __init__(self, color: tuple, points: List[Tuple[int, int]] = None, max_queue_size=10) -> None:
        super().__init__(color, points)
        self.events = deque(maxlen=max_queue_size)

    def add_event(self, cross_dir: str):
        if cross_dir in PASS_EVENT_CHARS:
            self.events.appendleft(PASS_EVENT_CHARS[cross_dir])


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays a video from a jpeg topic, visualizes the head detections and tracks, and pass detections.
           Displays the result on screen ('-d') or stores result in kafka ('-o').
           
           Required topics:
           - <prefix>.cam.0.original.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.0.tracks.TrackChangeRecord.json
           - <prefix>.cam.0.passdet.PassDetectionRecord.json
           """
        , formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("prefix", help="Prefix of topics (base|skeleton).", type=str)
    parser.add_argument("config", help="Path to service config.", type=str)
    parser.add_argument('-f', "--full_screen", action='store_true')
    parser.add_argument('-d', "--display", action='store_true')
    parser.add_argument('-v', "--video_file", action='store_true')
    parser.add_argument('-o', '--output', help='write output image into kafka topic', action='store_true')
    args = parser.parse_args()

    passdet_config_json = parse_config_data(
        args=args,
        parser=parser
    )

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

    passlines: Dict[str, PassLine] = {
        pl["id"]: PassLine(
            next(pass_colors), [(int(p["x"]), int(p["y"])) for p in pl["poly"]])
        for pl in passdet_config_json["passLines"]
    }

    image_topic = f"{args.prefix}.cam.0.original.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    track_topic = f"{args.prefix}.cam.0.tracks.TrackChangeRecord.json"
    frameinfo_topic = f"{args.prefix}.cam.0.frameinfo.FrameInfoRecord.json"
    passdet_topic = f"{args.prefix}.cam.0.passdet.PassDetectionRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.passdet.Image.jpg"

    # Write notification if no message is received for this long
    notification_delay_sec = 10

    # handle full screen
    window_name = "DEMO: Pass detection"
    if args.full_screen:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # read message, draw and display them
    consumer = TimeOrderedGeneratorWithTimeout(
        args.broker,
        "detection",
        [
            TopicInfo(image_topic),
            TopicInfo(track_topic, drop=False),
            TopicInfo(passdet_topic, drop=False),
            TopicInfo(detection_topic),
            TopicInfo(frameinfo_topic)
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
    tracks: DefaultDict[Any, ColoredPolyLine] = defaultdict(lambda: ColoredPolyLine(next(track_colors)))

    for msgs in consumer.getMessages():
        if not isinstance(msgs, HeartBeat):
            for ts, v in message_list_to_frame_structure(msgs).items():
                for track_key, track_val in v[args.prefix]["0"]["track"].items():
                    if track_val["end_of_track"]:
                        if track_key in tracks:
                            del tracks[track_key]
                        continue
                    point = track_val["point"]["x"], track_val["point"]["y"]
                    tracks[track_key].add_point(point)

                for pass_det in v[args.prefix]["0"]["passdet"].values():
                    if pass_det["type"] == "HEARTBEAT":
                        continue
                    elif pass_det["type"] == "END_OF_TRACK":
                        continue
                    elif pass_det["type"] == "PASS_CANDIDATE":
                        pass_id = pass_det["pass_candidate"]["pass"]["pass_line_id"]
                        cross_dir = pass_det["pass_candidate"]["pass"]["cross_dir"]
                        if pass_id in passlines:
                            passlines[pass_id].add_event(cross_dir)
                    elif pass_det["type"] == "PASS_REALIZED":
                        continue

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
                    if object_detection_record["type"] == "PERSON_HEAD":
                        img = draw_nice_bounding_box(
                            canvas=img,
                            bounding_box=object_detection_record["bounding_box"],
                            color=(10, 95, 255),
                            scaling=scaling
                        )
                for t in tracks.values():
                    t.draw(img, scaling)
                for idx, l in enumerate(passlines.values()):
                    l.draw(img, scaling)
                    cv2.putText(img, "".join(l.events), (40, (idx + 1) * 50), cv2.FONT_HERSHEY_COMPLEX, 2, l.color, 5,
                                bottomLeftOrigin=True)
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
                        i = 0
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
