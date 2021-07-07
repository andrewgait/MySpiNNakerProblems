import spynnaker8 as sim
import random
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

sim.setup(timestep=0.1,min_delay=0.1,max_delay=14.4)
sim.set_number_of_neurons_per_core(sim.IF_cond_exp, 20)

runtime = 500

initial_values=-70.0
pop = sim.Population(
    19, sim.IF_cond_exp(v_thresh=-57.0, v_rest=-70.0, v_reset=-70.0,
                        tau_refrac=2.0, tau_m=10.0, cm=0.29, e_rev_E=0.0,
                        e_rev_I=75.0, tau_syn_E=1.5, tau_syn_I=10.0),
    initial_values=initial_values, label="X_ON")

for i, lgn_cell in enumerate(pop.all_cells):
    offset = i * 0.1 + 0.1
    for j in range(300):
        times[j] = offset + j * 0.1
        amplitudes = random.random()

    print("times: ", times)
    print("amplitudes: ", amplitudes)
    scs = sim.StepCurrentSource(times=t, amplitudes=a)
    lgn_cell.inject(scs)

ncs = sim.NoisyCurrentSource(mean=0.0, stdev=1.7, dt=0.1)
pop.inject(ncs)

pop.record("all")
sim.run(runtime)

# print(proj.get(["weight", "delay"], "list"))

spikes = pop.get_data('spikes')
v = pop.get_data('v')

# print(pps)
# print(pps.segments[0].filter(name='v'))

Figure(
    # raster plot of the postsynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.75, xlim=(0, runtime)),
    Panel(v.segments[0].filter(name='v')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="gsyn inhibitory (mV)",
          data_labels=[pop.label], yticks=True, xlim=(0, runtime)),
    title="Noisy Current Source testing",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()
plt.savefig("CStest_noisy_step.png")

sim.end()

