import spynnaker8 as p

from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np

p.setup(timestep=1.0)

input_size = 3
rate = 2
input_pops = []
for i in range(3):
    input_pops.append(p.Population(input_size-i,
                                   p.SpikeSourcePoisson(rate=rate)))
    input_pops[-1].record('spikes')

readout_pops = []
for i in range(3):
    readout_pops.append(p.Population(input_size-i, p.IF_cond_exp()))
    readout_pops[-1].record('spikes')

projections = []
for i in range(3):
    for j in range(3):
        projections.append(p.Projection(input_pops[i], readout_pops[j],
                                        p.OneToOneConnector(),
                                        p.StaticSynapse(weight=0.1, delay=1)))

runtime = 5 * 1000
p.run(runtime)

for n in range(len(projections)):
    print(projections[n].get(['weight', 'delay'], 'list'))

in_spikes = []
out_spikes = []
for i in range(3):
    in_spikes.append(input_pops[i].get_data('spikes').segments[0].spiketrains)
    out_spikes.append(readout_pops[i].get_data('spikes').segments[0].spiketrains)

Figure(
    Panel(in_spikes[0], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(in_spikes[1], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(in_spikes[2], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(out_spikes[0], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(out_spikes[1], xlabel="Time (ms)", ylabel="nID", xticks=True),
    Panel(out_spikes[2], xlabel="Time (ms)", ylabel="nID", xticks=True)
)
plt.show()

p.end()

