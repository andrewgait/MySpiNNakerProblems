"""
Synfirechain-like example
"""
import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import json

runtime = 200
p.setup(timestep=1.0)
nNeurons = 8 #3456  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_cond_exp, 80 )

cell_params_lif = {'cm': 0.09,
                   'i_offset': 0.0,
                   'tau_m': 1000.0,
                   'tau_refrac': 0.0,
                   'tau_syn_E': 0.01,
                   'tau_syn_I': 0.01,
                   'v_reset': 0.0,
                   'v_rest': 0.0,
                   'v_thresh': 1.0,
                   'e_rev_E' : 10,
                   'e_rev_I' : -10.
                   }


connections_ex = [
(0.0, 0.0, 2.39533, 9),
(1.0, 3.0, 3.0, 10),
(2.0, 5.0, 1.88471, 5),
(4.0, 7.0, 4.0, 4),
(5.0, 4.0, 1.0, 6),
(7.0, 2.0, 1.0, 5)
]

connections_in = [
(3.0, 6.0, -1.9463, 3),
(6.0, 1.0, -0.336171, 2),
]


def input_spike():
        with  open('inputspike.txt', 'r') as f:
              data = f.read()
              data = json.loads(data)
              #print('json',data)
              spiketrains=data

        return spiketrains

p.set_number_of_neurons_per_core(p.SpikeSourceArray, 100)

spiketrains = input_spike()

main_pop = p.Population(
    nNeurons, p.IF_cond_exp(**cell_params_lif), label='pop_1')

main_pop.initialize(v=0.0)
input_pop = p.Population(
    8, p.SpikeSourceArray(spike_times=spiketrains), label='inputSpikes_1')

proj=p.Projection(
    #input_pop, main_pop, p.FromListConnector(connections_ex, ['weight', 'delay']), receptor_type='excitatory')
    input_pop, main_pop, p.FromFileConnector('con.txt'), receptor_type='excitatory')


proj2=p.Projection(
    input_pop, main_pop, p.FromListConnector(connections_in, ['weight', 'delay']), receptor_type='inhibitory')



input_pop.record(['spikes'])

main_pop.record(['v', 'gsyn_exc', 'gsyn_inh', 'spikes'])

p.run(runtime)

print(proj.get(["weight", "delay"], format="list"))

print(proj2.get(["weight", "delay"], format="list"))


# get data (could be done as one, but can be done bit by bit as well)
v = main_pop.get_data('v')
gsyn_exc = main_pop.get_data('gsyn_exc')
gsyn_inh = main_pop.get_data('gsyn_inh')
spikes = main_pop.get_data('spikes')

in_spikes = input_pop.get_data('spikes')

figure_filename = "results.png"
Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(in_spikes.segments[0].spiketrains,
        yticks=True, markersize=5.0, color='R', xlim=(0, runtime)),

    #Panel(spikes.segments[0].spiketrains,
    #      yticks=True, markersize=0.5, color='B', xlim=(0, runtime)),
    # membrane potential of the postsynaptic neuron
    #Panel(v.segments[0].filter(name='v')[0],
    #      ylabel="Membrane potential (mV)",
    #      data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_exc.segments[0].filter(name='gsyn_exc')[0],
          ylabel="gsyn excitatory (mV)",
          data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    Panel(gsyn_inh.segments[0].filter(name='gsyn_inh')[0],
          ylabel="gsyn inhibitory (mV)",
          data_labels=[main_pop.label], yticks=True, xlim=(0, runtime)),
    title="Simple synfire chain example on Spinnaker(poisson rate=50)",
    annotations="Simulated with {}".format(p.name())
)
plt.show()
print(figure_filename)

p.end()
