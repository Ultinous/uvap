import argparse
from collections import defaultdict
from itertools import cycle
from typing import DefaultDict, Any

import cv2
import numpy as np
from confluent_kafka.cimpl import Producer

from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.uvap.graphics import draw_nice_bounding_box, draw_overlay, Position, TYPE_TO_COLOR
from utils.uvap.uvap import message_list_to_frame_structure, encode_image_to_message

colors = cycle(TYPE_TO_COLOR.values())


class Track:
    MAX_SIZE = 30

    def __init__(self, color: tuple) -> None:
        self.color = color
        self.points = []

    def add_point(self, point: tuple):
        self.points.append(point)
        if len(self.points) > Track.MAX_SIZE:
            self.points = self.points[-Track.MAX_SIZE:]


def main():
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays a video from a jpeg topic, visualizes the head detections and tracks.
           Displays the result on screen ('-d') or stores result in kafka ('-o').
           
           Required topics:
           - <prefix>.cam.0.lowres.Image.jpg
           - <prefix>.cam.0.dets.ObjectDetectionRecord.json
           - <prefix>.cam.0.tracks.TrackChangeRecord.json
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

    image_topic = f"{args.prefix}.cam.0.lowres.Image.jpg"
    detection_topic = f"{args.prefix}.cam.0.dets.ObjectDetectionRecord.json"
    track_topic = f"{args.prefix}.cam.0.tracks.TrackChangeRecord.json"
    output_topic_name = f"{args.prefix}.cam.0.tracks.Image.jpg"

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
            TopicInfo(track_topic, drop=False),
            TopicInfo(detection_topic)
        ],
        100,
        None,
        True
    )
    i = 0

    tracks: DefaultDict[Any, Track] = defaultdict(lambda: Track(next(colors)))

    for msgs in consumer.getMessage():
        for time, v in message_list_to_frame_structure(msgs).items():
            for track_key, track_val in v[args.prefix]["0"]["track"].items():
                if track_val["end_of_track"]:
                    if track_key in tracks:
                        del tracks[track_key]
                    continue
                point = track_val["point"]["x"], track_val["point"]["y"]
                tracks[track_key].add_point(point)
            img = v[args.prefix]["0"]["image"]
            if type(img) == np.ndarray:
                # draw bounding_box
                for head_detection in v[args.prefix]["0"]["head_detection"]:
                    object_detection_record = v[args.prefix]["0"]["head_detection"][head_detection]["bounding_box"]
                    if object_detection_record["type"] == "PERSON_HEAD":
                        img = draw_nice_bounding_box(img, object_detection_record["bounding_box"], (10, 95, 255))

                for t_key, t in tracks.items():
                    cv2.polylines(
                        img=img,
                        pts=[np.array(t.points, np.int32)],
                        isClosed=False,
                        color=t.color,
                        thickness=3
                    )

                # draw ultinous logo
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
