#!/usr/bin/python

import spynnaker.pyNN as sim
import numpy as np
import pickle as pkl
import neo
import os
from quantities import ms

class WeightRecorder(object):
    """
    Recording of weights is not yet built in to PyNN, so therefore we need
    to construct a callback object, which reads the current weights from
    the projection at regular intervals.
    """

    def __init__(self, sampling_interval, projection):
        self.interval = sampling_interval
        self.projection = projection
        self._weights = []

    def __call__(self, t):
        self._weights.append(self.projection.get('weight', format='list', with_address=False))
        return t + self.interval

    def get_weights(self):
        signal = neo.AnalogSignal(self._weights, units='nA', sampling_period=self.interval * ms,
                                  name="weight", array_annotations={"channel_index": np.arange(len(self._weights[0]))})
        return signal


# os.environ['C_LOGS_DICT'] = '/home/sergio/tmp/training/logs/'
timestep = 1
spike_current = 20

t_max = 0

input_population_size = 2
number_of_packets = 1
spike_times = [[1,27],[1,33]]
training_times = [29]
save_spike_times = [35]

runtime = save_spike_times[-1] + 10

for i in range (number_of_packets):
    print ("")
    print ("**************************")
    print ("**************************")
    print ("Calculating weight changes for packet {}".format(i))
    print ("**************************")
    print ("**************************")
    print ("")

    sim.setup(timestep=timestep)
    sim.set_number_of_neurons_per_core(sim.IF_curr_delta, 100)

    IF_curr_delta_model = sim.IF_curr_delta()

    ssp = sim.Population(input_population_size, sim.SpikeSourceArray(spike_times), label='ssp')

    save_neuron = sim.Population(1, sim.SpikeSourceArray(save_spike_times), label='save_neuron')

    injector_neurons_exc = sim.Population(input_population_size, IF_curr_delta_model, label='injector_neurons_exc')
    injector_neurons_inh = sim.Population(input_population_size, IF_curr_delta_model, label='injector_neurons_inh')

    teacher_population = sim.Population(1, sim.SpikeSourceArray(training_times), label='teacher_population')

    output_neuron = sim.Population(1, IF_curr_delta_model, label='output_neuron')


    static_synapse = sim.StaticSynapse(weight=spike_current, delay=1)
    teaching_synapse = sim.StaticSynapse(weight=spike_current, delay=2)

    source_proj_exc = sim.Projection(ssp, injector_neurons_exc, sim.OneToOneConnector(), static_synapse, receptor_type='excitatory')
    source_proj_inh = sim.Projection(ssp, injector_neurons_inh, sim.OneToOneConnector(), static_synapse, receptor_type='excitatory')

    save_proj_exc = sim.Projection(save_neuron, injector_neurons_exc, sim.AllToAllConnector(allow_self_connections=True), static_synapse, receptor_type='excitatory')
    save_proj_inh = sim.Projection(save_neuron, injector_neurons_inh, sim.AllToAllConnector(allow_self_connections=True), static_synapse, receptor_type='excitatory')

    training_proj = sim.Projection(teacher_population, output_neuron, sim.AllToAllConnector(allow_self_connections=True), teaching_synapse, receptor_type='excitatory')

    stdp_model = sim.STDPMechanism(
        timing_dependence=sim.SpikePairRule(tau_plus=10, tau_minus=12, A_plus=1, A_minus=-1),
        weight_dependence=sim.AdditiveWeightDependence(w_min=0, w_max=20),
        weight=0,
        delay=1)
    stdp_model2 = sim.STDPMechanism(
        timing_dependence=sim.SpikePairRule(tau_plus=10, tau_minus=12, A_plus=1, A_minus=-1),
        weight_dependence=sim.AdditiveWeightDependence(w_min=0, w_max=20),
        weight=0,
        delay=1)

    injector_proj_exc = sim.Projection(injector_neurons_exc, output_neuron, sim.AllToAllConnector(allow_self_connections=True), stdp_model, receptor_type='excitatory')
    injector_proj_inh = sim.Projection(injector_neurons_inh, output_neuron, sim.AllToAllConnector(allow_self_connections=True), stdp_model2, receptor_type='inhibitory')

    ssp.record(['spikes'])
    save_neuron.record(['spikes'])
    output_neuron.record(['v','gsyn_exc','spikes'])
    teacher_population.record(['spikes'])
    injector_neurons_exc.record(['spikes'])
    injector_neurons_inh.record(['spikes'])

    weight_recorder_exc = WeightRecorder(sampling_interval=1, projection=injector_proj_exc)
    weight_recorder_inh = WeightRecorder(sampling_interval=1, projection=injector_proj_inh)

    sim.run(runtime, callbacks=[weight_recorder_exc, weight_recorder_inh])
#    sim.run(runtime, callbacks=[weight_recorder_inh])

    vm = output_neuron.get_data().segments[0].filter(name="v")
    im = output_neuron.get_data().segments[0].filter(name="gsyn_exc")
    spikesm = output_neuron.get_data().segments[0].spiketrains

    weights_exc = weight_recorder_exc.get_weights()
    weights_inh = weight_recorder_inh.get_weights()
    #final_weights = np.array(weights[-1])

    ssp_spikes = ssp.get_data().segments[0].spiketrains
    save_spikes = save_neuron.get_data().segments[0].spiketrains
    spikest = teacher_population.get_data().segments[0].spiketrains

    injector_spikes_exc = injector_neurons_exc.get_data().segments[0].spiketrains
    injector_spikes_inh = injector_neurons_inh.get_data().segments[0].spiketrains
    #injector_v = injector_neurons.get_data().segments[0].filter(name="v")[0]
    #injector_i = injector_neurons.get_data().segments[0].filter(name="gsyn_exc")[0]

    filename = "saved_data_modified/v_packet{}.pkl".format(i)
    v_file = open(filename, 'wb')
    pkl.dump(vm, v_file)
    v_file.close()

    filename = "saved_data_modified/i_packet{}.pkl".format(i)
    i_file = open(filename, 'wb')
    pkl.dump(im, i_file)
    i_file.close()

    filename = "saved_data_modified/weight_exc_final_packet{}.pkl".format(i)
    weight_file = open(filename, 'wb')
    pkl.dump(weights_exc, weight_file)
    weight_file.close()

    filename = "saved_data_modified/weight_inh_final_packet{}.pkl".format(i)
    weight_file = open(filename, 'wb')
    pkl.dump(weights_inh, weight_file)
    weight_file.close()

    filename = "saved_data_modified/ssp_spikes_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(ssp_spikes, spike_file)
    spike_file.close()

    filename = "saved_data_modified/save_spikes_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(save_spikes, spike_file)
    spike_file.close()

    filename = "saved_data_modified/injector_spikes_exc_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(injector_spikes_exc, spike_file)
    spike_file.close()

    filename = "saved_data_modified/injector_spikes_inh_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(injector_spikes_inh, spike_file)
    spike_file.close()

    filename = "saved_data_modified/spikest_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(spikest, spike_file)
    spike_file.close()

    filename = "saved_data_modified/spikesm_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(spikesm, spike_file)
    spike_file.close()

    print (weights_exc)
    print (weights_inh)
    print (weights_exc[-1].magnitude)
    print (weights_inh[-1].magnitude)
    print (np.where(weights_exc[-1].magnitude==1))
    print (np.where(weights_inh[-1].magnitude==1))
    print (injector_spikes_exc)
    print (injector_spikes_inh)
    print (spikesm)
    print (vm)
    print (im)
    input()


#    print("Input spike times: %s" % ssp_spikes)
#    print("Save spike times: %s" % save_spikes)
#    print("Injector spike times: %s" % injector_spikes)
#    print("Teacher spike times: %s" % spikest)
#    print("Output spike times: %s" % spikesm)

    sim.end()

#    break
