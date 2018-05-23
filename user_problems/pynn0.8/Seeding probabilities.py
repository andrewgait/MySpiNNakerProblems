import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import time
import copy
import pylab
import numpy as np
import threading
from threading import Condition
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pyNN.random import RandomDistribution# as rand
#import spynnaker8.spynakker_plotting as splot

input_labels = list()
output_labels = list()
no_neuron_pops = 9
pop_size = 25
poisson_rate = 1
time_segments = 200
average_runtime = 0.1
duration = 4000
run = 0

motor_spikes = [0 for i in range(2)]
def receive_spikes(label, time, neuron_ids):
    for neuron_id in neuron_ids:
#        for i in range(2):
            if label == output_labels[i]:
                motor_spikes[i] += 1

def threading_function(connection, start):
    new_start = time.clock()
    if(new_start - start < float(duration)/ 1000.0):
        print "set the rate at ",time.clock()
        connection.set_rates(input_labels[0],
                             [(i, poisson_rate) for i in range(pop_size)])
    finish = time.clock()
    print "elapsed time2 = {}\t{} - {}".format(finish - start, finish, start)

def poisson_threading(label, connection):
    #float_time = float(time_segments) / 1000.0
    start = time.clock()
    #time.sleep(float_time)
    offset1 = time.clock()
    threading.Thread(threading_function(connection, start)).start()
    offset2 = time.clock()
    poisson_threading2(label, connection, start, offset2 - offset1)
    finish = time.clock()
    print "elapsed time = {}\t{} - {}".format(finish - start, finish, start)

def poisson_threading2(label, connection, start, offset):
    float_time = float(time_segments) / 1000.0
    time.sleep(float_time - offset)
    offset1 = time.clock()
    threading.Thread(threading_function(connection, start)).start()
    offset2 = time.clock()
    poisson_threading2(label, connection, start, offset2 - offset1)
    finish = time.clock()
    print "elapsed time3 = {}\t{} - {}".format(finish - start, finish, start)

# def ballbeam(label, connection):
#     global current_angle
#     global current_beam_vlct
#     global current_beam_acc
#     global current_position
#     global current_ball_vlct
#     global current_ball_acc
#     global current_agent
#     global average_runtime
#     global motor_spikes
#     #convert to poisson rate
#     min_poisson_dist = 1
#     max_poisson_dist = poisson_rate
#     min_poisson_angle = 1
#     max_poisson_angle = poisson_rate
#     float_time = float(time_segments - (average_runtime * 1000)) / 1000
#     total = 0
#     start = time.clock()
#     for i in range(0, duration, time_segments):
#         #set at the precise time needed
#         float_time = max((float(i) / 1000.0) - (time.clock() - start), 0)
#         time.sleep(float_time)
#         clockwise = 0
#         anticlock = 0
#         for j in range(no_output_pop):
#             #clockwise rotation
#             if j < no_output_pop / 2:
#                 clockwise += motor_spikes[j]
#                 motor_spikes[j] = 0
#             #anticlockwise
#             else:
#                 anticlock += motor_spikes[j]
#                 motor_spikes[j] = 0
#         total_clock = clockwise - anticlock
#         torque = float(total_clock) * spike_to_torque
#         current_ball_acc = (current_ball_vlct*np.power(current_beam_vlct,2)) - (g*np.sin(current_angle))
#         current_ball_acc /= (1 + (moi_ball/(mass*np.power(radius,2))))
#         # current_ball_acc = (-5.0/7.0) * ((g * np.sin(current_angle)) - (current_position * np.power(current_beam_vlct, 2)))
#         current_beam_acc = (torque - (mass*g*current_position*np.cos(current_angle)) -
#                             (2*mass*current_position*current_ball_vlct*current_beam_vlct))
#         #current_beam_acc = torque
#         current_beam_acc /= (mass*np.power(current_position,2)) + moi_ball + moi_beam
#         seconds_window = float(time_segments / 1000.0)
#         current_ball_vlct += float(current_ball_acc * seconds_window)
#         current_position += float(current_ball_vlct *seconds_window)
#         current_beam_vlct += float(current_beam_acc * seconds_window)
#         #check that the beam is not at the maximum angle
#         previous_angle = current_angle
#         current_angle += float(current_beam_vlct * seconds_window)
#         current_angle = max(min(current_angle, max_angle), min_angle)
#         if current_angle == previous_angle:
#             current_beam_acc = 0
#             current_beam_vlct = 0
#         print "clock = {}\tanti = {}\ttorque = {}\tpos = {}\tangle = {}".format(clockwise,anticlock,torque,current_position,current_angle)
#         #set poisson rate
#         current_pos_ratio = max(min((current_position + beam_length) / (beam_length * 2), 1), 0)
#         poisson_position = min_poisson_dist + ((max_poisson_dist - min_poisson_dist) * current_pos_ratio)
#         current_ang_ratio = (current_angle + max_angle) / (max_angle * 2)
#         poisson_angle = min_poisson_angle + ((max_poisson_angle - min_poisson_angle) * current_ang_ratio)
#         #print "\tpoisson angle = {}\tposition = {}".format(poisson_angle, poisson_position)
#         n_number = pop_size
#         #set at the precise time needed
#         # time.sleep(max((float(i) / 1000.0) - (time.clock() - start), 0))
#         finish1 = time.clock()
#         connection.set_rates(input_labels[0], [(i, int(round(poisson_position))) for i in range(n_number)])
#         n_number = pop_size
#         connection.set_rates(input_labels[1], [(i, int(round(poisson_angle))) for i in range(n_number)])
#         experimental_record.append([current_position, current_ball_vlct,current_ball_acc,
#                                     current_angle, current_beam_vlct, current_beam_acc, time.clock()])
#         if abs(current_position) > beam_length or time.clock() - start > float(duration) / 1000.0:
#             #p.end()
#             break
#         finish = time.clock()
#         print "elapsed time = {} & {}\t{} - {}\tave_float = {}".format(finish1 - start, finish - start, finish, start, float_time)
#     #print 'total = {}, average = {}'.format(total, total/len(experimental_record))

def poisson_setting(label, connection):
    #float_time = float(time_segments - (average_runtime * 1000)) / 1000
    start = time.clock()
    for i in range(0, duration, time_segments):
        #time.sleep(float_time)
        time.sleep(max((float(i) / 1000.0) - (time.clock() - start), 0))
        connection.set_rates(label,
                             [(i, poisson_rate) for i in range(pop_size)])
        connection.set_rates(input_labels[1],
                             [(i, poisson_rate) for i in range(pop_size)])
        finish = time.clock()
        print "elapsed time = {}\t{} - {}".format(finish - start, finish, start)

poisson_angle_rates = [
    [9.78109456227, 15.9242335044, 15.9242335044, 15.9242335044, 15.9242335044, 15.9242335044, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    [9.78109456227, 15.9242335044, 15.9242335044, 15.9242335044, 15.9242335044, 15.9242335044, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
poisson_pos_rates = [
    [14.7019572675, 14.7004519057, 14.6595097958, 14.5803130904, 14.4628617894, 14.3159214112, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],

    [14.7019572675, 14.7004519057, 14.6595097958, 14.5803130904, 14.4628617894, 14.3159214112, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]
def from_list_poisson(label, connection):
    counter = 0
    start = time.clock()
    for i in range(0, duration, time_segments):
        float_time = max((float(i) / 1000.0) - (time.clock() - start), 0)
        time.sleep(float_time)
        if poisson_angle_rates[run][counter] > 1e-10:
            connection.set_rates(label,
                                 [(i, int(round(poisson_angle_rates[run][counter]))) for i in range(pop_sizes[0])])
            connection.set_rates(input_labels[1],
                                 [(i, int(round(poisson_pos_rates[run][counter]))) for i in range(pop_sizes[1])])
            stopped = 0
        else:
            stopped = 1
        finish = time.clock()
        print("motor_spikes: ", motor_spikes[0], motor_spikes[1])
        motor_spikes[0] = 0
        motor_spikes[1] = 0
        print "\tpoisson angle = {}\tposition = {}".format(poisson_angle_rates[run][counter], poisson_pos_rates[run][counter])

        print "elapsed time = {}\t{} - {}\tave_float = {}".format(finish - start, finish, start, float_time)
        if stopped == 1:
            print "stopped"
        counter += 1

pop_sizes = [119, 202, 111, 190, 71, 20, 182, 125, 215]

connect_prob_ex = [
    [0, 0.0681103414277, 0, 0, 0, 0, 0],
    [0, 0.000879610797628, 0, 0, 0, 0, 0],
    [0, 0.0828934387848, 0, 0.00207233596962, 0.00310850395443, 0, 0],
    [0, 0.00905033278898, 0, 0, 0, 0, 0],
    [0, 0, 0.000285849460898, 0, 0, 0.000285849460898, 0],
    [0.00936117791912, 0, 0, 0.00936117791912, 0, 0, 0],
    [0, 0, 0, 0, 0.000428056933407, 0, 0],
    [0.033665597766, 0, 0.0871344883356, 0.000990164640177, 0, 0.0871344883356, 0],
    [0, 0, 0, 0, 0, 0, 0]
]
connect_prob_in = [
    [0, 0.0604875120675, 0, 0, 0, 0, 0],
    [0, 0.00175251036758, 0, 0, 0, 0, 0],
    [0, 0.0508694541704, 0, 0.00127173635426, 0.00190760453139, 0, 0],
    [0, 0.0107679095459, 0, 0, 0, 0, 0],
    [0, 0, 0.178581636029, 0, 0, 0.178581636029, 0],
    [0.0221858007188, 0, 0, 0.0221858007188, 0, 0, 0],
    [0, 0, 0, 0, 0.00649903192466, 0, 0],
    [0.00192629440402, 0, 0.00498570316334, 5.66557177653e-05, 0, 0.00498570316334, 0],
    [0, 0, 0, 0, 0, 0, 0]
]
weight_mu = [0.0135315696237, 0.0133187405204, 0.00523644511694, 0.0111355836581, 0.00754018872431, 0.0013891381521,
             0.0125005772243, 0.00325860018406, 0]

weight_stdev = [0.00450565473001, 0.0016606547142, 0.00258163559908, 0.00286878820071, 0.00367132509218,
                0.00263321748455, 0.00386578662016, 0.00151869625327, 0]

delay_mu = [29.2650104591, 5.94240397319, 6.59281133218, 4.33278441921, 37.6847640275, 2.90869010045, 9.28699973655,
            24.8738493471, 0]

delay_stdev = [2.71154188689, 1.43696779091, 2.10549943528, 0.612859684105, 0.125665806109, 0.919638238878, 1.410038668,
               2.19690554715, 0]

def spinn_net():
    np.random.seed(272727)
    global output_labels
    global input_labels
    p.setup(timestep=1.0, min_delay=1, max_delay=60)
    p.set_number_of_neurons_per_core(p.IF_cond_exp, 64)
    n_pop_labels = []
    n_pop_list = []
    n_proj_list = []
    spike_source_list = []
    if offset != 0:
        for i in range(2):
            del output_labels[0]
        output_labels = list()
        for i in range(2):
            del input_labels[0]
        input_labels = list()
    for i in range(no_neuron_pops):
        #set up the input as a live spike source
        if i < 2:
            n_pop_labels.append("Input_pop{}".format(i))
            input_labels.append("Input_pop{}".format(i))
            n_pop_list.append(
                p.Population(pop_sizes[i], p.SpikeSourcePoisson(rate=poisson_rate),
                             label=n_pop_labels[i]))
            n_pop_list[i].record(["spikes"])
            p.external_devices.add_poisson_live_rate_control(
                n_pop_list[i], database_notify_port_num=(16000+offset))
        #set up output pop
        elif i < 4:
            n_pop_labels.append("Output_pop{}".format(i))
            output_labels.append("Output_pop{}".format(i))
            n_pop_list.append(p.Population(pop_sizes[i], p.IF_cond_exp(),
                                           label=n_pop_labels[i]))
            p.external_devices.activate_live_output_for(
                n_pop_list[i], database_notify_port_num=(18000+offset),
                port=(17000+offset))
            spike_source_list.append(p.Population(pop_sizes[i], p.SpikeSourcePoisson(rate=0.0),
                                                  label="source ".format(n_pop_labels[i])))
            n_pop_list[i].record(["spikes", "v"])
        #set up all other populations
        else:
            n_pop_labels.append("neuron{}".format(i))
            n_pop_list.append(p.Population(pop_sizes[i], p.IF_cond_exp(),
                                           label=n_pop_labels[i]))
            spike_source_list.append(p.Population(pop_sizes[i], p.SpikeSourcePoisson(rate=0.0),
                                                  label="source ".format(n_pop_labels[i])))
            n_pop_list[i].record(["spikes", "v"])



    poisson_control = p.external_devices.SpynnakerPoissonControlConnection(
        poisson_labels=input_labels, local_port=(16000+offset))
    poisson_control.add_start_callback(n_pop_list[0].label, from_list_poisson)
    poisson_control.add_start_callback(n_pop_list[1].label, from_list_poisson)
    # poisson_control.add_start_callback(n_pop_list[1].label, poisson_setting)
    # poisson_control.add_start_callback(n_pop_list[0].label, poisson_threading)



    live_connection = p.external_devices.SpynnakerLiveSpikesConnection(
        receive_labels=output_labels, local_port=(18000+offset))
    live_connection.add_receive_callback(n_pop_labels[2], receive_spikes)
    live_connection.add_receive_callback(n_pop_labels[3], receive_spikes)



    # weight_mu = 0.015
    # weight_sdtev = 0.05
    # delay_mu = 40
    # delay_sdtev = 5
    for i in range(no_neuron_pops):
        np.random.seed(272727)
        weights = RandomDistribution("normal_clipped", mu=weight_mu[i],
                                     sigma=weight_stdev[i], low=0, high=np.inf)
        delays = RandomDistribution("normal_clipped", mu=delay_mu[i],
                                    sigma=delay_stdev[i], low=1, high=55)
        synapse = p.StaticSynapse(weight=weights, delay=delays)
        for j in range(2, no_neuron_pops):
            print "\npop = {}({}) connecting to {}".format(i,pop_sizes[i],j)
            if connect_prob_ex[i][j-2] > 1e-10:
                print "ex = {}\tin = {}".format(connect_prob_ex[i][j-2], connect_prob_in[i][j-2])
                print "\tweight mu = {}\t stdev = {}".format(weight_mu[i], weight_stdev[i])
                print "\tdelay mu = {}\t stdev = {}".format(delay_mu[i], delay_stdev[i])
                n_proj_list.append(
                    p.Projection(n_pop_list[i], n_pop_list[j],
                                 p.FixedProbabilityConnector(connect_prob_ex[i][j-2]),#p.OneToOneConnector(),#
                                 synapse, receptor_type="excitatory"))
                n_proj_list.append(
                    p.Projection(n_pop_list[i], n_pop_list[j],
                                 p.FixedProbabilityConnector(connect_prob_in[i][j-2]),#p.OneToOneConnector(),#
                                 synapse, receptor_type="inhibitory"))
                # n_proj_list.append(p.Projection(n_pop_list[i], n_pop_list[j],
                #                                 p.FixedProbabilityConnector(1),
                #                                 synapse, receptor_type="inhibitory"))
    run = 0
    p.run(duration)

    print "finished 1st"

    run = 1
    p.reset()

    p.run(duration)
    total_v = list()
    spikes = list()
    v = list()
    spikes.append(n_pop_list[0].get_data("spikes"))
    spikes.append(n_pop_list[1].get_data("spikes"))
    for j in range(2,no_neuron_pops):
        spikes.append(n_pop_list[j].get_data("spikes"))
        v.append(n_pop_list[j].get_data("v"))

    # p.reset()

    p.end()

    poisson_control.close()
    live_connection.close()

    print "finished run"

    return v, spikes

offset = 0
while offset < 30:
    print "starting agent ", offset
    v, spikes = spinn_net()
    Figure(
        # raster plot of the presynaptic neuron spike times
        Panel(spikes[0].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[1].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[2].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[3].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[4].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[5].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[6].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[no_neuron_pops-2].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        Panel(spikes[no_neuron_pops-1].segments[0].spiketrains,
              yticks=True, markersize=2, xlim=(0, duration)),
        title="Raster plot",
        annotations="Simulated with {}".format(p.name())
    )
    plt.show()
#    plt.close()
    Figure(
        #membrane voltage plots
        Panel(v[0].segments[0].filter(name='v')[0],
              ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        Panel(v[1].segments[0].filter(name='v')[0],
              ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        Panel(v[2].segments[0].filter(name='v')[0],
              ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        Panel(v[3].segments[0].filter(name='v')[0],
              ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        # Panel(v[4].segments[0].filter(name='v')[0],
        #       ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        # Panel(v[no_neuron_pops-4].segments[0].filter(name='v')[0],
        #       ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        # Panel(v[no_neuron_pops-3].segments[0].filter(name='v')[0],
        #       ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
        title="Membrane voltage plot",
    )
    plt.show()
#    plt.close()

    offset += 1

print "finished everything"