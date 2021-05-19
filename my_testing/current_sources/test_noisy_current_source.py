import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=0.1)
runtime = 500

pop_lif = sim.Population(4, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")

noisy_source = sim.NoisyCurrentSource(
    mean=0.5, stdev=0.2, start=50.0, stop=450.0, dt=0.1)
# noisy_source2 = sim.NoisyCurrentSource(
#     mean=1.5, stdev=1.0, start=150.0, stop=480.0, dt=0.1)

# pop_lif[1,2].inject(noisy_source2)
pop_lif[0,3].inject(noisy_source)

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
    title="Noisy Current Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

