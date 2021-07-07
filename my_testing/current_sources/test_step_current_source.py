import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import random

sim.setup(timestep=0.1)

n_neurons = 200

runtime = 400 + n_neurons

sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 22)
pop_lif = sim.Population(n_neurons, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")
# pop_lif2 = sim.Population(n_neurons, sim.IF_curr_exp(
#     v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")

n_steps = 286
for n in range(n_neurons):
    times=[]
    amplitudes=[]
    for n_step in range(n_steps):
        times.append(50.0 + n_step + n)
        amplitudes.append(random.random())

    step_source = sim.StepCurrentSource(times=times, amplitudes=amplitudes)
    pop_lif[n].inject(step_source)

pop_lif.inject(sim.NoisyCurrentSource(
    mean=0.5, stdev=0.2, start=50.0, stop=450.0, dt=0.1))

# step_source2 = sim.StepCurrentSource(times=[20.0, 130.0, 160.0, 200.0, 220.0],
#                                     amplitudes=[0.7, 1.0, -1.2, 0.7, 0.8])

# step_source.set_parameters(times=[150.0, 180.0, 200.0, 220.0],
#                            amplitudes=[0.1, -0.5, 0.8, 0.3])

# pop_lif.inject(step_source)
# pop_lif[3].inject(step_source2)

pop_lif.record(["spikes", "v"])
# pop_lif2.record(["spikes", "v"])
sim.run(runtime)

# sim.run(50)
# pop_lif2.set(i_offset=0.4)
# sim.run(60)
# pop_lif2.set(i_offset=0.6)
# sim.run(40)
# pop_lif2.set(i_offset=-0.2)
# sim.run(60)
# pop_lif2.set(i_offset=0.2)
# sim.run(7290)

# print(proj.get(["weight", "delay"], "list"))

lif_spikes = pop_lif.get_data('spikes')
lif_v = pop_lif.get_data('v')

# lif2_spikes = pop_lif2.get_data('spikes')
# lif2_v = pop_lif2.get_data('v')

# print(pps)
# print(pps.segments[0].filter(name='v'))

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(lif_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    # Panel(lif2_spikes.segments[0].spiketrains,
    #       yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(lif_v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="membrane voltage (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime)),
    # Panel(lif2_v.segments[0].filter(name='v')[0],
    #       xlabel="Time (ms)", xticks=True,
    #       ylabel="membrane voltage (mV)",
    #       data_labels=[pop_lif2.label], yticks=True, xlim=(0, runtime)),
    title="Step Current Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

