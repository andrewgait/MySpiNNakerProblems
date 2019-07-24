from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import spynnaker8 as p

p.setup(timestep=1)

p.set_number_of_neurons_per_core(p.IF_cond_exp, 100)

# cell_params_lif_cond = {'cm': 0.25,
#                         'i_offset': 0.0,
#                         'tau_m': 20.0,
#                         'tau_refrac': 5.0,
#                         'tau_syn_E': 5.0,
#                         'tau_syn_I': 5.0,
#                         'v_reset': -70.0,
#                         'v_rest': -65.0,
#                         'v_thresh': -50.0,
#                         'e_rev_E': 0.,
#                         'e_rev_I': -80.
#                         }

cell_params_lif_curr = {'cm': 0.25,
                        'i_offset': 0.0,
                        'tau_m': 20.0,
                        'tau_refrac': 10.0,
                        'tau_syn_E': 5.0,
                        'tau_syn_I': 5.0,
                        'v_reset': -70.0,
                        'v_rest': -65.0,
                        'v_thresh': -50.0
                        }

# pop = p.Population(300, p.IF_cond_exp(**cell_params_lif_cond), label="pop")
pop = p.Population(300, p.IF_curr_exp(**cell_params_lif_curr), label="pop")

n_spikes_in = 10
diff = 100
runtime = n_spikes_in * diff
spike_times=[]
for i in range(n_spikes_in):
    spike_times.append(i*diff)

input = p.Population(1, p.SpikeSourceArray(spike_times),
                     label="input")

# proj = p.Projection(input, pop, p.FixedProbabilityConnector(0.75),
#                     p.StaticSynapse(weight=3.0, delay=0.0),
#                     receptor_type='excitatory')
proj = p.Projection(input, pop, p.AllToAllConnector(),
                    p.StaticSynapse(weight=2.0, delay=1.0),
                    receptor_type='excitatory')

# weightdist = p.RandomDistribution("uniform", [1.0, 4.0])
# delaydist = p.RandomDistribution("uniform", [1.0, 100.0])

# proj2 = p.Projection(pop, pop, p.FixedProbabilityConnector(0.75),
#                      p.StaticSynapse(weight=weightdist, delay=delaydist),
#                      receptor_type='excitatory')
proj2 = p.Projection(pop, pop, p.AllToAllConnector(),
                     p.StaticSynapse(weight=0.001, delay=1.0),
                     receptor_type='excitatory')
# proj2 = p.Projection(pop, pop, p.FixedProbabilityConnector(0.95),
#                      p.StaticSynapse(weight=0.001, delay=1.0),
#                      receptor_type='excitatory')

pop.record('all')
p.run(runtime)

v = pop.get_data('v')
spikes = pop.get_data('spikes')
spikes1 = pop.spinnaker_get_data('spikes')

print('spikes length: ', len(spikes1))

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, runtime)),
    # membrane potentials
    Panel(v.segments[0].filter(name='v')[0],
          xlabel="Time/ms", xticks=True,
          yticks=True, xlim=(0, runtime)),
    title="high_spike_count: spikes & v plot",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

p.end()