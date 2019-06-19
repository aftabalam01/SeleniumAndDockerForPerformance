import logging

class Logger(object):
    def __init_(self,name=__name__,level=logging.DEBUG):
        """

        :param name:
        :param level:
        :return:
        """

    def getLogger(self,name=__name__,level=logging.DEBUG):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        return logger