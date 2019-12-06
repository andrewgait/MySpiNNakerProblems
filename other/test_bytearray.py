import numpy as np
import struct
rows = 2
values = 2

raw = bytearray(struct.pack("f", 10.0)) + bytearray(struct.pack("d", 11.0)) + bytearray(struct.pack("d", 10.0))
raw += bytearray(struct.pack("f", 20.0)) + bytearray(struct.pack("d", 21.0)) + bytearray(struct.pack("d", 21.0))

#raw = bytearray(os.urandom(rows * (4 + values * 8)))
a = np.asarray(raw, dtype="uint8")
b = a.reshape(rows, (4 + values * 8))
c = np.zeros(rows * 4, dtype="uint8")
d = c.reshape(rows, 4)
e = np.concatenate([d, b], axis=1)
g = e.reshape(rows * (8 + values * 8))
h = g.view("double")
j = h.reshape(rows, values+1)
print(j)
print(j.shape)
