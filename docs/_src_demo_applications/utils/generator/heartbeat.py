class HeartBeat:
    """
    Technical record to deliver heartbeat messages. Check for this type with isinstanceof().
    """
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def get_timestamp(self):
        return self.timestamp
