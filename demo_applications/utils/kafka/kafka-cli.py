#!/usr/bin/env python3
# coding=utf-8

import json
import sys
from json import JSONDecodeError
from typing import Optional, Any, Union

from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from kafka import KafkaConsumer, KafkaProducer

topic = 'mytopic'


def print_usage() -> None:
    print(f"Usage:\n  {sys.argv[0]} produce[-high] [msg]\n  {sys.argv[0]} consume[-high]")


def json_serializer(msg: Optional[Any]) -> Optional[bytes]:
    if msg is None:
        return None
    return json.dumps(msg).encode('utf8')


def json_deserializer(msg: Union[bytes, str, None]) -> Union[Any, JSONDecodeError, None]:
    if msg is None:
        return None
    try:
        if isinstance(msg, bytes):
            msg = msg.decode('utf8')
        return json.loads(msg)
    except JSONDecodeError as e:
        return e


def produce(msg: Optional[str]) -> None:
    producer = Producer({
        'bootstrap.servers': 'localhost',
    })
    producer.produce(topic, msg.encode("utf8") if msg is not None else None)
    producer.flush(4)


def produce_high(msg: Optional[str]) -> None:
    msg = json_deserializer(msg)  # convert back to obj
    producer = KafkaProducer(
        bootstrap_servers=['localhost'],
        value_serializer=json_serializer,
    )
    producer.send(topic, value=msg)
    producer.flush(4)


def consume() -> None:
    consumer = Consumer({
        'bootstrap.servers': 'localhost',
        'group.id': 'pyconsumer',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': 'false',
        'enable.partition.eof': 'true',
    })
    try:
        consumer.subscribe([topic])
        at_eof = False
        while True:
            msg = consumer.poll(0.2)
            if msg is None:
                continue
            if msg.error():
                if msg.error() == KafkaError._PARTITION_EOF:
                    at_eof = True
                    print("EOF reached")
                    continue
                raise KafkaException(msg.error())
            at_eof = False
            print(msg.value())
    finally:
        consumer.close()


def consume_high() -> None:
    consumer = KafkaConsumer(
        topic,
        group_id='pyconsumer',
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        value_deserializer=json_deserializer,
    )
    try:
        for msg in consumer:
            print(msg.value)
    finally:
        consumer.close()


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
    elif sys.argv[1] == "produce" and len(sys.argv) in (2, 3):
        produce(sys.argv[2] if len(sys.argv) == 3 else None)
    elif sys.argv[1] == "produce-high" and len(sys.argv) in (2, 3):
        produce_high(sys.argv[2] if len(sys.argv) == 3 else None)
    elif sys.argv[1] == "consume" and len(sys.argv) == 2:
        consume()
    elif sys.argv[1] == "consume-high" and len(sys.argv) == 2:
        consume_high()
    else:
        print_usage()


if __name__ == '__main__':
    main()
