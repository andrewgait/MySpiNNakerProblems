import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
runtime = 500

spike_times = list(n for n in range(0, runtime, 100))
print(spike_times)
pop_src = sim.Population(10, sim.SpikeSourceArray(spike_times),
                         label="src")

cell_params_lif = {
                   'i_offset': 0
                   }
pop_lif = sim.Population(10, sim.IF_curr_exp(**cell_params_lif), label="lif")

weight = 5
delay = 5

# define the projection
proj = sim.Projection(pop_src, pop_lif, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=weight, delay=delay),
                      receptor_type="excitatory")

pop_lif.record("all")
sim.run(runtime)

# print(proj.get(["weight", "delay"], "list"))

spikes = pop_lif.get_data('spikes')
v = pop_lif.get_data('v')
gsyn_exc = pop_lif.get_data('gsyn_exc')
gsyn_inh = pop_lif.get_data('gsyn_inh')
pps = pop_lif.get_data('packets-per-timestep')

print(pps)
print(pps.segments[0].filter(name='packets-per-timestep'))

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
    title="LIF example (1.0)",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

