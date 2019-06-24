import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

n_pre_neurons = 40
n_post_neurons = 60
n_pop2 = 60
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 40)  # n_post_neurons // 2)

n_post = 10
runtime = 100

input_pop = sim.Population(n_pre_neurons, sim.SpikeSourceArray([0]), label="input")
pop = sim.Population(n_post_neurons, sim.IF_curr_exp(), label="pop")

input_pop2 = sim.Population(n_pre_neurons, sim.SpikeSourceArray([0]), label="input2")
pop2 = sim.Population(n_pop2, sim.IF_curr_exp(), label="pop2")

pop3 = sim.Population(n_post_neurons, sim.IF_curr_exp(), label="pop2")

weights = 3.0
delays = 5

c1 = sim.Projection(input_pop, pop, sim.FixedNumberPostConnector(n_post),
                    sim.StaticSynapse(weight=weights, delay=delays))

c2 = sim.Projection(input_pop2, pop2,
                    sim.FixedNumberPostConnector(n_post,
                                                 with_replacement=True),
                    sim.StaticSynapse(weight=weights, delay=delays))

c3 = sim.Projection(pop2, pop2,
                    sim.FixedNumberPostConnector(n_post,
                                                 with_replacement=True,
                                                 allow_self_connections=False),
                    sim.StaticSynapse(weight=weights, delay=delays))

c4 = sim.Projection(input_pop2, pop3,
                    sim.FixedNumberPostConnector(n_post,
                                                 allow_self_connections=False),
                    sim.StaticSynapse(weight=weights, delay=delays))

c5 = sim.Projection(pop3, pop3,
                    sim.FixedNumberPostConnector(n_post,
                                                 allow_self_connections=False),
                    sim.StaticSynapse(weight=weights, delay=delays))

pop2.record(['v', 'spikes'])

sim.run(runtime)

weights_delays = sorted(c1.get(['weight', 'delay'], 'list'),
                        key = lambda x: x[0])

weights_delays2 = sorted(c2.get(['weight', 'delay'], 'list'),
                         key = lambda x: x[0])

weights_delays3 = sorted(c3.get(['weight', 'delay'], 'list'),
                         key = lambda x: x[0])

weights_delays4 = sorted(c4.get(['weight', 'delay'], 'list'),
                         key = lambda x: x[0])

weights_delays5 = sorted(c5.get(['weight', 'delay'], 'list'),
                         key = lambda x: x[0])

print(weights_delays)
print(len(weights_delays))
print(weights_delays2)
print(len(weights_delays2))
print(weights_delays3)
print(len(weights_delays3))
print(weights_delays4)
print(len(weights_delays4))
print(weights_delays5)
print(len(weights_delays5))

# get data (could be done as one, but can be done bit by bit as well)
spikes = pop2.get_data('spikes')
v = pop2.get_data('v')

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=0.5, xlim=(0, runtime)),
    title="one-to-one connector, varying delays",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()
