import spynnaker8 as sim
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import random

sim.setup(timestep=0.1)

n_neurons = 1

runtime = 1000

sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 22)
pop_lif = sim.Population(n_neurons, sim.IF_curr_exp(
    v_thresh=-55.0, tau_refrac=5.0, tau_m=10.0), label="lif")

times=[]
amplitudes=[]
zero_amplitudes=[]
n_steps = 50
for n_step in range(n_steps):
    times.append(10.0 + (n_step * 35))
    amplitudes.append(random.random())
    zero_amplitudes.append(0.0)

small_times = [0, 100, 300]
small_amplitudes = [0.2, 0.75, 0.3]

step_source = sim.StepCurrentSource(
    times=small_times, amplitudes=small_amplitudes)
# step_source.set_parameters(times=times, amplitudes=amplitudes)
pop_lif.inject(step_source)

pop_lif.record(["spikes", "v"])

sim.run(runtime)

times.append(1950.0)
amplitudes.append(0.9)

step_source.set_parameters(times=times, amplitudes=amplitudes)

# step_source2 = sim.StepCurrentSource(times=times, amplitudes=amplitudes)
# pop_lif.inject(step_source2)
#
# sim.reset()

sim.run(runtime)

lif_spikes = pop_lif.get_data('spikes')
lif_v = pop_lif.get_data('v')

print(lif_v.segments[0].filter(name='v')[0])
print(lif_v.segments[1].filter(name='v')[0])

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(lif_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime * 2)),
    Panel(lif_v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="membrane voltage (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime * 2)),
    Panel(lif_v.segments[1].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="membrane voltage (mV)",
          data_labels=[pop_lif.label], yticks=True, xlim=(0, runtime * 2)),
    title="Step Current Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()

sim.end()

