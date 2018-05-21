import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import time
import copy
import pylab
import numpy as np
import threading
from threading import Condition
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pyNN.random import RandomDistribution# as rand
#import spynnaker8.spynakker_plotting as splot

input_labels = list()
output_labels = list()
no_neuron_pops = 9
pop_size = 250
poisson_rate = 50
time_segments = 200
average_runtime = 0.1
duration = 2000

motor_spikes = [0 for i in range(1)]
def receive_spikes(label, time, neuron_ids):
    for neuron_id in neuron_ids:
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

def spinn_net():
    global output_labels
    global input_labels
    p.setup(timestep=1.0, min_delay=1, max_delay=60)
    p.set_number_of_neurons_per_core(p.IF_cond_exp, 64)
    n_pop_labels = []
    n_pop_list = []
    n_proj_list = []
    if offset != 0:
        for i in range(2):
            del output_labels[0]
        for i in range(2):
            del input_labels[0]
    for i in range(no_neuron_pops):
        #set up the input as a live spike source
        if i < 2:
            n_pop_labels.append("Input_pop{}".format(i))
            input_labels.append("Input_pop{}".format(i))
            n_pop_list.append(
                p.Population(pop_size, p.SpikeSourcePoisson(rate=poisson_rate),
                             label=n_pop_labels[i]))
            #n_pop_list[i].record(["spikes"])
            p.external_devices.add_poisson_live_rate_control(
                n_pop_list[i], database_notify_port_num=(16000+offset))
        #set up output pop
        elif i < 4:
            n_pop_labels.append("Output_pop{}".format(i))
            output_labels.append("Output_pop{}".format(i))
            n_pop_list.append(p.Population(pop_size, p.IF_cond_exp(),
                                           label=n_pop_labels[i]))
            p.external_devices.activate_live_output_for(
                n_pop_list[i], database_notify_port_num=(18000+offset),
                port=(17000+offset))
            #n_pop_list[i].record(["spikes", "v"])
        #set up all other populations
        else:
            n_pop_labels.append("neuron{}".format(i))
            n_pop_list.append(p.Population(pop_size, p.IF_cond_exp(),
                                           label=n_pop_labels[i]))
            #n_pop_list[i].record(["spikes", "v"])



    poisson_control = p.external_devices.SpynnakerPoissonControlConnection(
        poisson_labels=input_labels, local_port=(16000+offset))
    poisson_control.add_start_callback(n_pop_list[0].label, poisson_setting)
    poisson_control.add_start_callback(n_pop_list[1].label, poisson_setting)
    # poisson_control.add_start_callback(n_pop_list[0].label, poisson_threading)



    live_connection = p.external_devices.SpynnakerLiveSpikesConnection(
        receive_labels=output_labels, local_port=(18000+offset))
    live_connection.add_receive_callback(n_pop_labels[2], receive_spikes)
    live_connection.add_receive_callback(n_pop_labels[3], receive_spikes)



    weight_mu = 0.015
    weight_sdtev = 0.05
    delay_mu = 40
    delay_sdtev = 5
    weights = RandomDistribution("normal_clipped", mu=weight_mu,
                                 sigma=weight_sdtev, low=0, high=np.inf)
    delays = RandomDistribution("normal_clipped", mu=delay_mu,
                                sigma=delay_sdtev, low=1, high=55)
    synapse = p.StaticSynapse(weight=weights, delay=delays)
    for i in range(no_neuron_pops):
        for j in range(2, no_neuron_pops):
            if i != j:
                n_proj_list.append(
                    p.Projection(n_pop_list[i], n_pop_list[j],
                                 p.FixedProbabilityConnector(1e-3),#p.OneToOneConnector(),#
                                 synapse, receptor_type="excitatory"))
                n_proj_list.append(
                    p.Projection(n_pop_list[i], n_pop_list[j],
                                 p.FixedProbabilityConnector(1e-3),#p.OneToOneConnector(),#
                                 synapse, receptor_type="inhibitory"))
                # n_proj_list.append(p.Projection(n_pop_list[i], n_pop_list[j],
                #                                 p.FixedProbabilityConnector(1),
                #                                 synapse, receptor_type="inhibitory"))

    p.run(duration)

    print "finished 1st"

#    p.reset()

    p.run(duration)
    # total_v = list()
    # spikes = list()
    # v = list()
    # spikes.append(n_pop_list[0].get_data("spikes"))
    # for j in range(1,no_neuron_pops):
    #     spikes.append(n_pop_list[j].get_data("spikes"))
    #     v.append(n_pop_list[j].get_data("v"))
    # Figure(
    #     # raster plot of the presynaptic neuron spike times
    #     Panel(spikes[0].segments[0].spiketrains,
    #           yticks=True, markersize=2, xlim=(0, duration)),
    #     Panel(spikes[1].segments[0].spiketrains,
    #           yticks=True, markersize=2, xlim=(0, duration)),
    #     Panel(spikes[2].segments[0].spiketrains,
    #           yticks=True, markersize=2, xlim=(0, duration)),
    #     Panel(spikes[3].segments[0].spiketrains,
    #           yticks=True, markersize=2, xlim=(0, duration)),
    #     # Panel(spikes[4].segments[0].spiketrains,
    #     #       yticks=True, markersize=2, xlim=(0, duration)),
    #     title="Raster plot",
    #     annotations="Simulated with {}".format(p.name())
    # )
    # plt.show()
    # Figure(
    #     #membrane voltage plots
    #     Panel(v[0].segments[0].filter(name='v')[0],
    #           ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
    #     Panel(v[1].segments[0].filter(name='v')[0],
    #           ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
    #     Panel(v[2].segments[0].filter(name='v')[0],
    #           ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
    #     Panel(v[3].segments[0].filter(name='v')[0],
    #           ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
    #     # Panel(v[4].segments[0].filter(name='v')[0],
    #     #       ylabel="Membrane potential (mV)", yticks=True, xlim=(0, duration)),
    #     title="Membrane voltage plot",
    # )
    # plt.show()

#    p.reset()

    p.end()

    poisson_control.close()
    live_connection.close()

    print "finished run"

offset = 0
while offset < 20:
    print "starting agent ", offset
    spinn_net()
    offset += 1

print "finished everything"