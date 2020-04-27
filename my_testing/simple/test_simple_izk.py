import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import quantities

sim.setup(timestep=1.0)
runtime = 500

spike_times = list(n for n in range(0, runtime, 100))
print(spike_times)
pop_src = sim.Population(1, sim.SpikeSourceArray(spike_times),
                         label="src")

cell_params_izk = {'a': 0.02,
                   'b': 0.2,
                   'c': -65,
                   'd': 8,
                   'v': -75,
                   'u': 0,
                   'tau_syn_E': 2,
                   'tau_syn_I': 2,
                   'i_offset': 0
                   }
pop_izh = sim.Population(1, sim.Izhikevich(**cell_params_izk), label="izh")

weight = 20
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

# run again with timestep 0.1

sim.setup(timestep=0.1)
runtime1 = 500

spike_times1 = list(n for n in range(0, runtime1, 100))
print(spike_times1)
pop_src1 = sim.Population(1, sim.SpikeSourceArray(spike_times1),
                         label="src1")

cell_params_izk1 = {'a': 0.02,
                    'b': 0.2,
                    'c': -65,
                    'd': 8,
                    'v': -75,
                    'u': 0,
                    'tau_syn_E': 2,
                    'tau_syn_I': 2,
                    'i_offset': 0
                    }
pop_izh1 = sim.Population(1, sim.Izhikevich(**cell_params_izk1), label="izh1")

weight1 = 20
delay1 = 5

# define the projection
proj1 = sim.Projection(pop_src1, pop_izh1, sim.OneToOneConnector(),
                       sim.StaticSynapse(weight=weight1, delay=delay1),
                       receptor_type="excitatory")

pop_izh1.record("all")
sim.run(runtime1)

print(proj1.get(["weight", "delay"], "list"))

spikes1 = pop_izh1.get_data('spikes')
v1 = pop_izh1.get_data('v')
gsyn_exc1 = pop_izh1.get_data('gsyn_exc')
gsyn_inh1 = pop_izh1.get_data('gsyn_inh')

plot_data = spikes1.segments[0].time_slice(50*quantities.ms, 250*quantities.ms)
# plot_v1_data = v1.segments[0].filter(name='v')[0].time_slice(50*quantities.ms, 250*quantities.ms)
plot_v1_data = v1.segments[0].filter(name='v')[0][50:250]
# plot_v1_data.annotations['channel_index'] = v1.segments[0].filter(name='v')[0].get_channel_index()

# plot_v1_data.channel_index = v1.segments[0].get_channel_index()

print(spikes.segments[0].spiketrains)
print(spikes1.segments[0].spiketrains)
print(plot_data)
print(v1)
print(v1.segments[0].filter(name='v')[0])
print(v1.segments[0].filter(name='v')[0].channel_index)
print(plot_v1_data)
# print(plot_v1_data.filter(name='v')[0])
print(plot_v1_data.channel_index)

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
#     Panel(spikes1.segments[0].spiketrains,
    Panel(plot_data.spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime1)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop_izh.label], yticks=True, xlim=(0, runtime)),
    Panel(plot_v1_data,
          ylabel="Membrane potential (mV)",
          data_labels=[pop_izh1.label], yticks=True, xlim=(0, runtime1)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_izh.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc1.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop_izh1.label], yticks=True, xlim=(0, runtime1)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_izh.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh1.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_izh1.label], yticks=True, xlim=(0, runtime1)),
    title="Single-neuron Izhikevich example (1.0 vs 0.1)",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

sim.end()
