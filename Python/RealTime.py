import paho.mqtt.client as mqtt
import numpy as np
import time
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.patches as patches
import math


plt.axis([0, 10, 0, 1])
now_time = time.time()
pre_time = now_time
MAX_NUM = 20
tag_a_anchor_a_list = [0] * MAX_NUM
tag_a_anchor_a_index = 0
tag_a_anchor_b_list = [0] * MAX_NUM
tag_a_anchor_b_index = 0
tag_b_anchor_a_list = [0] * MAX_NUM
tag_b_anchor_a_index = 0
tag_b_anchor_b_list = [0] * MAX_NUM
tag_b_anchor_b_index = 0

anchor_a_id = '6C1DEBA097F3'
anchor_b_id = '6C1DEBA097FA'
tag_a_id = '6C1DEBA42193'
tag_b_id = '6C1DEBA41680'

def cal_loc(angle_a:list, angle_b:list):
    angle_2 = avg(angle_a) +45
    angle_1 = -avg(angle_b) +45
    print("ANGLE", angle_2, angle_1)
    angle_sum = angle_2 + angle_1
    angle_2 = angle_2 / 360 * (2*math.pi)
    angle_1 = angle_1 / 360 * (2*math.pi)
    angle_sum = angle_sum / 360 * (2*math.pi)
    d = 14.7 * math.sin(angle_1) * math.sin(angle_2) / math.sin(angle_sum)
    u = d / math.tan(angle_1)
    return (u, d*0.8)

def add_index(index, max):
    if index < max - 1:
        return index + 1
    else:
        return 0

def avg(lst):
    return sum(lst) / len(lst)

# 當地端程式連線伺服器得到回應時，要做的動作
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("data/6C1DEBA42193")
    client.subscribe("data/6C1DEBA41680")

# 當接收到從伺服器發送的訊息時要進行的動作
def on_message(client, userdata, msg):
    global now_time
    global pre_time
    global tag_a_anchor_a_index, tag_a_anchor_a_list
    global tag_a_anchor_b_index, tag_a_anchor_b_list
    global tag_b_anchor_a_index, tag_b_anchor_a_list
    global tag_b_anchor_b_index, tag_b_anchor_b_list
    # 轉換編碼utf-8才看得懂中文
    #print(msg.topic+" "+ msg.payload.decode('utf-8'))
    if (msg.topic == 'data/6C1DEBA42193'): ## tag a
        temp = json.loads(msg.payload.decode('utf-8'))
        if(temp['anchor_id'] == '6C1DEBA097F3'): # anchor a
            tag_a_anchor_a_list[tag_a_anchor_a_index] = temp['azimuth']
            tag_a_anchor_a_index = add_index(tag_a_anchor_a_index, MAX_NUM)
        if(temp['anchor_id'] == '6C1DEBA097FA'): # anchor b
            tag_a_anchor_b_list[tag_a_anchor_b_index] = temp['azimuth']
            tag_a_anchor_b_index = add_index(tag_a_anchor_b_index, MAX_NUM)
    if (msg.topic == 'data/6C1DEBA41680'): ## tag b
        #print('bbb')
        temp = json.loads(msg.payload.decode('utf-8'))
        if(temp['anchor_id'] == '6C1DEBA097F3'): # anchor a
            tag_b_anchor_a_list[tag_b_anchor_a_index] = temp['azimuth']
            tag_b_anchor_a_index = add_index(tag_b_anchor_a_index, MAX_NUM)
        if(temp['anchor_id'] == '6C1DEBA097FA'): # anchor b
            tag_b_anchor_b_list[tag_b_anchor_b_index] = temp['azimuth']
            tag_b_anchor_b_index = add_index(tag_b_anchor_b_index, MAX_NUM)

    now_time = time.time()

    if(now_time - pre_time > 0.5):
        plt.clf()
        plt.grid()
        
        def plot_anchor(x, y, nickName, type):
            if(type == 'xplr-aoa'):
                plt.scatter(x, y, marker='^', color='limegreen', s=75) #xplr-aoa
                plt.text(x, y-0.5, 'xplr-aoa', fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
                plt.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
            elif(type == 'esp32'):
                plt.scatter(x, y, marker='v', color='deepskyblue', s=75) #esp32
                plt.text(x, y-0.5, 'esp32', fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')
                plt.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')

        plot_anchor(   0,    0, 'Anchor B', 'xplr-aoa')
        plot_anchor(12.5,    0, 'Anchor A', 'xplr-aoa')
        #plot_anchor(   0, 12.5, 'Anchor D', 'esp32')
        #plot_anchor(12.5, 12.5, 'Anchor C', 'esp32')
        
        plt.ylim(-1, 13.5)
        plt.xlim(-1, 13.5)

        tiles = []
        for x in range(0, 25):
            for y in range(0, 37):
                if x % 6 == 0 and y % 6 == 0:
                    tiles.append((x/2, y/2))
                elif (x-3) % 6 == 0 and (y-3) % 6 == 0:
                    tiles.append((x/2, y/2))
        for tile in tiles:
            rect = patches.Rectangle(tile, 0.5, 0.5, linewidth=1, edgecolor='none', facecolor='mistyrose')
            plt.gca().add_patch(rect)
        #for i in range(MAX_NUM):
        #    plt.scatter(3, tag_a_anchor_a_list[i], color=(0.1, 0.2, 0.5), alpha = 0.5)
        ax, ay = cal_loc(tag_a_anchor_a_list, tag_a_anchor_b_list)
        bx, by = cal_loc(tag_b_anchor_a_list, tag_b_anchor_b_list)
        print(tag_b_anchor_a_index, tag_b_anchor_b_index)
        #print(ax, ay)
        plt.scatter(ax, ay, color=(1, 0, 0), alpha = 0.8)
        plt.scatter(bx, by, color=(0, 0, 1), alpha = 0.8)
        pre_time = now_time
        #plt.draw()
        plt.pause(0.01)


# 連線設定
# 初始化地端程式
client = mqtt.Client()

# 設定連線的動作
client.on_connect = on_connect

# 設定接收訊息的動作
client.on_message = on_message

# 設定登入帳號密碼
client.username_pw_set("try","xxxx")

# 設定連線資訊(IP, Port, 連線時間)
#client.connect("xplr-aoa.local", 1883, 60)
client.connect("192.168.245.144", 1883, 60)
#plt.show()

client.loop_forever()
