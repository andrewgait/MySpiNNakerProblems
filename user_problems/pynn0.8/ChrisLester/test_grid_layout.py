import spynnaker8 as p
from pyNN.random import RandomDistribution, NumpyRNG

import numpy as np

import pickle
import uuid

#rng = NumpyRNG(seed=900307)

N = 10; #Square-root of number of sub-networks
M = 1024; #Size of each sub-network
C = 5; #Connections (directed) from sub-network alpha to sub-network beta.
E = 2; #View/ping points in each sub-network

p.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
p.set_number_of_neurons_per_core(p.IF_curr_exp, 8)
#p.reset()


rng = NumpyRNG(seed=900307)

delay_dist = RandomDistribution('uniform', \
                                [50., 100.], \
                                rng=rng)

connector = p.FixedProbabilityConnector(p_connect=0.25, rng=rng)


neurons = dict()
neurons_connect = dict()
neurons_experi = dict()

for i in range(N):
    for j in range(N):

        neurons[(i,j)] =  p.Population(M - C - E, \
                       p.IF_curr_exp, \
                       {'v_thresh': -57.5, \
                        'tau_refrac': 50., \
                        'tau_m':2.5,  \
                        'tau_syn_E':1.0},\
                       label="pop")

        neurons[(i,j)].record('spikes')

        neurons_connect[(i,j)] =  p.Population(C, \
                       p.IF_curr_exp, \
                       {'v_thresh': -57.5, \
                        'tau_refrac': 50., \
                        'tau_m':2.5,  \
                        'tau_syn_E':1.0},\
                       label="con")

        neurons_connect[(i,j)].record('spikes')

        p.Projection(neurons[(i,j)], neurons[(i,j)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))


        p.Projection(neurons[(i,j)], neurons_connect[(i,j)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))

        p.Projection(neurons_connect[(i,j)], neurons[(i,j)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))

        for k in range(E):
            neurons_experi[(i,j, k)] =  p.Population(1, \
                       p.IF_curr_exp, \
                       {'v_thresh': -57.5, \
                        'tau_refrac': 50., \
                        'tau_m':2.5,  \
                        'tau_syn_E':1.0},\
                       label="exp")

            p.Projection(neurons[(i,j)], neurons_experi[(i,j, k)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))

            p.Projection(neurons_experi[(i,j, k)], neurons[(i,j)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))


            p.Projection(neurons_connect[(i,j)], neurons_experi[(i,j, k)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))

            p.Projection(neurons_experi[(i,j, k)], neurons_connect[(i,j)], \
                                connector, \
                                p.StaticSynapse(weight=25.0, \
                                                delay=delay_dist))


            neurons_experi[(i, j, k)].record('spikes')

for w in [(q1, q2) for q1 in neurons for q2 in neurons if (np.abs(q1[0] - q2[0]) + np.abs(q1[1] - q2[1]))==1]:

     p.Projection(neurons_connect[w[0]], \
                  neurons_connect[w[1]], \
                  p.OneToOneConnector(), \
                  p.StaticSynapse(weight=25.0, \
                                  delay=delay_dist))

ping_source = p.Population(1, p.SpikeSourceArray(spike_times=np.arange(0,50000,150)), label="input")
forcing = p.Projection(ping_source, neurons_experi[(0,0,0)],  p.OneToOneConnector(), \
                              p.StaticSynapse(weight=20., delay=0.))

p.run(2500.0)

#ping_sources = dict()

#forcing = dict()

#for i in range(N):
#    for j in range(N):
#        for k in range(E):
#            ping_sources[(i,j, k)] = p.Population(E, p.SpikeSourceArray(spike_times=np.arange(0,50000,150)), label="input")
            #print ([q for q in ping_sources])
            #print ([q for q in neurons_experi])

#            forcing[(i,j, k)] = p.Projection(ping_sources[(i,j,k)], neurons_experi[(i,j,k)], p.OneToOneConnector(), \
#                              p.StaticSynapse(weight=0., delay=1.5))
#p.run(5000.0)
#for i in range(N):
#    for j in range(N):
#        for k in range(E):
#            p.reset()

#            for l in range(E):
#                if l == k:
#                    forcing[i,j,k].set(weight=20.0)
#                else:
#                    forcing[i,j,l].set(weight=0.0)
    #print neurons_forced.get(["weight", "delay"], format="list")

#            p.run(5000.0)

data = dict()
for q in neurons:
    data[q] = neurons[q].get_data('spikes')
p.end()

pickle.dump(data,open(str(uuid.uuid4())+'.pk', 'wb'))