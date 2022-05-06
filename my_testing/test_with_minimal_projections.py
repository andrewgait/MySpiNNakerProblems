import pyNN.spiNNaker as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sources = 180
destinations = 249

sim.setup(timestep=1.0)
# sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 200)
# sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 200)

pop1 = sim.Population(sources, sim.SpikeSourceArray(spike_times=[100]),
                      label="input")
pop2 = sim.Population(destinations, sim.IF_curr_exp(),
                      label="pop2")

fromlistconnector = sim.FromListConnector([(10,10),(20,20),(110,240)])

proj = sim.Projection(pop1, pop2, fromlistconnector,
                      sim.StaticSynapse(weight=2.0, delay=2))

pop2.record('all')

runtime=1000
sim.run(runtime)

proj_list = proj.get(["weight", "delay"], "list")

print(proj_list, len(proj_list))

ioffset2 = pop2.get('i_offset')

print(ioffset2)

v = pop2.get_data('v')
gsyn_exc = pop2.get_data('gsyn_exc')
gsyn_inh = pop2.get_data('gsyn_inh')
spikes = pop2.get_data('spikes')

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    title="Testing projections on views",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

sim.end()