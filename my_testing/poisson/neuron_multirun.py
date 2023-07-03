import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np

pre_rate = 0.0
nrn = 2
dt=10

p.setup(1)

simtime = 100

init_rate = [0.15, 0.15]  # [0.1*i for i in range(nrn)]
pop_src = p.Population(nrn, p.IF_curr_exp(), label="src")

pop_src.set(i_offset=[0.15, 0.15])

pop_src.record('spikes')

pre_spikes_test = []

for i in range(simtime//dt):
    print(i)
    p.run(dt)
    new_rate = [0.1, 0.2]  # [np.random.rand()*(i+1) for j in range(nrn)]
    pop_src.set(i_offset=new_rate)

pre_spikes = pop_src.get_data('spikes')

plot_time = simtime

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(pre_spikes.segments[0].spiketrains,
          yticks=True, markersize=5.5, xlim=(0, plot_time),
          xticks=True, data_labels=['pre-spikes']),
    annotations="Simulated with {}".format(p.name()))

plt.show()

p.end()

print("\n job done")