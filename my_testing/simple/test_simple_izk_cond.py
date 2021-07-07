import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import quantities

sim.setup(timestep=1.0)
runtime = 500

spike_times = list(n for n in range(0, runtime, 100))
print(spike_times)
pop_1 = sim.Population(25, sim.IF_curr_exp, label="if_curr")
pop_src = sim.Population(25, sim.SpikeSourceArray(spike_times),
                         label="src")

pop_izh = sim.Population(16, sim.extra_models.Izhikevich_cond, label="izh_cond")

weight = 5
delay = 5

# define the projection
proj = sim.Projection(pop_src, pop_izh, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=weight, delay=delay),
                      receptor_type="excitatory")

pop_izh.record("all")
sim.run(runtime)

print(proj.get(["weight", "delay"], "list"))

spikes = pop_izh.get_data('spikes')
v = pop_izh.get_data('v')
gsyn_exc = pop_izh.get_data('gsyn_exc')
gsyn_inh = pop_izh.get_data('gsyn_inh')

sim.end()

print(spikes.segments[0].spiketrains)
print(v)
print(v.segments[0].filter(name='v')[0])

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_izh.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_izh.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_izh.label], yticks=True, xlim=(0, runtime)),
    title="Single-neuron Izhikevich_cond example (ts=1.0)",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

print(v.name, v.segments[0].name, v.segments[0].filter(name='v')[0].name)
print(gsyn_exc.name, gsyn_exc.segments[0].filter(name='gsyn_exc')[0].name)
print(gsyn_exc.segments[0].filter(name='gsyn_exc')[0].annotations)
print(gsyn_inh.segments[0].filter(name='gsyn_inh')[0].annotations)
print(gsyn_inh.name)
