import spynnaker8 as p

from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np

p.setup(timestep=1.0)

input_size = 2
rate = 2
input_pops = []
input_pops.append(p.Population(input_size,
                               p.SpikeSourcePoisson(rate=rate)))
input_pops[-1].record('spikes')

output_size = 2
readout_pops = []
for i in range(2):
    readout_pops.append(p.Population(output_size+i, p.IF_cond_exp()))
    readout_pops[-1].record('spikes')

projections = []
for i in range(2):
    projections.append(p.Projection(input_pops[0], readout_pops[i],
                                    p.OneToOneConnector(),
                                    p.StaticSynapse(weight=0.1, delay=1)))

runtime = 5 * 1000
p.run(runtime)

for n in range(len(projections)):
    print(projections[n].get(['weight', 'delay'], 'list'))

in_spikes = []
out_spikes = []
in_spikes.append(input_pops[0].get_data('spikes').segments[0].spiketrains)
for i in range(2):
    out_spikes.append(readout_pops[i].get_data('spikes').segments[0].spiketrains)

Figure(
    Panel(in_spikes[0], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(out_spikes[0], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(out_spikes[1], xlabel="Time (ms)", ylabel="nID", xticks=True),
)
plt.show()

p.end()

