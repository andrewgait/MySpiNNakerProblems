import pyNN.spiNNaker as sim
from pyNN.random import RandomDistribution
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
runtime = 100
n_neurons = 4

spike_times = list(n for n in range(0, runtime, 5))
print(spike_times)
pop_src = sim.Population(n_neurons, sim.SpikeSourceArray(spike_times),
                         label="src")

test = sim.RandomDistribution('uniform_int', [1, 5])
# test = 3

cell_params_lif = {
    'v_rest': -70, 'i_offset': test
                   }
pop_lif = sim.Population(n_neurons, sim.IF_curr_exp(**cell_params_lif),
                         label="lif")

# weight = sim.RandomDistribution('normal', [2.0, 1.0])
# weight = sim.RandomDistribution('poisson', lambda_=3.0)
weight = sim.RandomDistribution('uniform', (0.05, 50.5))
delay = sim.RandomDistribution('uniform', (3.0, 10.0))

# define the projection
proj = sim.Projection(pop_src, pop_lif, sim.AllToAllConnector(),
                      sim.StaticSynapse(weight=weight, delay=delay),
                      receptor_type="excitatory")

pop_lif.record("all")
sim.run(runtime)

print("connections for projection: ", proj.get(["weight", "delay"], "list"))

spikes = pop_lif.get_data('spikes')
v = pop_lif.get_data('v')
gsyn_exc = pop_lif.get_data('gsyn_exc')
gsyn_inh = pop_lif.get_data('gsyn_inh')

sim.end()

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
    title="LIF testing, different distributions",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()
