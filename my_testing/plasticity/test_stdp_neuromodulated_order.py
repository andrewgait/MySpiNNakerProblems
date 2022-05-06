# Copyright (c) 2017-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Testing whether the order of projections is important or not
"""

try:
    import pyNN.spiNNaker as sim
except Exception:
    import pyNN.spiNNaker as sim
import pylab
import numpy as np
from pyNN.random import NumpyRNG
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

timestep = 1.0
stim_rate = 1
duration = 12000
plastic_weights = 2.0
n_neurons = 10
rng = NumpyRNG(seed=11)

# Times of rewards and punishments
rewards = [x for x in range(2000, 2010)] + \
          [x for x in range(3000, 3020)] + \
          [x for x in range(4000, 4100)]
punishments = [x for x in range(6000, 6010)] + \
              [x for x in range(7000, 7020)] + \
              [x for x in range(8000, 8100)]

cell_params = {'cm': 0.25,
               'i_offset': 0.0,
               'tau_m': 20.0,
               'tau_refrac': 2.0,
               'tau_syn_E': 1.0,
               'tau_syn_I': 1.0,
               'v_reset': -70.0,
               'v_rest': -65.0,
               'v_thresh': -50.0
               }

sim.setup(timestep=timestep)

# Create a population of dopaminergic neurons for reward and punishment
reward_pop = sim.Population(n_neurons, sim.SpikeSourceArray,
                            {'spike_times': rewards}, label='reward')
punishment_pop = sim.Population(n_neurons, sim.SpikeSourceArray,
                                {'spike_times': punishments},
                                label='punishment')

stim_pop = sim.Population(
    n_neurons, sim.SpikeSourcePoisson,
    {'rate': stim_rate, 'duration': duration}, label="pre")

#### from here

post_pop1 = sim.Population(n_neurons, sim.IF_curr_exp,
                           cell_params, label='post')
post_pop2 = sim.Population(n_neurons, sim.IF_curr_exp,
                           cell_params, label='post')

synapse_dynamics_neuromod = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=2, tau_minus=1,
        A_plus=1, A_minus=1),
    weight_dependence=sim.MultiplicativeWeightDependence(w_min=0, w_max=20),
    weight=plastic_weights)

plastic_projection1a = sim.Projection(
    stim_pop, post_pop1,
    sim.OneToOneConnector(),
    synapse_type=synapse_dynamics_neuromod,
    receptor_type='excitatory',
    label='Pre-post1a projection')
plastic_projection2a = sim.Projection(
    stim_pop, post_pop2,
    sim.OneToOneConnector(),
    synapse_type=synapse_dynamics_neuromod,
    receptor_type='excitatory',
    label='Pre-post2a projection')
plastic_projection2b = sim.Projection(
    stim_pop, post_pop2,
    sim.AllToAllConnector(),
    synapse_type=synapse_dynamics_neuromod,
    receptor_type='excitatory',
    label='Pre-post2b projection')
plastic_projection2c = sim.Projection(
    stim_pop, post_pop2,
    sim.AllToAllConnector(),
    synapse_type=synapse_dynamics_neuromod,
    receptor_type='excitatory',
    label='Pre-post2b projection')
# plastic_projection1b = sim.Projection(
#     stim_pop, post_pop1,
#     sim.AllToAllConnector(),
#     synapse_type=synapse_dynamics_neuromod,
#     receptor_type='excitatory',
#     label='Pre-post1b projection')

reward_projection1 = sim.Projection(
    reward_pop, post_pop1, sim.OneToOneConnector(),
    synapse_type=sim.extra_models.Neuromodulation(
            weight=0.05, tau_c=100.0, tau_d=5.0, w_max=20.0),
    receptor_type='reward',
    label='reward synapses 1')
punishment_projection1 = sim.Projection(
    punishment_pop, post_pop1, sim.OneToOneConnector(),
    synapse_type=sim.extra_models.Neuromodulation(
            weight=0.05, tau_c=100.0, tau_d=5.0, w_max=20.0),
    receptor_type='punishment',
    label='punishment synapses 1')
reward_projection2 = sim.Projection(
    reward_pop, post_pop2, sim.OneToOneConnector(),
    synapse_type=sim.extra_models.Neuromodulation(
            weight=0.05, tau_c=100.0, tau_d=5.0, w_max=20.0),
    receptor_type='reward',
    label='reward synapses 2')
punishment_projection2 = sim.Projection(
    punishment_pop, post_pop2, sim.OneToOneConnector(),
    synapse_type=sim.extra_models.Neuromodulation(
            weight=0.05, tau_c=100.0, tau_d=5.0, w_max=20.0),
    receptor_type='punishment',
    label='punishment synapses 2')

plastic_projection1b = sim.Projection(
    stim_pop, post_pop1,
    sim.AllToAllConnector(),
    synapse_type=synapse_dynamics_neuromod,
    receptor_type='excitatory',
    label='Pre-post1b projection')
plastic_projection1c = sim.Projection(
    stim_pop, post_pop1,
    sim.AllToAllConnector(),
    synapse_type=synapse_dynamics_neuromod,
    receptor_type='excitatory',
    label='Pre-post1b projection')

post_pop1.record("spikes")
post_pop2.record("spikes")

sim.run(duration)

# Graphical diagnostics


def plot_spikes(mid_spikes, spikes, title, n_pops, n_neurons):
    if spikes is not None:
        pylab.figure(figsize=(15, 5))
        pylab.xlim((0, duration))
        pylab.ylim((0, (n_pops * n_neurons) + 1))
        pylab.plot(
            [i[1] for i in mid_spikes], [i[0] for i in mid_spikes], "y.")
        pylab.plot([i[1] for i in spikes], [i[0] for i in spikes], "b.")
        pylab.xlabel('Time/ms')
        pylab.ylabel('spikes')
        pylab.title(title)
    else:
        print("No spikes received")


post_spikes1 = []
post_spikes2 = []
weights = []

weights.append(plastic_projection1a.get('weight', 'list'))
weights.append(plastic_projection1b.get('weight', 'list'))
weights.append(plastic_projection2a.get('weight', 'list'))
weights.append(plastic_projection2b.get('weight', 'list'))
spikes1 = post_pop1.get_data('spikes').segments[0].spiketrains
spikes2 = post_pop2.get_data('spikes').segments[0].spiketrains
# for j in range(n_neurons):
#     for x in spikes1[j]:
#         post_spikes1.append([j+1, x])
#     for x in spikes2[j]:
#         post_spikes2.append([j+1, x])
#
# plot_spikes(post_spikes1, post_spikes2, "post-synaptic neuron activity",
#             1, n_neurons)
# pylab.plot(rewards, [0.5 for x in rewards], 'g^')
# pylab.plot(punishments, [0.5 for x in punishments], 'r^')
# pylab.show()

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(spikes1, xlabel="Time/ms", xticks=True,
          yticks=True, markersize=0.5, xlim=(0, duration)),
    Panel(spikes2, xlabel="Time/ms", xticks=True,
          yticks=True, markersize=0.5, xlim=(0, duration)),
    title="Test neuromodulation order: spikes",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()

print("Weights(Initial %s)" % plastic_weights)
for x in weights:
    print(x)

sim.end()
