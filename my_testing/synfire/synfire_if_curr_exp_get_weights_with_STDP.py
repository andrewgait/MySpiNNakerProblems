"""
Synfirechain-like example
"""
import pyNN.spiNNaker as p

runtime = 5000
p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
nNeurons = 200  # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons / 2)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                  }


stdp_model = p.STDPMechanism(
    timing_dependence=p.SpikePairRule(
        tau_plus=20.0, tau_minus=20.0, A_plus=0.02, A_minus=0.02),
    weight_dependence = p.AdditiveWeightDependence(w_min=0, w_max=10.0))

populations = list()
projections = list()

weight_to_spike = 2.0
delay = 17

loopConnections = list()
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
    loopConnections.append(singleConnection)

injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}

populations.append(p.Population(nNeurons, p.IF_curr_exp(**cell_params_lif),
                                label='pop_1'))
populations.append(p.Population(1, p.SpikeSourceArray(**spikeArray),
                                label='inputSpikes_1'))

projections.append(p.Projection(populations[0], populations[0],
                                p.FromListConnector(loopConnections),
                                synapse_type=stdp_model))
#                  p.StaticSynapse(weight=weight_to_spike, delay=delay)))
projections.append(p.Projection(populations[1], populations[0],
                                p.FromListConnector(injectionConnection),
                                p.StaticSynapse(
                                    weight=weight_to_spike, delay=1)))

p.run(runtime)

print projections[0].get(['weight', 'delay'], 'list')

p.end()