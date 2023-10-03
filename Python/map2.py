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
ax.set_xlim(-1, 19.5)
# Change major ticks to show every 20.
ax.xaxis.set_major_locator(MultipleLocator(6))
ax.yaxis.set_major_locator(MultipleLocator(6)) # 主要格線距離

# Change minor ticks to show every 5. (20/4 = 5)
ax.xaxis.set_minor_locator(AutoMinorLocator(12))
ax.yaxis.set_minor_locator(AutoMinorLocator(12)) # 切n段

# Turn grid on for both major and minor ticks and style minor slightly
# differently.
ax.grid(which='major', color='#CCCCCC', linestyle='--')
ax.grid(which='minor', color='#CCCCCC', linestyle=':')

tiles = []
for x in range(0, 37):
    for y in range(0, 25):
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
        plt.scatter(x, y, marker='^', color='limegreen', s=75) #xplr-aoa
        ax.text(x, y-0.5, 'xplr-aoa', fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
        ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
    elif(type == 'esp32'):
        plt.scatter(x, y, marker='v', color='deepskyblue', s=75) #esp32
        ax.text(x, y-0.5, 'esp32', fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')
        ax.text(x, y+0.5, nickName, fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')

plot_anchor(   0,    0, 'Anchor B', 'xplr-aoa')
plot_anchor(18.5, 12.5, 'Anchor A', 'xplr-aoa')
plot_anchor(18.5,    0, 'Anchor C', 'esp32')
plot_anchor(   0, 12.5, 'Anchor D', 'esp32')

plt.scatter( 4.75, 7.75, marker='o', color='red', s=75) #tag p
plt.scatter(10.75, 7.75, marker='o', color='red', s=75) #tag q
plt.scatter(16.75, 7.75, marker='o', color='red', s=75) #tag r
plt.scatter( 1.75, 4.75, marker='o', color='red', s=75) #tag p
plt.scatter( 7.75, 4.75, marker='o', color='red', s=75) #tag q
plt.scatter(13.75, 4.75, marker='o', color='red', s=75) #tag r
ax.text(16.75, 7.75+0.5, 'T1', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text(10.75, 7.75+0.5, 'T2', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text( 4.75, 7.75+0.5, 'T3', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text( 1.75, 4.75+0.5, 'T4', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text( 7.75, 4.75+0.5, 'T5', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')
ax.text(13.75, 4.75+0.5, 'T6', fontsize=8, horizontalalignment='center', verticalalignment='center', color='red')

result = [(16.25, 8.14 ), (16.28, 8.15 ), (15.40, 7.35 ), (15.22, 7.96 ), (15.94, 8.06 ), \
(16.06, 8.04 ), (16.07, 7.85 ), (16.82, 7.70 ), (16.51, 7.34 ), (16.52, 7.82 ), \
(16.09, 8.07 ), (15.90, 7.78 ), (16.58, 7.95 ), (17.12, 7.78 ), (16.43, 7.73 ), \
(16.08, 8.06 ), (16.23, 7.84 ), (15.93, 8.10 ), (15.97, 7.72 ), (15.90, 8.18 ), \
(16.44, 7.86 ), (16.11, 6.99 ), (16.04, 9.24 ), (16.15, 8.30 ), (16.15, 8.30 ), \
(15.92, 7.80 ), (16.01, 7.72 ), (16.06, 7.54 ), (15.66, 7.66 ), (15.28, 7.66 ), \
(16.19, 7.50 ), (15.83, 7.89 ), (15.74, 6.96 ), (15.88, 7.69 ), (16.00, 7.71 ), \
(14.98, 8.26 ), (15.55, 8.09 ), (16.13, 8.08 ), (15.99, 7.84 ), (15.73, 7.89 ), \
(15.73, 7.89 ), (15.79, 7.75 ), (14.69, 6.96 ), (15.98, 7.48 ), (15.95, 7.50 ), \
(16.55, 7.65 ), (16.05, 8.06 ), (15.82, 7.94 ), (15.82, 7.94 ), (15.42, 8.94 ), \
(15.42, 8.94 ), (16.16, 7.96 ), (14.18, 6.99 ), (16.16, 8.65 ), (15.64, 7.43 ), \
(15.43, 8.16 ), (16.19, 7.77 ), (16.13, 7.16 ), (15.89, 7.29 ), (16.73, 5.99 )]

for point_x, point_y in result:
    plt.scatter(point_x, point_y, marker='.', color='blue', s=10)


plt.scatter(16.75, 7.75, marker='x', color='yellow', s=75) #tag r


plt.show()
