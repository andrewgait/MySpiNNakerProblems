import spynnaker8 as sim
from pyNN import space
import numpy as np
import matplotlib.pyplot as plt

sim.setup(timestep=1)
simtime = 50

structure = {}

structure['layer'] = space.Grid3D(
    aspect_ratioXY=2.0, aspect_ratioXZ=0.5, dx=1.0, dy=0.5, dz=1.0, x0=0.0,
    y0=0.0, z0=0, fill_order='sequential')

structure['cube'] = space.Grid3D(
    aspect_ratioXY=1.0, aspect_ratioXZ=1.0, dx=1.0, dy=1.0, dz=1.0, x0=0.0,
    y0=0.0, z0=0, fill_order='sequential')

n_neurons = 32
pops={}
pops['exc_layer'] = sim.Population(
    n_neurons, sim.IF_curr_exp(), structure = structure['layer'], label="exc_layer")
pops['inh_layer'] = sim.Population(
    n_neurons, sim.IF_curr_exp(), structure = structure['layer'], label="inh_layer")

synapse_types = {}
synapse_types['static_synapse'] = sim.StaticSynapse(weight=1.0, delay=0.5)
synapse_types['stdp_synapse'] = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=20.0, tau_minus=20.0, A_plus=0.3, A_minus=0.1),
    weight_dependence=sim.AdditiveWeightDependence(w_min=0.0, w_max=7.0),
    voltage_dependence=None,
    dendritic_delay_fraction=1.0, weight = 0.1, delay = "0.5 + 0.01*d")

connectors={}
d_rule = "exp(-d)"
connectors['distance_probability'] = sim.DistanceDependentProbabilityConnector(
    d_expression=d_rule)
connectors['one_to_one'] = sim.OneToOneConnector()
connectors['all_to_all'] = sim.AllToAllConnector()

times=[3,6,8,10,13,15,18,20,30,40]

stim = sim.Population(n_neurons, sim.SpikeSourceArray(spike_times=times), label='stim')

projs={}
projs['exc_layer', 'inh_layer'] = sim.Projection(
    pops['exc_layer'], pops['inh_layer'], connector = connectors['all_to_all'],
    synapse_type = synapse_types['stdp_synapse'], receptor_type = 'excitatory',
    space = space.Space(axes = 'xyz'))

projs['inh_layer', 'exc_layer'] = sim.Projection(
    pops['inh_layer'], pops['exc_layer'], connector = connectors['all_to_all'],
    synapse_type = synapse_types['stdp_synapse'], receptor_type = 'inhibitory',
    space = space.Space(axes = 'xyz'))

projs['stim', 'exc_layer'] = sim.Projection(
    pops['inh_layer'], pops['exc_layer'], connector = connectors['one_to_one'],
    synapse_type = synapse_types['static_synapse'], receptor_type = 'excitatory',
    space = space.Space(axes = 'xyz'))

pops['exc_layer'].record(['spikes','v','gsyn_exc','gsyn_inh'])
pops['inh_layer'].record(['spikes','v','gsyn_exc','gsyn_inh'])

sim.run(simtime)

# get_data?

sim.end()
