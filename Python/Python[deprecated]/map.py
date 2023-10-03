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



plt.scatter(   0,    0, marker='^', color='limegreen', s=75) #xplr-aoa
plt.scatter(18.5, 12.5, marker='^', color='limegreen', s=75) #xplr-aoa
plt.scatter(18.5,    0, marker='v', color='deepskyblue', s=75) #esp32
plt.scatter(   0, 12.5, marker='v', color='deepskyblue', s=75) #esp32

ax.text(   0, -0.5, "xplr-aoa", fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
ax.text(18.5,   13, "xplr-aoa", fontsize=8, horizontalalignment='center', verticalalignment='center', color='limegreen')
ax.text(18.5, -0.5, "esp32", fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')
ax.text(   0,   13, "esp32", fontsize=8, horizontalalignment='center', verticalalignment='center', color='deepskyblue')

plt.scatter( 4.75, 7.75, marker='o', color='red', s=75) #tag p
plt.scatter(10.75, 7.75, marker='o', color='red', s=75) #tag q
plt.scatter(16.75, 7.75, marker='o', color='red', s=75) #tag r

plt.scatter(16.75, 7.75, marker='x', color='yellow', s=75) #tag r


plt.show()