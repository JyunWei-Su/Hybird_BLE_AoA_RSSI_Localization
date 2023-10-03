import numpy as np
import cupy as cp
import time

### Numpy and CPU
s = time.time()
for i in range(100):
  x_cpu = np.ones((100,1000,1000))
e = time.time()
print(e-s)

### Cupy and GPU
s = time.time()
for i in range(10000):
  x_gpu = cp.ones((100,1000,1000))
e = time.time()
print(e-s)