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

pop_lif = sim.Population(1, sim.IF_cond_alpha(), label="lif_cond_alpha")
pop_lif_exp = sim.Population(1, sim.IF_cond_exp(), label="lif_cond_exp")

weight = 0.05  #sim.RandomDistribution('uniform', [2.0, 5.0])
delay = 10.0  #sim.RandomDistribution('uniform', (3.0, 10.0))

# define the projection
proj = sim.Projection(pop_src, pop_lif, sim.AllToAllConnector(),
                      sim.StaticSynapse(weight=weight, delay=delay),
                      receptor_type="excitatory")
proj2 = sim.Projection(pop_src, pop_lif_exp, sim.AllToAllConnector(),
                       sim.StaticSynapse(weight=weight, delay=delay),
                       receptor_type="excitatory")

pop_lif.record("all")
pop_lif_exp.record("all")
sim.run(runtime)

print("connections for projection: ", proj.get(["weight", "delay"], "list"))
print("connections for projection2: ", proj2.get(["weight", "delay"], "list"))

spikes = pop_lif.get_data('spikes')
v = pop_lif.get_data('v')
gsyn_exc = pop_lif.get_data('gsyn_exc')
gsyn_inh = pop_lif.get_data('gsyn_inh')

spikes_exp = pop_lif_exp.get_data('spikes')
v_exp = pop_lif_exp.get_data('v')
gsyn_exc_exp = pop_lif_exp.get_data('gsyn_exc')
gsyn_inh_exp = pop_lif_exp.get_data('gsyn_inh')

sim.end()

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes_exp.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v_exp.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif_exp.label], yticks=True, xlim=(0, runtime)),
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc_exp.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif_exp.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh_exp.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif_exp.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    title="IF_cond_alpha testing vs IF_cond_exp",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()
