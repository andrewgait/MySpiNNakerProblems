import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel, DataTable
import matplotlib.pyplot as plt
import numpy as np

pre_rate = 100
nrn = 1
dt=10

p.setup(1)

simtime = 100

pop_src = p.Population(nrn, p.SpikeSourcePoisson(rate=pre_rate), label="src")

pop_src.record('spikes')

for i in range(simtime//dt):
        print(i)
        p.run(dt)

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