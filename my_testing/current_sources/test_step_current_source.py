import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=0.1)
runtime = 250

pop_lif = sim.Population(4, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")
pop_lif2 = sim.Population(4, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")

step_source = sim.StepCurrentSource(times=[50.0, 110.0, 150.0, 210.0],
                                    amplitudes=[0.4, 0.6, -0.2, 0.2])
# step_source2 = sim.StepCurrentSource(times=[20.0, 130.0, 160.0, 200.0, 220.0],
#                                     amplitudes=[1.4, 1.6, -1.2, 1.2, 0.8])

pop_lif[1,3].inject(step_source)
# pop_lif[2].inject(step_source2)

pop_lif.record("all")
pop_lif2.record("all")
# sim.run(runtime)

sim.run(50)
pop_lif2.set(i_offset=0.4)
sim.run(60)
pop_lif2.set(i_offset=0.6)
sim.run(40)
pop_lif2.set(i_offset=-0.2)
sim.run(60)
pop_lif2.set(i_offset=0.2)
sim.run(40)

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
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    Panel(lif2_v.segments[0].filter(name='v')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop_lif2.label], yticks=True, xlim=(0, runtime)),
    title="Step Current Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

