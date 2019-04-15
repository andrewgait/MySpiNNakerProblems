import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

n_pop = 9
runtime = 100

spiking = [[n*5] for n in range(n_pop)]
print('ssa using ', spiking)

input_pop = sim.Population(n_pop, sim.SpikeSourceArray(spiking), label="input")
pop = sim.Population(n_pop, sim.IF_curr_exp(), label="pop")

weights = 3.0
delays = 5

shape_pre = [3, 3]
shape_post = [3, 3]
shape_kernel = [3, 3]
kernel_connector = sim.KernelConnector(shape_pre, shape_post, shape_kernel)
c2 = sim.Projection(input_pop, pop, kernel_connector,
                    sim.StaticSynapse(weight=weights, delay=delays))

pop.record(['v', 'spikes'])

sim.run(runtime)

weightsdelays = sorted(c2.get(['weight', 'delay'], 'list'),
                       key = lambda x: x[1])
print(weightsdelays)
print('there are', len(weightsdelays), 'connections')

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
    title="kernel connector testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()
