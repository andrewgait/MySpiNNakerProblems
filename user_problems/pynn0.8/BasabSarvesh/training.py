import spynnaker8 as p
import time
from matplotlib import pyplot as plt
import numpy as np

weights = [0.5] * 2000
digit = 0

for sample in range(140):
    start_time = time.time()

    # total duration of simulation
    TotalDuration = 120.0

    # RS neuron parameters for y and z units
    param_a = 0.03
    param_b = -2
    param_c = -50
    param_d = 100
    param_u_init = 0
    param_v_init = -60

    # excitatory input time constant
    tau_ex = 2

    # inhibitory input time constant
    tau_inh = 2

    # Iinj current if kept constant
    # current_pulse = 150

    # Iinj current from prototype data
    current_pulse = np.loadtxt("0_" + str(sample) + ".csv")
    # Number of y and z neurons
    NumYCells = 1
    NumZCells = 1

    # Model used
    model_Izh = p.Izhikevich
    model_If = p.IF_curr_exp

    '''Starting the SpiNNaker Simulator'''
    p.setup(timestep=1.0, min_delay=1.0, max_delay=10.0)
    # set number of neurons per core to 50, for the spike source to avoid clogging
    # p.set_number_of_neurons_per_core(p.SpikeSourceArray, 50)

    # Defining RS cell params for Izh
    RS_cell_params_Izh = []
    for current in current_pulse:
        RS_cell_params_Izh.append({'a': param_a, 'b': param_b, 'c': param_c, 'd': param_d,
                                   'v': param_v_init, 'u': param_u_init,
                                   'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
                                   'i_offset': current
                                   })

    # Defining RS cell params for IF curr exp
    RS_cell_params_IF = {
        'cm': 0.25, 'i_offset': 0.0, 'tau_m': 20.0,
        'tau_refrac': 2.0, 'tau_syn_E': 5.0, 'tau_syn_I': 5.0,
        'v_reset': -70.0, 'v_rest': -65.0, 'v_thresh': -50.0}

    y_Izh_population = []
    y_population = []
    z_population = []
    for i in range(200):

        y_Izh_population.append(p.Population(
            NumYCells, model_Izh(**RS_cell_params_Izh[i]), label='RS_Izh_neuron_input'))

        y_population.append(p.Population(
            NumYCells, model_If(**RS_cell_params_IF), label='RS_IF_neuron_input'))

    for j in range(10):
        z_population.append(p.Population(
            NumZCells, model_If(**RS_cell_params_IF), label='RS_IF_neuron_output'))

    # Connecting Izh constant input neurons to IF neurons
    ee_connector = p.OneToOneConnector()

    for i in range(200):
        p.Projection(
            y_Izh_population[i], y_population[i], ee_connector, receptor_type='excitatory',
            synapse_type=p.StaticSynapse(delay=5, weight=1))

    for j in range(10):
        for i in range(200):
            if(j == digit):
                p.Projection(
                    y_Izh_population[i], z_population[j], ee_connector, receptor_type='excitatory',
                    synapse_type=p.StaticSynapse(delay=10, weight=1))
            else:
                p.Projection(
                    y_Izh_population[i], z_population[j], ee_connector, receptor_type='excitatory',
                    synapse_type=p.StaticSynapse(delay=0, weight=1))

    # STDP model and connetion
    stdp_model = p.STDPMechanism(
        timing_dependence=p.SpikePairRule(
            tau_plus=20., tau_minus=20.0, A_plus=0.02, A_minus=0.02),
        weight_dependence=p.AdditiveWeightDependence(w_min=0, w_max=1))

    plastic_projection = []
    k = 0
    for j in range(10):
        for i in range(200):
            stdp_model = p.STDPMechanism(
                timing_dependence=p.SpikePairRule(
                    tau_plus=20., tau_minus=20.0, A_plus=0.02, A_minus=0.02),
                weight_dependence=p.AdditiveWeightDependence(w_min=0, w_max=1), weight=weights[k])
            k = k + 1
            plastic_projection.append(p.Projection(
                y_population[i], z_population[j], ee_connector, receptor_type='excitatory', synapse_type=stdp_model))

    # recording the spikes and voltage
    # for i in range(200):
    #     y_population[i].record(["spikes","v"])
    #     y_Izh_population[i].record(["spikes","v"])

    # for j in range(10):
    #     z_population[j].record(["spikes","v"])

    # running simulation for total duration set
    p.run(TotalDuration)

    # getting weights from the STDP connection
    for projection in range(2000):
        temp_weight = plastic_projection[projection].get('weight', 'list')
        weights[projection] = temp_weight[0][2]

    # extracting the membrane potential data (in millivolts)
    # y_membrane_data = []
    # y_izh_data = []

    # for i in range(200):
    #     #y_membrane_data.append(y_population[i].get_data(["v","spikes"]))
    #     #y_izh_data.append(y_Izh_population[i].get_data(["v","spikes"]))

    # z_membrane_data = []
    # for j in range(10):
    #     #z_membrane_data.append(z_population[j].get_data(["v","spikes"]))

    # y_membrane_spikes_converted = convert.convert_data(y_membrane_data,"spikes",run=0)
    #y_membrane_volt_converted = convert.convert_data(y_membrane_data,"v")
    # np.savetxt('y_memb_volt.csv',y_membrane_volt_converted)
    # #np.savetxt('./y_memb_spikes_'+str(count)+'.csv',y_membrane_spikes_converted)

    # proto_spike_trains.append(z_membrane_data[sample])
    # Release the SpiNNaker machine
    p.end()

final_weights = np.asarray(weights)
np.savetxt('./final_weights_' + str(digit) + '.csv', final_weights)
