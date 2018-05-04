

def log(type, subtype, msg):
    print(fill(type, 10) + " : " + fill(subtype, 10) + " : " + msg)


def fill(tex, l):
    st = tex
    while len(st) < l:
        st = st + " "
    return st
