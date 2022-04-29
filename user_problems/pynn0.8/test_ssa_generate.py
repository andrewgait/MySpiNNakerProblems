import numpy as np
import random
from PIL.JpegImagePlugin import APP

data_y = 12
data_x = 8
data_size = data_x * data_y

data_point = np.zeros((data_size,), dtype=np.dtype([('x', np.uint16), ('y', np.uint16)]))

spike_array = [[] for _ in range(data_size)]

data_point_spike_array = [[] for _ in range(data_size)]

for d in range(data_size):
    data_point["x"][d] = (d // data_y)
    data_point["y"][d] = (d % data_y)
    index = data_point["x"][d]*data_y+(data_point["y"][d])
    # print(index)

    time = random.randint(1,9)

    data_point_spike_array[index].append(time)


data_point_spike_array[10].append(time)
data_point_spike_array[20].append(time)

print(spike_array)
print("------")
print(data_point_spike_array)

idx_sa = 0
for sa,dpsa in zip(spike_array,data_point_spike_array):
    spike_array[idx_sa] = sa+dpsa
    idx_sa+=1

print("------")
print(spike_array)
# print(spike_array[0])
# print(spike_array[1000000])
test = 0
for d in range(idx_sa):
    test += len(spike_array[d])
print(test)
# print(spike_array)
# print(len(spike_array))