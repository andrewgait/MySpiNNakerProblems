import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
runtime = 500

spike_times = list(n for n in range(0, runtime, 200))
spike_times2 = list(n for n in range(100, runtime, 200))
print(spike_times)
pop_src = sim.Population(1, sim.SpikeSourceArray(spike_times),
                         label="src")
pop_src2 = sim.Population(1, sim.SpikeSourceArray(spike_times2),
                          label="src2")

cell_params_lif = {
                   'i_offset': 0,
#                   'v_thresh': -60
                   }
pop_lif_delta = sim.Population(
    1, sim.IF_curr_delta(**cell_params_lif), label="lif_delta")
#     1, sim.extra_models.IFCurDelta(**cell_params_lif), label="lif_delta")

weight = 2
weight2 = 1
delay = 5

# define the projection
proj = sim.Projection(pop_src, pop_lif_delta, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=weight, delay=delay),
                      receptor_type="excitatory")
proj_inh = sim.Projection(pop_src2, pop_lif_delta, sim.OneToOneConnector(),
                          sim.StaticSynapse(weight=weight2, delay=delay),
                          receptor_type="inhibitory")

pop_lif_delta.record("all")
sim.run(runtime)

# print(proj.get(["weight", "delay"], "list"))

spikes = pop_lif_delta.get_data('spikes')
v = pop_lif_delta.get_data('v')
gsyn_exc = pop_lif_delta.get_data('gsyn_exc')
gsyn_inh = pop_lif_delta.get_data('gsyn_inh')

sim.end()

# run again with timestep 0.1

sim.setup(timestep=0.1)
runtime1 = 500

spike_times1 = list(n for n in range(0, runtime1, 200))
spike_times12 = list(n for n in range(100, runtime1, 200))
print(spike_times1)
pop_src1 = sim.Population(1, sim.SpikeSourceArray(spike_times1),
                         label="src1")
pop_src12 = sim.Population(1, sim.SpikeSourceArray(spike_times12),
                           label="src12")

cell_params_lif1 = {
                    'i_offset': 0,
#                    'v_thresh': -60
                    }
pop_lif_delta1 = sim.Population(
    1, sim.IF_curr_delta(**cell_params_lif1), label="lif_delta1")
#     1, sim.extra_models.IFCurDelta(**cell_params_lif1), label="lif_delta1")

weight1 = 2
weight12 = 1
delay1 = 5

# define the projection
proj1 = sim.Projection(pop_src1, pop_lif_delta1, sim.OneToOneConnector(),
                       sim.StaticSynapse(weight=weight1, delay=delay1),
                       receptor_type="excitatory")
proj1_inh = sim.Projection(pop_src12, pop_lif_delta1, sim.OneToOneConnector(),
                           sim.StaticSynapse(weight=weight12, delay=delay1),
                           receptor_type="inhibitory")

pop_lif_delta1.record("all")
sim.run(runtime1)

# print(proj1.get(["weight", "delay"], "list"))

spikes1 = pop_lif_delta1.get_data('spikes')
v1 = pop_lif_delta1.get_data('v')
gsyn_exc1 = pop_lif_delta1.get_data('gsyn_exc')
gsyn_inh1 = pop_lif_delta1.get_data('gsyn_inh')

print(spikes.segments[0].spiketrains)
print(spikes1.segments[0].spiketrains)

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(spikes1.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime1)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(v1.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_lif_delta1.label], yticks=True, xlim=(0, runtime1)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc1.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_lif_delta1.label], yticks=True, xlim=(0, runtime1)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif_delta.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh1.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif_delta1.label], yticks=True, xlim=(0, runtime1)),
    title="Single-neuron LIF delta example (1.0 vs 0.1)",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

sim.end()
