import argparse
import numpy as np
from argparse import RawTextHelpFormatter
from confluent_kafka import Consumer, TopicPartition
import cv2

from utils.uvap.uvap import decode_image_message


def main():
    # parse and check command line args
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Play and optionaly dumps video from a jpeg topic (a topic that ends with Image.jpg)."""
        , formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("topic", help="The name of topic (*.Image.jpg).", type=str)
    parser.add_argument('-f', "--full_screen", action='store_true')
    parser.add_argument('-d', "--dump", help="if set images are stored in jpg files", action='store_true')
    parser.add_argument('-o', "--offset", type=int, default=-1)
    args = parser.parse_args()
    if not args.topic.endswith(".Image.jpg"):
        raise argparse.ArgumentTypeError('The topic must be a jpeg image topic (should end with .Image.jpg)')

    # handle full screen
    window_name = args.topic
    if args.full_screen:
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # calc start time and create consumer
    c = Consumer({'bootstrap.servers': args.broker, 'group.id': 'display', 'auto.offset.reset': 'latest'})
    c.assign([TopicPartition(topic=args.topic, partition=0, offset=args.offset)])

    # read frames and show (or dump) them
    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        time = msg.timestamp()[1]
        img = decode_image_message(msg)
        if type(img) == np.ndarray:
            if args.dump:
                cv2.imwrite(args.topic + "_" + str(time) + ".jpg", img)
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
