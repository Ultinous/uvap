import argparse
import json
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
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position, draw_polyline
from utils.uvap.graphics import PASS_EVENT_CHARS, TYPE_TO_COLOR
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message

track_colors = cycle(TYPE_TO_COLOR.values())
pass_colors = cycle(((0, 0, 255), (255, 0, 0), (255, 0, 0)))


class ColoredPolyLine:
    MAX_SIZE = 30

    def __init__(self, color: tuple, points: List[Tuple[int, int]] = None) -> None:
        self.color = color
        self.points = points or []

    def add_point(self, point: tuple):
        self.points.append(point)
        if len(self.points) > ColoredPolyLine.MAX_SIZE:
            self.points = self.points[-ColoredPolyLine.MAX_SIZE:]

    def draw(self, img: np.array):
        draw_polyline(img, self.points, self.color)


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
    parser.add_argument('-o', '--output', help='write output image into kafka topic', action='store_true')
    args = parser.parse_args()

    config_file = Path(args.config)

    if not config_file.is_file():
        parser.error(f"{args.config} does not exist.")

    if not args.display and not args.output:
        parser.error("Missing argument: -d (display output) or -o (write output to kafka) is needed")

    if args.output:
        producer = Producer({'bootstrap.servers': args.broker})

    with config_file.open() as f:
        try:
            passdet_config_json = json.loads(javaproperties.load(f)["ultinous.service.kafka.passdet.config"])
        except KeyError:
            parser.error("Missing property: ultinous.service.kafka.passdet.config")
        except JSONDecodeError as e:
            parser.error(f"Error parsing {e}")

    overlay = cv2.imread('resources/powered_by_white.png', cv2.IMREAD_UNCHANGED)

    passlines: Dict[str, PassLine] = {
        pl["id"]: PassLine(
            next(pass_colors), [(int(p["x"]), int(p["y"])) for p in pl["poly"]])
        for pl in passdet_config_json["passLines"]
    }

    image_topic = f"{args.prefix}.cam.0.original.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    track_topic = f"{args.prefix}.cam.0.tracks.TrackChangeRecord.json"
    passdet_topic = f"{args.prefix}.cam.0.passdet.PassDetectionRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.passdet.Image.jpg"

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
            TopicInfo(detection_topic)
        ],
        100,
        None,
        True
    )
    i = 0

    tracks: DefaultDict[Any, ColoredPolyLine] = defaultdict(lambda: ColoredPolyLine(next(track_colors)))

    for msgs in consumer.getMessages():
        for time, v in message_list_to_frame_structure(msgs).items():
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
            if type(img) == np.ndarray:
                # draw bounding_box
                for head_detection in v[args.prefix]["0"]["head_detection"]:
                    object_detection_record = v[args.prefix]["0"]["head_detection"][head_detection]["bounding_box"]
                    if object_detection_record["type"] == "PERSON_HEAD":
                        img = draw_nice_bounding_box(img, object_detection_record["bounding_box"], (10, 95, 255))

                for t in tracks.values():
                    t.draw(img)

                for idx, l in enumerate(passlines.values()):
                    l.draw(img)
                    cv2.putText(img, "".join(l.events), (40, (idx + 1) * 50), cv2.FONT_HERSHEY_COMPLEX, 2, l.color, 5,
                                bottomLeftOrigin=True)
                img = draw_overlay(img, overlay, Position.BOTTOM_RIGHT)

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
            break
        elif k == -1:  # normally -1 returned,so don't print it
            continue
        else:
            print(f"Press 'q' key for EXIT!")


if __name__ == "__main__":
    main()
