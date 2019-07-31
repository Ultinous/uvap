class GeneratorInterface:
    """
    Inherit from this class to read and handle arbitrary objects sending messages.
    """
    def stopGenerator(self):
        raise NotImplementedError

    def getMessages(self):
        raise NotImplementedError
