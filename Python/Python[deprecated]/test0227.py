import threading
import multiprocessing as mp
import random
import time
import os

def job(queue, val, val_):
  queue.put(val + val_)

class producer(mp.Process):
  def __init__(self, queue):
    mp.Process.__init__(self)
    self.queue = queue

  def run(self):
    for i in range(10):
      item = random.randint(0, 256)
      self.queue.put(item)
      print("Process Producer: item %d append to queue %s "\
            % (item, self.name))
      time.sleep(1)
      print("The size of queue is %s"\
            % self.queue.qsize())

class consumer(mp.Process):
  def __init__(self, queue):
    mp.Process.__init__(self)
    self.queue = queue

  def run(self):
    while True:
      if (self.queue.empty()):
        print("The queue is empty")
        break
      else :
        time.sleep(2)
        item = self.queue.get()
        print("Process consumer : otem %d popped from by %s "\
              % (item, self.name))
        time.sleep(1)

if __name__ == '__main__':
  queue = mp.Queue()
  process_producer = producer(queue)
  process_consumer = consumer(queue)
  process_producer.start()
  process_consumer.start()
  process_producer.join()
  process_consumer.join()

  q = mp.Queue()
  p = mp.Process(target=job, args=(q, 10, 20))
  start_time = time.time()
  p.start() 
  p.join()
  end_time = time.time()
  print(end_time - start_time)
  # os.system("pause")