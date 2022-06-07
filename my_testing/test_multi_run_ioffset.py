import pyNN.spiNNaker as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)  #, min_delay=1.0, max_delay=144.0)

run1 = 50
run2 = 60
run3 = 40
run4 = 60
run5 = 40
runtime = run1 + run2 + run3 + run4 + run5
inp = sim.Population(2, sim.SpikeSourceArray,
                     {'spike_times': [10,20]}, label='input')
pop = sim.Population(2, sim.IF_curr_exp(), label='test',
                     additional_parameters={"min_weights": [0.3, 0.2],
                                            "weight_random_sigma": 3,
                                            "max_stdp_spike_delta": 30})

proj = sim.Projection(inp, pop, sim.AllToAllConnector(),
                      sim.StaticSynapse(weight=1.25, delay=4),
                      label='input to pop')

pop.record(["v", "spikes"])

# ioffset starts at zero
sim.run(run1)

pop.set(i_offset=0.4)
sim.run(run2)

pop.set(i_offset=0.6)
sim.run(run3)

pop.set(i_offset=-0.2)
sim.run(run4)

pop.set(i_offset=0.2)
sim.run(run5)

v1 = pop.get_data("v")
spikes1 = pop.get_data("spikes")

print(v1)
print(spikes1)

Figure(
    # membrane potential of the postsynaptic neuron
    Panel(v1.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="Membrane potential (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, runtime)),
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes1.segments[0].spiketrains,
          xlabel="Time (ms)", xticks=True,
          yticks=True, markersize=1.5, xlim=(0, runtime)),
    title="testing ioffset in multi-run as StepCurrentSource",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()
