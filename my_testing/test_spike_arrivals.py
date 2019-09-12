import spynnaker8 as sim
import os
import numpy
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 50)

n_pop = 500
runtime = 10000

input = sim.Population(
    n_pop, sim.SpikeSourceArray(spike_times=[0,1000,2000,3000,4000]), label="input")
pop_1 = sim.Population(n_pop, sim.IF_curr_exp(), label="pop_1")

sim.Projection(input, pop_1, sim.OneToOneConnector(),
               synapse_type=sim.StaticSynapse(weight=5, delay=1))

# pop_1.set(v=-60.0)
pop_1.tset(v=-60.0)

pop_1.record(["spikes", "v", "gsyn_exc"])

sim.run(runtime)

v = pop_1.spinnaker_get_data("v")
v1 = pop_1.get_data("v")
spikes1 = pop_1.get_data("spikes")

print(v)

path1 = "test1v.txt"
if os.path.exists(path1):
    os.remove(path1)

current_file_path = os.path.dirname(os.path.abspath(__file__))
file1 = os.path.join(current_file_path, path1)
numpy.savetxt(file1, v)

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v1.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="Membrane potential (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes1.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=1.5, xlim=(0, runtime)),
    title="spike arrival times, split pops",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()


sim.end()