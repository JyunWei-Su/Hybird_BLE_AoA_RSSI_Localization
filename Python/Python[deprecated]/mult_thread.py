import threading
import time

# 子執行緒的工作函數
def job(i, start, end, results):
  time.sleep(i)
  results[i] = i-10
  print("Thread", i, start, end)
  

# 建立 5 個子執行緒
total_threads = 5
threads = [None] * total_threads
results = [None] * total_threads
for i in range(total_threads):
  threads[i] = threading.Thread(target = job, args = (i, i*2, i*3, results))
  threads[i].start()

# 主執行緒繼續執行自己的工作
# ...

# 等待所有子執行緒結束
for i in range(total_threads):
  threads[i].join()

print(results)

print("Done.")