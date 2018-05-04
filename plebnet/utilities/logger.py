import logging


class Logger(object):
    def __init__(self, name="logger", file="/root/Documents/logs"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.info)

        self.handler = logging.FileHandler(file)
        self.handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)

        self.logger.addHandler(self.handler)

    def log(self, file, method, msg):
        tex = fill(file, 10) + " : " + fill(method, 10) + " : " + msg
        print(tex)
        self.logger.info(tex)


def fill(tex, l):
    if len(tex) > l:
        tex = tex.substring(0, l-3) + "..."
    else:
        while len(tex) < l:
            tex = tex + " "
    return tex
