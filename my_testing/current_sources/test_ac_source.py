import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=1.0)
runtime = 500

pop_lif = sim.Population(4, sim.IF_curr_exp(
    v_thresh=-50.0, tau_m=10.0), label="lif")

ac_source = sim.ACSource(start=50.0, stop=450.0, amplitude=1.0, offset=1.0,
                         frequency=10.0, phase=180.0)

# ac_source2 = sim.ACSource(start=150.0, stop=250.0, amplitude=1.5, offset=0.5,
#                          frequency=50.0, phase=90.0)

# pop_lif.inject(ac_source)
ac_source.inject_into(pop_lif[1])
# ac_source2.inject_into(pop_lif[2,3])

pop_lif.record("all")
sim.run(runtime)

# print(proj.get(["weight", "delay"], "list"))

lif_spikes = pop_lif.get_data('spikes')
lif_v = pop_lif.get_data('v')

# print(pps)
# print(pps.segments[0].filter(name='v'))

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(lif_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(lif_v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    title="AC Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

