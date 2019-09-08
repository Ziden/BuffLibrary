

class BuffErrorCodes(object):
    REMOVING_BUFF_NOT_FROM_SOURCE = 1


class BuffException(Exception):
    def __init__(self, error):
        self.error = error