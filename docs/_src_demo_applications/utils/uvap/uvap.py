import cv2
import json
import numpy as np
import os
import platform
from pathlib import Path
from confluent_kafka import Message
from typing import List
from turbojpeg import TurboJPEG

actual_platform = platform.system()
try:
    if actual_platform == 'Windows' and 'PythonTurboJpeg' in os.environ :
        print("Looking for turbojpeg.dll location defined in %PythonTurboJpeg% environmental variable: \n",
              os.environ['PythonTurboJpeg'] , "\n")
        if not Path(os.environ['PythonTurboJpeg']).exists():
            raise FileNotFoundError(os.environ['PythonTurboJpeg'])
        turbo = TurboJPEG(os.environ['PythonTurboJpeg'])
    else:
        turbo = TurboJPEG()
except RuntimeError as e:
    if e.args[0].find("turbojpeg"):
        print("libjpeg-turbo library is not found. Please check if it is installed on the system. \n"
              "Installable can be downloaded from: https://github.com/libjpeg-turbo/libjpeg-turbo/releases \n"
              "or refer to the installation steps described at https://pypi.org/project/PyTurboJPEG \n"
              "(Because of current limitation of PyTurboJpeg, please use the vc version.)")
        if actual_platform == 'Windows':
            print("If the library is already installed, please ensure that the installation location is directly under the C: drive, e.g.:\n"
                  "c:\\libjpeg-turbo64\\bin\\turbojpeg.dll \n"
                  "or set the actual path of the .dll file in %PythonTurboJpeg% environmental variable\n")
        elif actual_platform == 'Linux':
            print("If the library is already installed, please ensure that it can be found at:\n"
                  "/usr/lib/x86_64-linux-gnu/libturbojpeg.so.0 \n"
                  "or /opt/libjpeg-turbo/lib64/libturbojpeg.so \n"
                  "Create a symbolic link or add the path to the LD_LIBRARY_PATH if the .so file is located elsewhere. \n")
        else:
            print("If the library is already installed, please ensure that it can be found at: \n"
                  "/usr/local/opt/jpeg-turbo/lib/libturbojpeg.dylib \n")
        raise



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

    # todo make repr method pls

def decode_standard_message(msg: Message) -> dict:
    return json.loads(msg.value().decode('utf-8'))


def decode_image_message(msg: Message) -> np.array:
    img_mat = np.fromstring(msg.value(), dtype=np.uint8)
    return turbo.decode(img_mat)


def encode_image_to_message(img: np.array):
    return turbo.encode(img)


def _get_message_type(message_topic) -> str:
    if '.jpg' in message_topic:
        return 'image'
    elif '.ObjectDetectionRecord' in message_topic:
        if '.filtered_dets.' in message_topic:
            return 'filtered_bounding_box'
        return 'bounding_box'
    elif '.HeadPose3DRecord' in message_topic:
        return 'head_pose'
    elif '.skeletons' in message_topic:
        return 'skeleton'
    elif '.AgeRecord' in message_topic:
        return 'age'
    elif '.GenderRecord' in message_topic:
        return 'gender'
    elif '.FaceMaskRecord' in message_topic:
        return 'face_mask'
    elif '.TrackChangeRecord' in message_topic:
        return 'track'
    elif '.PassDetectionRecord' in message_topic:
        return "passdet"
    elif '.ReidRecord' in message_topic:
        return 'reid'
    elif '.FrameInfoRecord' in message_topic:
        return 'frame_info'
    return 'unknown'


def _get_current_stream(message_topic: str) -> str:
    parts = message_topic.split('.')
    return parts[0]


def _get_current_cam(message_topic: str) -> str:
    parts = message_topic.split('.')
    for idx, part in enumerate(parts):
        if 'cam' in part:
            return parts[idx + 1]
    else:
        return 'default_cam'


def message_list_to_frame_structure(messages: List[Message]) -> dict:
    """
    Grouping list of messages into a dictionary. Bounding boxes, age and gender infos, face masks, head poses are grouped
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
            if type in ('skeleton', 'track', 'passdet'):
                frame_dict[ts][stream][cam][type][detection] = value
            elif type == 'reid':
                if not len(frame_dict[ts][stream][cam][type][detection]):
                    frame_dict[ts][stream][cam][type][detection] = [value]
                else:
                    frame_dict[ts][stream][cam][type][detection].append(value)
            elif type == 'filtered_bounding_box':
                frame_dict[ts][stream][cam]['filtered_head_detection'][detection][type] = value
            else:
                frame_dict[ts][stream][cam]['head_detection'][detection][type] = value
    return frame_dict
