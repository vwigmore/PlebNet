import logging


def log(msg, method="", name="logger", file="/root/Documents/logs"):
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

    # prepare the output
    tex = fill(method, 10) + " : " + msg

    # output the log details
    print(tex)
    logger.info(tex)


def fill(tex, l):
    if len(tex) > l:
        tex = tex.substring(0, l-3) + "..."
    else:
        while len(tex) < l:
            tex = tex + " "
    return tex
