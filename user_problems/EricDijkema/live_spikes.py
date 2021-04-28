import spynnaker8 as p

# Setup
runtime = 5000
p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
nNeurons = 20 # number of neurons in each population
p.set_number_of_neurons_per_core(p.IF_curr_exp, nNeurons / 2)

cell_params_lif = {'cm': 0.25,
'i_offset': 0.0,
'tau_m': 20.0,
'tau_refrac': 2.0,
'tau_syn_E': 5.0,
'tau_syn_I': 5.0,
'v_reset': -70.0,
'v_rest': -65.0,
'v_thresh': -50.0,
'e_rev_E': 0.,
'e_rev_I': -80.
}

weight_to_spike = 0.035
delay = 17

loopConnections = list()
for i in range(0, nNeurons):
    singleConnection = ((i, (i + 1) % nNeurons, weight_to_spike, delay))
    loopConnections.append(singleConnection)

injectionConnection = [(0, 0)]
spikeArray = {'spike_times': [[0]]}

# Declare populations
main_pop = p.Population(
    nNeurons, p.IF_cond_exp(**cell_params_lif), label='pop_1')
input_pop = p.Population(
    1, p.SpikeSourceArray(**spikeArray), label='inputSpikes_1')

# Declare projections
p.Projection(
    main_pop, main_pop, p.FromListConnector(loopConnections),
p.StaticSynapse(weight=weight_to_spike, delay=delay))
p.Projection(
    input_pop, main_pop, p.FromListConnector(injectionConnection),
    p.StaticSynapse(weight=weight_to_spike, delay=1))

def receive_spikes(label, time, neuron_ids):
    for neuron_id in neuron_ids:
        print("Received spike at time {} from {}-{}".format(
            time, label, neuron_id))


live_spikes_connection = p.external_devices.SpynnakerLiveSpikesConnection(receive_labels=["pop_1"])

live_spikes_connection.add_receive_callback("pop_1", receive_spikes)

# Receiver
p.external_devices.activate_live_output_for(
    main_pop,
    database_notify_port_num=live_spikes_connection.local_port)

p.run(runtime)

p.end()
live_spikes_connection.close()