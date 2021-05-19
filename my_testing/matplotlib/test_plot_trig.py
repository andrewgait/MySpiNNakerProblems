import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0, 400, 1.0)

amplitude = 1.0
offset = 1.0
frequency = 10.0
phase = 180.0 * (np.pi / 180.0)

y = offset + amplitude * np.sin((x * 2 * np.pi * frequency / 1000.0) + phase)

plt.plot(x,y)

plt.show()

