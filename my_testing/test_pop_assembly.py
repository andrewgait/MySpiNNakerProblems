import pyNN.spiNNaker as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sources = 10
destinations = 10

sim.setup(timestep=1.0)
# sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 200)
# sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 200)

pop1 = sim.Population(sources, sim.SpikeSourceArray(spike_times=[10,50]),
                      label="input")
pop2 = sim.Population(destinations, sim.IF_curr_exp(),
                      label="pop2")
pop3 = sim.Population(destinations, sim.IF_cond_exp(),
                      label="pop2")
synapse_type12 = sim.StaticSynapse(weight=5.5, delay=2)
synapse_type13 = sim.StaticSynapse(weight=0.1, delay=10)

assemble = sim.Assembly(pop2, pop3)

assemble2 = pop2 + pop3

assemble.set(i_offset=0.1)

connector1 = sim.OneToOneConnector()
connector2 = sim.AllToAllConnector()
projection12 = sim.Projection(pop1, pop2, connector1,
                              synapse_type=synapse_type12)
projection13 = sim.Projection(pop1, pop3, connector2,
                              synapse_type=synapse_type13)

pop2.record('all')
pop3.record('all')

before_pro12 = projection12.get(["weight", "delay"], "list")
before_pro13 = projection13.get(["weight", "delay"], "list")
print('projection.get was called before run')
runtime=100
sim.run(runtime)
after_pro12 = projection12.get(["weight", "delay"], "list")
after_pro13 = projection13.get(["weight", "delay"], "list")

ioffset2 = pop2.get('i_offset')
ioffset3 = pop3.get('i_offset')

print(ioffset2)
print(ioffset3)

print(before_pro12)
print(len(before_pro12))
print(after_pro12)
print(len(after_pro12))
print(before_pro13)
print(len(before_pro13))
print(after_pro13)
print(len(after_pro13))

v2 = pop2.get_data('v')
gsyn_exc2 = pop2.get_data('gsyn_exc')
gsyn_inh2 = pop2.get_data('gsyn_inh')
spikes2 = pop2.get_data('spikes')
v3 = pop3.get_data('v')
gsyn_exc3 = pop3.get_data('gsyn_exc')
gsyn_inh3 = pop3.get_data('gsyn_inh')
spikes3 = pop3.get_data('spikes')

spikes_assemble = assemble.get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes2.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v2.segments[0].filter(name='v')[0],
          ylabel="Membrane potential pop2 (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes3.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v3.segments[0].filter(name='v')[0],
          ylabel="Membrane potential pop3 (mV)",
          data_labels=[pop3.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes_assemble.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime)),
    title="Testing population assemblies",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

sim.end()