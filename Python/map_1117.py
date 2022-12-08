from turtle import color
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
import matplotlib.patches as patches

# 顏色：https://matplotlib.org/stable/gallery/color/named_colors.html
# 散點圖：https://www.runoob.com/matplotlib/matplotlib-scatter.html
# 主要及次要格線：https://stackoverflow.com/questions/24943991/change-grid-interval-and-specify-tick-labels-in-matplotlib
# 矩形：https://www.delftstack.com/zh-tw/howto/matplotlib/how-to-draw-rectangle-on-image-in-matplotlib/

fig, ax = plt.subplots()
ax.set_ylim(-1, 13.5)
ax.set_xlim(-1, 13.5)
# Change major ticks to show every 20.
ax.xaxis.set_major_locator(MultipleLocator(12))
ax.yaxis.set_major_locator(MultipleLocator(12)) # 主要格線距離

# Change minor ticks to show every 5. (20/4 = 5)
ax.xaxis.set_minor_locator(AutoMinorLocator(6))
ax.yaxis.set_minor_locator(AutoMinorLocator(6)) # 切n段

# Turn grid on for both major and minor ticks and style minor slightly
# differently.
ax.grid(which='major', color='#CCCCCC', linestyle='dashed')
ax.grid(which='minor', color='#CCCCCC', linestyle='dotted')

tiles = []
for x in range(0, 25):
    for y in range(0, 37):
        if x % 6 == 0 and y % 6 == 0:
            tiles.append((x/2, y/2))
        elif (x-3) % 6 == 0 and (y-3) % 6 == 0:
            tiles.append((x/2, y/2))
for tile in tiles:
    rect = patches.Rectangle(tile, 0.5, 0.5, linewidth=1, edgecolor='none', facecolor='mistyrose')
    ax.add_patch(rect)
#                         x  y   w  h

# Add the patch to the Axes

def plot_anchor(x, y, nickName, type):
    if(type == 'xplr-aoa'):
        ax.scatter(x, y, marker='^', color='limegreen', s=75) #xplr-aoa
        ax.text(x, y-0.5, 'xplr-aoa', fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
        ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
    elif(type == 'esp32'):
        plt.scatter(x, y, marker='v', color='deepskyblue', s=75) #esp32
        ax.text(x, y-0.5, 'esp32', fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')
        ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')

def plot_tag(x, y, tagName):
    plt.scatter(x, y, marker='o', color='red', s=75)
    ax.text( x, y+0.5, tagName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')

plot_anchor(   0,    0, 'Anchor B', 'xplr-aoa')
plot_anchor(12.5,    0, 'Anchor A', 'xplr-aoa')
plot_anchor(   0, 12.5, 'Anchor D', 'esp32')
plot_anchor(12.5, 12.5, 'Anchor C', 'esp32')

plot_tag(9.25, 3.25, 'T1')
plot_tag(6.25, 3.25, 'T2')
plot_tag(3.25, 3.25, 'T3')
plot_tag(3.25, 9.25, 'T4')
plot_tag(9.25, 9.25, 'T5')
plot_tag(6.25, 6.25, 'T6')

#plt.scatter(16.75, 7.75, marker='x', color='yellow', s=75) #tag r


plt.show()