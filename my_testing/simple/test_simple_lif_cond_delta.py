import spynnaker8 as sim
from pyNN.random import RandomDistribution
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
runtime = 500
n_neurons = 10

spike_times = list(n for n in range(0, runtime, 100))
print(spike_times)
pop_src = sim.Population(1, sim.SpikeSourceArray(spike_times),
                         label="src")

pop_lif_cond_delta = sim.Population(1, sim.extra_models.IF_cond_delta(),
                                    label="lif_cond_delta")
pop_lif_curr_delta = sim.Population(1, sim.IF_curr_delta(),
                                    label="lif_curr_delta")

weight_cond = 0.01
weight_curr = 1.0
delay = 10.0

# define the projection
proj = sim.Projection(pop_src, pop_lif_cond_delta, sim.AllToAllConnector(),
                      sim.StaticSynapse(weight=weight_cond, delay=delay),
                      receptor_type="excitatory")
proj2 = sim.Projection(pop_src, pop_lif_curr_delta, sim.AllToAllConnector(),
                       sim.StaticSynapse(weight=weight_curr, delay=delay),
                       receptor_type="excitatory")

pop_lif_cond_delta.record("all")
pop_lif_curr_delta.record("all")
sim.run(runtime)

print("connections for projection: ", proj.get(["weight", "delay"], "list"))
print("connections for projection2: ", proj2.get(["weight", "delay"], "list"))

spikes_cond = pop_lif_cond_delta.get_data('spikes')
v_cond = pop_lif_cond_delta.get_data('v')
gsyn_exc_cond = pop_lif_cond_delta.get_data('gsyn_exc')
gsyn_inh_cond = pop_lif_cond_delta.get_data('gsyn_inh')

spikes_curr = pop_lif_curr_delta.get_data('spikes')
v_curr = pop_lif_curr_delta.get_data('v')
gsyn_exc_curr = pop_lif_curr_delta.get_data('gsyn_exc')
gsyn_inh_curr = pop_lif_curr_delta.get_data('gsyn_inh')

sim.end()

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes_curr.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(spikes_cond.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v_curr.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif_curr_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(v_cond.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif_cond_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc_curr.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif_curr_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc_cond.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif_cond_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh_curr.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif_curr_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh_cond.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif_cond_delta.label], yticks=True, xlim=(0, runtime)),
    title="IF_cond_delta testing vs IF_curr_delta",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()
