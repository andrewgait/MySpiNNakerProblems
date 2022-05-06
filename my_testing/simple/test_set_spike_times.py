import pyNN.spiNNaker as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

p.setup(1.0)

runtime = 100

pop = p.Population(10, p.SpikeSourceArray([]))
pop[1].set_parameters(spike_times=[5])

pop_out = p.Population(10, p.IF_curr_exp(), label='out')

p.Projection(pop, pop_out, p.OneToOneConnector(),
             p.StaticSynapse(weight=5.0, delay=1))

pop_out.record("all")

p.run(runtime)

lif_spikes = pop_out.get_data('spikes')
lif_v = pop_out.get_data('v')

p.end()

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(lif_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(lif_v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="membrane voltage (mV)",
          data_labels=[pop_out.label], yticks=True, xlim=(0, runtime)),
    title="set spike times testing",
    annotations="Simulated with {}".format(p.name())
)

plt.show()
