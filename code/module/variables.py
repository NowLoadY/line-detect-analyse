
def _init():
    global _global_dict
    _global_dict = {}


def set_val(key, value):

    _global_dict[key] = value


def get_val(key):
    try:
        return _global_dict[key]
    except:
        print('读取' + key + '失败\r\n')

