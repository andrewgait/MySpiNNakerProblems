import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
from pyNN.random import NumpyRNG
import random

sources = 240
destinations = 250

sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 200)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 200)

pop1 = sim.Population(sources, sim.SpikeSourceArray(spike_times=[10,50]),
                      label="input")
pop2 = sim.Population(destinations, sim.IF_curr_exp(),
                      label="pop2")
synapse_type_onetoone = sim.StaticSynapse(weight=5.5, delay=2)
synapse_type_alltoall = sim.StaticSynapse(weight=0.5, delay=5)
synapse_type_alltoall2 = sim.StaticSynapse(weight=1.5, delay=5)
synapse_type_fp = sim.StaticSynapse(weight=2.5, delay=5)

# pop1view = pop1[250:258]
# pop2view = pop2[250:258]
pop1view = pop1[1:6]
pop2view = pop2[198:203]

pop1view_all = pop1[200:210]
pop2view_all = pop2[100:105]
pop2view_all2 = pop2[190:205]

pop1view_fp = pop1[25:45]
pop2view_fp = pop2[65:85]

pop1view_wrong = pop1[24,25,27,29]
pop2view_wrong = pop2[36:49]

# pop2view.set(i_offset=0.1)

onetoone_connector = sim.OneToOneConnector()
alltoall_connector = sim.AllToAllConnector()
alltoall_connector2 = sim.AllToAllConnector(allow_self_connections=False)
onetoone_connector2 = sim.OneToOneConnector()

rng = NumpyRNG(seed=None, parallel_safe=True)

fixedprob_connector = sim.FixedProbabilityConnector(0.25, rng=rng)

projection_one = sim.Projection(pop1view, pop2view, onetoone_connector,
                                synapse_type=synapse_type_onetoone)
projection_all = sim.Projection(pop1view_all, pop2view_all, alltoall_connector,
                                synapse_type=synapse_type_alltoall)
projection_all_same = sim.Projection(pop2view_all2, pop2view_all2, alltoall_connector2,
                                     synapse_type=synapse_type_alltoall2)
projection_fp = sim.Projection(pop1view_fp, pop2view_fp, fixedprob_connector,
                               synapse_type=synapse_type_fp)
projection_one2 = sim.Projection(pop1view_wrong, pop2view_wrong, onetoone_connector2,
                                 synapse_type=synapse_type_onetoone)

# sim.run(0)

pop2.record('all')

before_pro_one = projection_one.get(["weight", "delay"], "list")
before_pro_all = projection_all.get(["weight", "delay"], "list")
before_pro_all2 = projection_all_same.get(["weight", "delay"], "list")
before_pro_fp = projection_fp.get(["weight", "delay"], "list")
before_pro_one2 = projection_one2.get(["weight", "delay"], "list")

runtime=100
sim.run(runtime)

after_pro_one = projection_one.get(["weight", "delay"], "list")
after_pro_all = projection_all.get(["weight", "delay"], "list")
after_pro_all2 = projection_all_same.get(["weight", "delay"], "list")
after_pro_fp = projection_fp.get(["weight", "delay"], "list")
after_pro_one2 = projection_one2.get(["weight", "delay"], "list")

ioffset2 = pop2.get('i_offset')

print(ioffset2)

print(before_pro_one)
print(len(before_pro_one))
print(before_pro_all)
print(len(before_pro_all))
print(before_pro_all2)
print(len(before_pro_all2))
print(before_pro_fp)
print(len(before_pro_fp))
print(before_pro_one2)
print(len(before_pro_one2))

print(after_pro_one)
print(len(after_pro_one))
print(after_pro_all)
print(len(after_pro_all))
print(after_pro_all2)
print(len(after_pro_all2))
print(after_pro_fp)
print(len(after_pro_fp))
print(after_pro_one2)
print(len(after_pro_one2))

v = pop2.get_data('v')
gsyn_exc = pop2.get_data('gsyn_exc')
gsyn_inh = pop2.get_data('gsyn_inh')
spikes = pop2.get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    title="Testing projections on views",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

sim.end()