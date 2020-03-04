import argparse
import os
import sys
import numpy as np
from argparse import RawTextHelpFormatter
from confluent_kafka import Consumer, TopicPartition
import cv2

from utils.uvap.uvap import message_list_to_frame_structure, decode_image_message


def main():
    # parse and check command line args
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Plays and optionaly dumps video from a jpeg topic (a topic that ends with Image.jpg)."""
        , formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("topic", help="The name of topic (*.Image.jpg).", type=str)
    parser.add_argument('-o', "--offset", help="The offset of image topic", type=int, default=0)
    parser.add_argument('-c', "--count", help="The number of frames", type=int, default=-1)
    parser.add_argument('-n', "--name_of_video", help="The name of the output video", type=str, default="")
    parser.add_argument('-fps', "--frames_per_second", help="Frame per second of the output video.", type=int, default=1)
    parser.add_argument('-width', "--width_of_output", help="Width of the output video.", type=int, default=1)
    parser.add_argument('-height', "--height_of_output", help="Height of the output video.", type=int, default=1)
    args = parser.parse_args()
    if not args.topic.endswith(".Image.jpg"):
        raise argparse.ArgumentTypeError('The topic must be a jpeg image topic (should end with .Image.jpg)')

    # calc start time and create consumer
    c = Consumer({'bootstrap.servers': args.broker, 'group.id': 'write_video.py', 'auto.offset.reset': 'latest'})
    c.assign([TopicPartition(topic=args.topic, partition=0, offset=args.offset)])

    if "" == args.name_of_video:
        output_video_name = f'{args.topic}.avi'
    else:
        output_video_name = args.name_of_video

    if not os.path.exists('../videos'):
        sys.exit(f'ERROR: "../videos" folder does not exist!')

    out = cv2.VideoWriter(
        f'../videos/{output_video_name}',
        cv2.VideoWriter_fourcc('D', 'I', 'V', 'X'),
        float(args.frames_per_second),
        (args.width_of_output, args.height_of_output)
    )
    i = 0
    while True:
        msg = c.poll(1.0)
        if msg is None:
            break
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        img = decode_image_message(msg)
        if type(img) == np.ndarray:
            out.write(img)
            if 0 < args.count < i:
                break
            i += 1

    out.release()
    print(f'Done: ../videos/{output_video_name}')
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
