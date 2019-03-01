import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(1.0)

spikeArray = {'spike_times': [[2, 15]]}
in_pop = sim.Population(1, sim.SpikeSourceArray(**spikeArray), label="input")
rec_pop = sim.Population(1, sim.IF_curr_exp(), label="pop")
proj = sim.Projection(in_pop, rec_pop, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=5.0, delay=1))

in_pop.record(["spikes"])
rec_pop.record(["v", "spikes"])

loopruns = 3
runtime = 10
spike_in = list()
spike_rec = list()
for n in range(loopruns):
    sim.run(runtime)
    in_pop.set(spike_times=[[22]])
    spike_in.append(in_pop.spinnaker_get_data('spikes'))
    spike_rec.append(rec_pop.spinnaker_get_data('spikes'))

srec = rec_pop.get_data('spikes')
vrec = rec_pop.get_data('v')

sim.end()

print(spike_in)
print(spike_rec)

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(srec.segments[0].spiketrains,
          yticks=True, markersize=1.0, xlim=(0, loopruns*runtime)),
    # membrane potential of the postsynaptic neuron
    Panel(vrec.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="Membrane potential (mV)",
          data_labels=[rec_pop.label], yticks=True, xlim=(0, loopruns*runtime)),
    title="Simple ssa example",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()