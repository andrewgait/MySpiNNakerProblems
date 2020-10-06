import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(1.0)

sources = 500
destinations = 1

# conn = sim.OneToOneConnector()
conn = sim.AllToAllConnector()
# fixedprob = sim.FixedProbabilityConnector(1.0)
# fixedtotal = sim.FixedTotalNumberConnector(200*200)

# spike_times = [[10*i+1] for i in range(sources)]
# pop1 = sim.Population(sources, sim.SpikeSourceArray(spike_times), label="pop1")
pop1 = sim.Population(sources, sim.IF_curr_exp(), label="pop1")
pop2 = sim.Population(destinations, sim.IF_curr_exp(), label="pop2")
synapse_type = sim.StaticSynapse(weight=4.0, delay=1)
projection = sim.Projection(
    pop1, pop2, conn, synapse_type=synapse_type)
# conn_list = [(0, 0, -0.5, 10)]
proj_list = sim.Projection(pop1, pop2, sim.OneToOneConnector(),
                           sim.StaticSynapse(weight=-0.06, delay=10))

pop2.record('all')

runtime=100
sim.run(runtime)

weights = projection.get(["weight"], "list")
print(weights)
print(sum(weight[2] for weight in weights))
print(len(weights))
weights_list = proj_list.get(["weight"], "list")
print(weights_list)

# v = pop2.get_data('v')
# gsyn_exc = pop2.get_data('gsyn_exc')
# gsyn_inh = pop2.get_data('gsyn_inh')
# spikes = pop2.get_data('spikes')
#
# Figure(
#     # raster plot of the presynaptic neuron spike times
#     Panel(spikes.segments[0].spiketrains,
#           yticks=True, markersize=1.0, xlim=(0, runtime)),
#     # membrane potential of the postsynaptic neuron
#     Panel(v.segments[0].filter(name='v')[0],
#           ylabel="Membrane potential (mV)",
#           data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
#     Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
#           ylabel="gsyn excitatory (mV)",
#           data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
#     Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
#           ylabel="gsyn inhibitory (mV)",
#           data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
#     title="Testing projections on views",
#     annotations="Simulated with {}".format(sim.name())
# )
# plt.show()

sim.end()