import argparse
import sys
import numpy as np
from argparse import RawTextHelpFormatter
import cv2
from pathlib import Path
from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo
from utils.kafka.time_ordered_generator_with_timeout import BeginFlag, EndFlag
from utils.uvap.uvap import decode_image_message
from utils.generator.heartbeat import HeartBeat


def main():
    # parse and check command line args
    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           Dump and optionally plays video from a jpeg topic (a topic that ends with Image.jpg)."""
        , formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("topic", help="The name of topic (*.Image.jpg).", type=str)
    parser.add_argument('-o', "--offset", help="The offset of image topic", type=int, default=0)
    parser.add_argument('-c', "--count", help="The number of frames", type=int, default=-1)
    parser.add_argument('-e', "--exit", help="Exit at the end of the topic", action='store_true')
    parser.add_argument('-n', "--name_of_video", help="The name (and optionally path) of the output video", type=str, default='../videos')
    parser.add_argument('-fps', "--frames_per_second", help="Frame per second of the output video.", type=int, default=1)
    parser.add_argument('-width', "--width_of_output", help="Width of the output video.", type=int, default=1024)
    parser.add_argument('-height', "--height_of_output", help="Height of the output video.", type=int, default=768)
    parser.add_argument('-d', "--display", help="Display video", action='store_true')
    args = parser.parse_args()
    if not args.topic.endswith(".Image.jpg"):
        raise argparse.ArgumentTypeError('The topic must be a jpeg image topic (should end with .Image.jpg)')

    output_video_name = Path(args.name_of_video, strict=True).resolve()
    if not output_video_name.suffix:
        if not output_video_name.exists():
            sys.exit('ERROR: {} directory does not exist.'.format(output_video_name))
        output_video_name = output_video_name.joinpath(f'{args.topic}.avi')

    consumer = TimeOrderedGeneratorWithTimeout(
        args.broker,
        "write_video.py",
        [TopicInfo(args.topic)],
        100,
        None,
        True,
        begin_flag=BeginFlag.OFFSET,
        end_flag=(EndFlag.END_OF_PARTITION if args.exit else EndFlag.NEVER),
        heartbeat_interval_ms=1000,
        begin_offset=args.offset
    )

    out = cv2.VideoWriter(
        str(output_video_name),
        cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
        int(args.frames_per_second),
        (args.width_of_output, args.height_of_output)
    )

    i = 0
    img = np.zeros((args.height_of_output, args.width_of_output, 3), np.uint8)
    for msgs in consumer.getMessages():
        if not isinstance(msgs, HeartBeat):
            for message in msgs:
                img = decode_image_message(message)
                if type(img) != np.ndarray:
                    continue
                out.write(img)
            if 0 < args.count < i:
                consumer.stopGenerator()
            i += 1
            if args.display:
                cv2.imshow(args.topic, img)

        k = cv2.waitKey(33)
        if k == 113:  # The 'q' key to stop
            consumer.stopGenerator()
        elif k == -1:
            continue
        else:
            print(f"Press 'q' key for EXIT!")

    out.release()
    print('Done: {}'.format(output_video_name))
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
