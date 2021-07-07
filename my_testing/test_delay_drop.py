import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

n_neurons = 75 # 75 works 76 fails
runtime = 12000
sim.setup(timestep=1.0)

pop_1 = sim.Population(n_neurons, sim.IF_curr_exp(), label="pop_1")
input1 = sim.Population(
    n_neurons, sim.SpikeSourceArray(spike_times=range(0, runtime, 100)),
    label="input")
input2 = sim.Population(
    n_neurons, sim.SpikeSourceArray(spike_times=range(0, runtime, 100)),
    label="input")
input3 = sim.Population(
    n_neurons, sim.SpikeSourceArray(spike_times=range(0, runtime, 100)),
    label="input")
input4 = sim.Population(
    n_neurons, sim.SpikeSourceArray(spike_times=range(0, runtime, 100)),
    label="input")
input5 = sim.Population(
    n_neurons, sim.SpikeSourceArray(spike_times=range(0, runtime, 100)),
    label="input")

sim.Projection(
    input1, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5.0, delay=1))
sim.Projection(
    input2, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5.0, delay=20))
sim.Projection(
    input3, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5.0, delay=40))
sim.Projection(
    input4, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5.0, delay=60))
sim.Projection(
    input5, pop_1, sim.OneToOneConnector(),
    synapse_type=sim.StaticSynapse(weight=5.0, delay=80))

pop_1.record(["spikes", "v"])
sim.run(runtime)

spikes = pop_1.spinnaker_get_data("spikes")

lif_spikes = pop_1.get_data('spikes')
lif_v = pop_1.get_data('v')

sim.end()
print(len(spikes))
print(10 * 5 * n_neurons)

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(lif_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(lif_v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="membrane voltage (mV)",
          data_labels=[pop_1.label], yticks=True, xlim=(0, runtime)),
    title="delay dropped packets testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()
