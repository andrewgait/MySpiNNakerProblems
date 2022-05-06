import pyNN.spiNNaker as sim
from pacman.model.constraints.placer_constraints import (
    RadialPlacementFromChipConstraint)
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

constraint = RadialPlacementFromChipConstraint(1, 1)

runtime = 10

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 100)

pop_1 = sim.Population(200, sim.IF_curr_exp(), label="pop_1")
# pop_1.add_placement_constraint(x=1, y=1)

input = sim.Population(1, sim.SpikeSourceArray(spike_times=[0]), label="input")

pop_1.set_constraint(constraint)
print(pop_1._vertex.constraints)

sim.Projection(input, pop_1, sim.AllToAllConnector(),
               synapse_type=sim.StaticSynapse(weight=5, delay=1))

pop_1.record(['v', 'spikes'])

sim.run(runtime)

# get data (could be done as one, but can be done bit by bit as well)
spikes = pop_1.get_data('spikes')
v = pop_1.get_data('v')

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=2.0, xlim=(0, runtime)),
    title="testing radial placer constraint",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()