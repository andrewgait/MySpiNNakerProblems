import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=0.1)
runtime = 100

sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)

pop_lif = sim.Population(10, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")
pop_lif2 = sim.Population(10, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif2")

dc_source = sim.DCSource(amplitude=0.5, start=20.0, stop=80.0)
# dc_source2 = sim.DCSource(amplitude=1.5, start=40.0, stop=90.0)

pop_lif[3,7].inject(dc_source)
# pop_lif[2,6].inject(dc_source2)

pop_lif.record("all")
pop_lif2.record("all")
# sim.run(runtime)

sim.run(20)
pop_lif2.set(i_offset=0.5)
sim.run(60)
pop_lif2.set(i_offset=0.0)
sim.run(20)


# print(proj.get(["weight", "delay"], "list"))

lif_spikes = pop_lif.get_data('spikes')
lif_v = pop_lif.get_data('v')

lif2_spikes = pop_lif2.get_data('spikes')
lif2_v = pop_lif2.get_data('v')

# print(pps)
# print(pps.segments[0].filter(name='v'))

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(lif_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(lif2_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(lif_v.segments[0].filter(name='v')[0],
          ylabel="membrane voltage (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    Panel(lif2_v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="membrane voltage (mV)",
          data_labels=[pop_lif2.label], yticks=True, xlim=(0, runtime)),
    title="DC Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

