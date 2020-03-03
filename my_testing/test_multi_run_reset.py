import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)  #, min_delay=1.0, max_delay=144.0)

runtime = 500

inp = sim.Population(2, sim.SpikeSourceArray(spike_times=([5,200],[15,210])),
                     label='input')
out = sim.Population(2, sim.IF_curr_exp(), label='test')

weight = 5.0
delay = 105
# delay = sim.RandomDistribution('uniform', [6,14])

static_synapse = sim.StaticSynapse(weight=weight, delay=delay)

proj = sim.Projection(inp, out, sim.OneToOneConnector(), static_synapse)

inp.record(["spikes"])
out.record(["v", "spikes"])

sim.run(runtime/2)

weightsdelays1 = proj.get(['weight', 'delay'], 'list')

sim.reset()

print('delay after reset: ', static_synapse.delay)

# out2 = sim.Population(1, sim.IF_curr_exp(), label='out2')

# out.set(v_thresh=-58.0)

sim.run(runtime/2)

weightsdelays2 = proj.get(['weight', 'delay'], 'list')

spikes_in = inp.get_data("spikes")
v1 = out.get_data("v")
spikes1 = out.get_data("spikes")

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v1.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="Membrane potential (mV)",
          data_labels=[out.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes1.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=1.5, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes_in.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=1.5, xlim=(0, runtime)),
    # plots of the second segment
    Panel(v1.segments[1].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="Membrane potential (mV)",
          data_labels=[out.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes1.segments[1].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=1.5, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(spikes_in.segments[1].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=1.5, xlim=(0, runtime)),
    title="testing spike after reset",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

print(v1.segments[0].filter(name='v')[0])
print(v1.segments[1].filter(name='v')[0])
print(weightsdelays1)
print(weightsdelays2)

sim.end()
