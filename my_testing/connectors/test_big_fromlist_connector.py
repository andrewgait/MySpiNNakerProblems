import random
import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

# this is a copy of the test_big_connection unit test; trying to work out
# what's different for this case when using weight_scale branch

sources = 300
destinations = 300
aslist = []
spiketimes = []
for s in range(sources):
    for d in range(destinations):
        aslist.append(
            (s, d, 5 + random.random(), random.randint(1, 5)))
    spiketimes.append([s * 20])

sim.setup(1.0)
pop1 = sim.Population(
    sources, sim.SpikeSourceArray(spike_times=spiketimes),
    label="input")
pop2 = sim.Population(destinations, sim.IF_curr_exp(), label="pop2")
synapse_type = sim.StaticSynapse(weight=5, delay=2)
projection = sim.Projection(
    pop1, pop2, sim.FromListConnector(aslist),
    synapse_type=synapse_type)
pop2.record("spikes")
pop2.record("v")
runtime = sources * 20
sim.run(runtime)

pop2_spikes = pop2.get_data("spikes")
pop2_v = pop2.get_data("v")

# Plot
Figure(
    # membrane potential of the postsynaptic neuron
    Panel(pop2_v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the presynaptic neuron spike times
    Panel(pop2_spikes.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=0.5, xlim=(0, runtime)),
    title="big fromlist connector",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()