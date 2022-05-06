import pyNN.spiNNaker as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)

runtime = 500

spike_times = list(n for n in range(0, runtime, 100))
print(spike_times)
pop_src = sim.Population(1, sim.SpikeSourceArray(spike_times),
                         label="src")

cell_params_lif = {
                   'i_offset': 0
                   }
pop_lif = sim.Population(1, sim.IF_curr_exp(**cell_params_lif), label="lif")

weight = 2
delay = 5

# define the projection
proj = sim.Projection(pop_src, pop_lif, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=weight, delay=delay),
                      receptor_type="excitatory")

weight_inh = 1
delay_inh = 10

proj = sim.Projection(pop_src, pop_lif, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=weight_inh, delay=delay_inh),
                      receptor_type="inhibitory")


pop_lif.record("all")
sim.run(runtime)

# print(proj.get(["weight", "delay"], "list"))

spikes = pop_lif.get_data('spikes')
v = pop_lif.get_data('v')
gsyn_exc = pop_lif.get_data('gsyn_exc')
gsyn_inh = pop_lif.get_data('gsyn_inh')

sim.end()

print(spikes.segments[0].spiketrains)

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    title="Single-neuron LIF example with exc and inh",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()
