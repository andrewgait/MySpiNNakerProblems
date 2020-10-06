import spynnaker8 as p

from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np

p.setup(timestep=1.0)

# p.set_number_of_neurons_per_core(p.IF_cond_exp, 100)
# p.set_number_of_neurons_per_core(p.SpikeSourcePoisson, 100)

input_size = 10
rate = 2
input_pops = []
input_pops.append(p.Population(input_size,
                               p.SpikeSourcePoisson(rate=rate)))
input_pops[-1].record('spikes')

n_outputs = 9
output_size = 2
readout_pops = []
for i in range(n_outputs):
    readout_pops.append(p.Population(output_size+i, p.IF_cond_exp()))
    readout_pops[-1].record('spikes')

projections = []
for i in range(n_outputs):
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
for i in range(n_outputs):
    out_spikes.append(readout_pops[i].get_data('spikes').segments[0].spiketrains)

Figure(
    Panel(in_spikes[0], xlabel="Time (ms)", ylabel="nID", xticks=True, yticks=True),
    Panel(out_spikes[0], xlabel="Time (ms)", ylabel="nID", xticks=True, yticks=True),
    Panel(out_spikes[1], xlabel="Time (ms)", ylabel="nID", xticks=True, yticks=True),
)
plt.show()

p.end()

