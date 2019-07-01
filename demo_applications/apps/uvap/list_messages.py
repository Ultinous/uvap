from utils.kafka.time_ordered_generator_with_timeout import TimeOrderedGeneratorWithTimeout, TopicInfo, BeginFlag
from utils.uvap.uvap import message_list_to_frame_structure


def get_messages(broker: str, topic: str):
    consumer = TimeOrderedGeneratorWithTimeout(
        broker,
        "list_messages",
        [
            TopicInfo(topic),
        ],
        100,
        None,
        True,
        begin_flag=BeginFlag.BEGINNING
    )
    ret = consumer.getMessage()
    return ret


if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           List messages from a topic."""
        , formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument("topic", help="The name of topic.", type=str)
    args = parser.parse_args()

    for msgs in get_messages(args.broker, args.topic):
        for time, v in message_list_to_frame_structure(msgs).items():
            print(time, v.asdict)
