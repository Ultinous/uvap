import json
from typing import List

import cv2
import numpy as np
from confluent_kafka import Message


class NoKeyErrorDict(dict):
    """
    Dictionary with error handling during KeyError. With this dictionary we can create nested structures more simply.
    """

    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

    def asdict(self):
        for k, v in self.items():
            if isinstance(v, type(self)):
                self[k] = v.asdict()
        return dict(self)


def decode_standard_message(msg: Message) -> dict:
    return json.loads(msg.value().decode('utf-8'))


def decode_image_message(msg: Message) -> np.array:
    img_mat = np.fromstring(msg.value(), dtype=np.uint8)
    return cv2.imdecode(img_mat, -1)


def encode_image_to_message(img: np.array):
    _, encoded = cv2.imencode('.jpg', img)
    return encoded.tobytes()


def _get_message_type(message_topic):
    if '.jpg' in message_topic:
        return 'image'
    elif '.ObjectDetectionRecord' in message_topic:
        return 'bounding_box'
    elif '.HeadPose3DRecord' in message_topic:
        return 'head_pose'
    elif '.skeletons' in message_topic:
        return 'skeleton'
    elif '.AgeRecord' in message_topic:
        return 'age'
    elif '.GenderRecord' in message_topic:
        return 'gender'
    elif '.TrackChangeRecord' in message_topic:
        return 'track'
    elif '.PassDetectionRecord' in message_topic:
        return "passdet"
    elif '.ReidRecord' in message_topic:
        return 'reid'
    return 'unknown'


def _get_current_stream(message_topic):
    parts = message_topic.split('.')
    return parts[0]


def _get_current_cam(message_topic):
    parts = message_topic.split('.')
    for idx, part in enumerate(parts):
        if 'cam' in part:
            return parts[idx + 1]
    else:
        return 'default_cam'


def message_list_to_frame_structure(messages: List[Message]) -> dict:
    """
    Grouping list of messages into a dictionary. Bounding boxes, age and gender infos, head poses are grouped
    under "head_detection" key. The points of skeletons are grouped under "skeleton" key. Skeletons and head detections
    are grouped under the associated camera, which is represented by the camera id. The structure allows us to use
    multiple cameras from multiple streams so the cameras are merging under the stream key. To use re-identification
    across multiple streams and cameras, streams and re-identification is grouped together with their common timestamp.
    :param messages: list of kafka messages
    :return: dictionary with the grouped values
    """
    frame_dict = NoKeyErrorDict()
    for message in messages:
        ts = message.timestamp()[1]
        topic_name = message.topic()
        message_key = message.key()

        stream = _get_current_stream(topic_name)
        cam = _get_current_cam(topic_name)
        type = _get_message_type(topic_name)
        detection = message_key.decode('utf-8') if message_key is not None else 'image'
        value = decode_image_message(message) if '.jpg' in message.topic() else decode_standard_message(message)

        if type == 'image':
            frame_dict[ts][stream][cam][type] = value
        elif not value.get("end_of_frame", False):
            if type in ('skeleton', 'track', 'passdet', 'reid'):
                frame_dict[ts][stream][cam][type][detection] = value
            else:
                frame_dict[ts][stream][cam]['head_detection'][detection][type] = value
    return frame_dict
