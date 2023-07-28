#!/usr/bin/python

import spikes as spikeSourceTimes
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

    def __init__(self, sampling_interval, runtime, timestep, input_population_size, projection):
        self.interval = sampling_interval
        self.projection = projection
        self._weights = np.zeros((int(runtime+1), input_population_size))
        self._timestep = timestep
        self._input_population_size = input_population_size

    def __call__(self, t):
        if t > 0:
            slice_index = int(t/self._timestep)
            print ("Extracting weights for ms: {}".format(slice_index))
            #self._weights.append(self.projection.get('weight', format='list', with_address=False))
            self._weights[slice_index] = self.projection.get('weight', format='list', with_address=False)
            if (np.sum(self._weights[slice_index]) != 0):
                print ("Weights at time {} are different from 0".format(slice_index))

            if t%1000 == 0:
                weight_timestamp_filename = "weight_{}.pkl".format(int(t))
                weight_file_timestamp = open(weight_timestamp_filename, 'wb')
                pkl.dump(self._weights, weight_file_timestamp)
                weight_file_timestamp.close()

                if (t - 1000) > 0:
                    weight_timestamp_filename_delete = "weight_{}.pkl".format(t - 1000)
                    os.remove(weight_timestamp_filename_delete)

        return t + self.interval

    def get_weights(self):
        signal = neo.AnalogSignal(self._weights, units='nA', sampling_period=self.interval * ms,
                                  name="weight", array_annotations={"channel_index": np.arange(len(self._weights[0]))})
        return signal


os.environ['C_LOGS_DICT'] = '/home/sergio/tmp/training/logs/'
timestep = 1
spike_current = 20

t_max = 0

input_population_size = len(spikeSourceTimes.spike_times[0])

save_spike_times = [13]

runtime = save_spike_times[-1] + 10

for i in range (spikeSourceTimes.number_of_packets):
    print ("Calculating weight changes for packet {}".format(i))

    sim.setup(timestep=timestep)
    sim.set_number_of_neurons_per_core(sim.IF_curr_delta, 100)

    IF_curr_delta_model = sim.IF_curr_delta(i_offset=0.0, tau_refrac = 0)

    ssp = sim.Population(input_population_size, sim.SpikeSourceArray(spikeSourceTimes.spike_times[i]), label='ssp')

    save_neuron = sim.Population(1, sim.SpikeSourceArray(save_spike_times), label='save_neuron')

    injector_neurons = sim.Population(input_population_size, IF_curr_delta_model, label='injector_neurons')

    teacher_population = sim.Population(1, sim.SpikeSourceArray(spikeSourceTimes.training_times), label='teacher_population')

    output_neuron = sim.Population(1, IF_curr_delta_model, label='output_neuron')


    static_synapse = sim.StaticSynapse(weight=spike_current, delay=1)
    teaching_synapse = sim.StaticSynapse(weight=spike_current, delay=5)

    source_proj = sim.Projection(ssp, injector_neurons, sim.OneToOneConnector(), static_synapse, receptor_type='excitatory')

    save_proj = sim.Projection(save_neuron, injector_neurons, sim.AllToAllConnector(allow_self_connections=True), static_synapse, receptor_type='excitatory')

    training_proj = sim.Projection(teacher_population, output_neuron, sim.AllToAllConnector(allow_self_connections=True), teaching_synapse, receptor_type='excitatory')

    stdp_model = sim.STDPMechanism(
        timing_dependence=sim.SpikePairRule(tau_plus=10, tau_minus=12, A_plus=1, A_minus=1),
        weight_dependence=sim.AdditiveWeightDependence(w_min=0, w_max=20),
        weight=0,
        delay=1)

    injector_proj = sim.Projection(injector_neurons, output_neuron, sim.AllToAllConnector(allow_self_connections=True), stdp_model, receptor_type='excitatory')

    ssp.record(['spikes'])
    save_neuron.record(['spikes'])
    output_neuron.record(['v','gsyn_exc','spikes'])
    teacher_population.record(['spikes'])
    injector_neurons.record(['spikes'])

    weight_recorder = WeightRecorder(sampling_interval=1, runtime=runtime, timestep=timestep, input_population_size=input_population_size, projection=injector_proj)

    sim.run(runtime, callbacks=[weight_recorder])

    vm = output_neuron.get_data().segments[0].filter(name="v")
    im = output_neuron.get_data().segments[0].filter(name="gsyn_exc")
    spikesm = output_neuron.get_data().segments[0].spiketrains

    weights = weight_recorder.get_weights()
    #final_weights = np.array(weights[-1])

    ssp_spikes = ssp.get_data().segments[0].spiketrains
    save_spikes = save_neuron.get_data().segments[0].spiketrains
    spikest = teacher_population.get_data().segments[0].spiketrains

    injector_spikes = injector_neurons.get_data().segments[0].spiketrains
    #injector_v = injector_neurons.get_data().segments[0].filter(name="v")[0]
    #injector_i = injector_neurons.get_data().segments[0].filter(name="gsyn_exc")[0]

    filename = "saved_data/v_packet{}.pkl".format(i)
    v_file = open(filename, 'wb')
    pkl.dump(vm, v_file)
    v_file.close()

    filename = "saved_data/i_packet{}.pkl".format(i)
    i_file = open(filename, 'wb')
    pkl.dump(im, i_file)
    i_file.close()

    filename = "saved_data/weight_final_packet{}.pkl".format(i)
    weight_file = open(filename, 'wb')
    pkl.dump(weights, weight_file)
    weight_file.close()

    filename = "saved_data/ssp_spikes_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(ssp_spikes, spike_file)
    spike_file.close()

    filename = "saved_data/save_spikes_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(save_spikes, spike_file)
    spike_file.close()

    filename = "saved_data/injector_spikes_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(injector_spikes, spike_file)
    spike_file.close()

    filename = "saved_data/spikest_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(spikest, spike_file)
    spike_file.close()

    filename = "saved_data/spikesm_packet{}.pkl".format(i)
    spike_file = open(filename, 'wb')
    pkl.dump(spikesm, spike_file)
    spike_file.close()

    print (vm)
    print (im)


    print("Input spike times: %s" % ssp_spikes)
    print("Save spike times: %s" % save_spikes)
    print("Injector spike times: %s" % injector_spikes)
    print("Teacher spike times: %s" % spikest)
    print("Output spike times: %s" % spikesm)

    sim.end()

    break
