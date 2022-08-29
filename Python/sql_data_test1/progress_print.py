import time

for i in range(100):
    time.sleep(0.1)
    print(f'Downloading File FooFile.txt {i}%\r', end="")