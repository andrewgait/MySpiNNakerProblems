import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
runtime = 1000
runtime1 = 2000

spike_times = list(n for n in range(0, runtime+runtime1, 100))
print(spike_times)
pop_src = sim.Population(1, sim.SpikeSourceArray(spike_times),
                         label="src")

pop_layer = sim.Population(1, sim.IF_curr_exp(), label="layer")

# add another pop
pop_output = sim.Population(1, sim.IF_curr_exp(), label="lif")

weight = 5.0
delay = 2

# define projection, src to layer
proj1 = sim.Projection(pop_src, pop_layer, sim.AllToAllConnector(),
                       sim.StaticSynapse(weight=weight, delay=delay),
                       receptor_type="excitatory")

weight2 = 4.1
delay2 = 10

sim.run(runtime)

# add projection between layer and output
proj2 = sim.Projection(pop_layer, pop_output, sim.AllToAllConnector(),
                       sim.StaticSynapse(weight=weight2, delay=delay2),
                       receptor_type="excitatory")

# a reset is required
sim.reset()

sim.run(runtime1)

print(proj1.get(["weight", "delay"], "list"))
print(proj2.get(["weight", "delay"], "list"))

# spikes = pop_lif.get_data('spikes')
# v = pop_lif.get_data('v')
# gsyn_exc = pop_lif.get_data('gsyn_exc')
# gsyn_inh = pop_lif.get_data('gsyn_inh')
#
# spikes_layer = pop_layer.get_data('spikes')
# v_layer = pop_layer.get_data('v')
# gsyn_exc_layer = pop_layer.get_data('gsyn_exc')
# gsyn_inh_layer = pop_layer.get_data('gsyn_inh')
#
# Figure(
#     # raster plot of the postsynaptic neuron spike times
#     Panel(spikes.segments[0].spiketrains,
#           yticks=True, markersize=0.75, xlim=(0, runtime+runtime1)),
#     Panel(spikes_layer.segments[0].spiketrains,
#           yticks=True, markersize=0.75, xlim=(0, runtime+runtime1)),
#     # membrane potential of the postsynaptic neuron
#     Panel(v.segments[0].filter(name='v')[0],
#           ylabel="Membrane potential (mV)",
#           data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime+runtime1)),
#     Panel(v_layer.segments[0].filter(name='v')[0],
#           ylabel="Membrane potential (mV)",
#           data_labels=[pop_layer.label], yticks=True,
#           xlim=(0, runtime+runtime1)),
#     Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
#           ylabel="gsyn excitatory (mV)",
#           data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime+runtime1)),
#     Panel(gsyn_exc_layer.segments[0].filter(name='gsyn_exc')[0],
#           ylabel="gsyn excitatory (mV)",
#           data_labels=[pop_layer.label], yticks=True,
#           xlim=(0, runtime+runtime1)),
#     Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
#           ylabel="gsyn inhibitory (mV)",
#           data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime+runtime1)),
#     Panel(gsyn_inh_layer.segments[0].filter(name='gsyn_inh')[0],
#           xlabel="Time (ms)", xticks=True,
#           ylabel="gsyn inhibitory (mV)",
#           data_labels=[pop_layer.label], yticks=True, xlim=(0, runtime+runtime1)),
#     title="Single-neuron LIF example, two layers",
#     annotations="Simulated with {}".format(sim.name())
# )
# plt.show()

sim.end()
