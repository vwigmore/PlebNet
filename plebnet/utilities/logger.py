import logging


def log(msg, method="", name="logger", file="/root/Documents/logs"):
    logger = get_logger(name, file)
    # prepare the output
    tex = fill(method, 15) + " : " + msg
    # output the log details
    print(tex)
    logger.info(tex)


def error(msg, method="", name="logger", file="/root/Documents/logs"):
    logger = get_logger(name, file)
    # prepare the output
    tex = fill(method, 15) + " : " + msg
    # output the log details
    print(tex)
    logger.error(tex)


def get_logger(name, file):
    # create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # create formatter and handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler(file)

        # combine
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def fill(tex, l):
    if len(tex) > l:
        # tex = tex.substring(0, l-3) + "..."
        tex = tex[:l-2] + ".."
    else:
        while len(tex) < l:
            tex = tex + " "
    return tex
