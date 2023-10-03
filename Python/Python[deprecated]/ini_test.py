import configparser
from datetime import datetime
# @see usage: https://www.delftstack.com/zh-tw/howto/python/python-ini-file/

#filename = "anchor.ini"


def get_anchor_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    config_dict = config._sections
    for anchor in [section for section in config.sections() if 'anchor' in section]:
        for key in ['coordinate', 'norm_vector', 'anim_vector', 'elev_vector', 'const']:
            config_dict[anchor][key] = eval(config_dict[anchor][key])
    return config_dict

def get_measurement_data(anchor_config:dict, anchor_name:str, start_time:int, end_time:int): # time format in second
    try:
        start = datetime.fromtimestamp(start_time)
        end = datetime.fromtimestamp(end_time)
        delta = end - start
    except:
        raise ValueError('Time format error. ')
    id = anchor_config[anchor_name]['id']
    print(id)
    return 0


anchor_config = get_anchor_config("anchor.ini")
print(anchor_config)

try:
    measurement_data = get_measurement_data(anchor_config, 'anchor-b', 1657873805, 1657883805)
except ValueError as ex:
    print(f"{ex}")


'''
# Reading Data
keys = None
config
print(config.sections())
print(config._sections)


try:
    value = config.get('CONFIG', 'version')
    #keys = ast.literal_eval(value)
    print(value)
except configparser.Error as ex:
    print(f"{ex.message}")

coord = None
try:
    value = config.get('ANCHOR_A', 'coordinate')
    coord = eval(value)
    print(coord)
except configparser.Error as ex:
    print(f"{ex.message}")
'''



'''
keys = [
    "time",
    "time_format",
    "language",
    "testing",
    "production"
]

for key in keys:
    try:
        value = config.get("SETTINGS", key)
        print(f"{key}:", value)
    except configparser.NoOptionError:
        print(f"No option '{key}' in section 'SETTINGS'")
'''