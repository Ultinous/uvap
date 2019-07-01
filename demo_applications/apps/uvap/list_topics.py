from confluent_kafka import Consumer, admin
from typing import List


def get_cluster_metadata(broker: str, timeout: float) -> admin.ClusterMetadata:
    consumer = Consumer({'bootstrap.servers': broker, 'group.id': 'groupid'})
    ret = consumer.list_topics(timeout=timeout)
    consumer.close()
    return ret


def get_topic_names(metadata: admin.ClusterMetadata) -> List[str]:
    return list(metadata.topics.keys())


if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(
        epilog=
        """Description:
           List topics from Kafka."""
        , formatter_class=RawTextHelpFormatter
    )
    parser.add_argument("broker", help="The name of the kafka broker.", type=str)
    parser.add_argument('-t', "--timeout", help="Timeout", type=float, default=10.)
    args = parser.parse_args()

    print(*get_topic_names(get_cluster_metadata(args.broker, args.timeout)), sep='\n')
