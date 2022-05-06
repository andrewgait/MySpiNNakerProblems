import pyNN.spiNNaker as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

n_pop = 4
runtime = 100

input_pop2 = sim.Population(n_pop, sim.SpikeSourceArray([0]), label="input")
pop = sim.Population(n_pop, sim.IF_curr_exp(), label="pop")

weights = []
delays = []
weights.append(0.3)
delays.append(1)
for n in range(n_pop-2):
    weights.append(1.0)
    delays.append(77)
weights.append(2.0)
delays.append(37)

c2 = sim.Projection(input_pop2, pop, sim.OneToOneConnector(),
                    sim.StaticSynapse(weight=weights, delay=delays))

pop.record(['v', 'spikes'])

sim.run(runtime)

print(c2.get(['weight', 'delay'], 'list'))

# get data (could be done as one, but can be done bit by bit as well)
spikes = pop.get_data('spikes')
v = pop.get_data('v')

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=0.5, xlim=(0, runtime)),
    title="one-to-one connector, varying delays",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()
