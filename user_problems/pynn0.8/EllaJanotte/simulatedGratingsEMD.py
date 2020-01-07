
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 23:19:18 2019

@author: ejanotte
"""

"""
Start point for the ISY project self motion perception
See https://www.cit-ec.de/en/nbs/spiking-insect-vision for more details
"""

# imports

import spynnaker8 as p
from random import *
import ClassSpks as spks
from time import localtime
import numpy as np
import sys
import matplotlib
import matplotlib.pyplot as plt
import pickle
import seaborn as sns
# matplotlib.use('TkAgg')
blob = 20


class Sizes:
    pass

    edge_dvs = 128
    edge_sptc = 32
    edge_semd = 32
    pop_dvs = edge_dvs ** 2 * 2
    pop_sptc = edge_sptc ** 2
    pop_semd = edge_semd ** 2


N_AER_ADRESSES = Sizes.edge_dvs ** 2 * 2

# neuron parameters
cell_params_semd = {'cm': 0.25,
                    'i_offset': 0,  # offset current
                    'tau_m': 10,  # membrane potential time constant	10 default
                    'tau_refrac': 1,  # refractory period time constant
                    'tau_syn_E': 20,  # excitatory current time constant was 20
                    'tau_syn_I': 20,  # inhibitory current time constant was 20
                    'v_reset': -85,  # reset potential
                    'v_rest': -60,  # resting potential
                    'v_thresh': -50  # spiking threshold
                    }

cell_params_sptc = {'cm': 0.25,
                    'i_offset': 0,  # offset current
                    'tau_m': 10,  # membrane potential time constant [ms]
                    'tau_refrac': 1,  # refractory period time constant [ms]
                    'tau_syn_E': 20,  # excitatory current time constant [ms]
                    'tau_syn_I': 20,  # inhibitory current time constant [ms]
                    'v_reset': -85,  # reset potential
                    'v_rest': -60,  # resting potential
                    'v_thresh': -50  # spiking threshold
                    }

AEDATresolution = [128, 128]

grate = range(0, 127,32)
steps = [1000.0/(32.0*2.5)]
for step in steps:
    stamp = 1;  # 1 milliseconds
    hor_EventsON = [[[] for i in range(AEDATresolution[0])] for j in range(AEDATresolution[1])]
    for x in range(AEDATresolution[0]):
        for y in range(0, AEDATresolution[0]):
            for i in grate:
                b = x+i
                if b<128:
                    hor_EventsON[b][y].append(stamp+ randint(0,3))  # vertical
                elif b>= 128 and b <256:
                    hor_EventsON[b-128][y].append(stamp+ randint(0,3))  # vertical
                else:
                    hor_EventsON[b - 256] [y].append(stamp+ randint(0,3))  # vertical
        stamp = int(step) + stamp
    entryHor = []

    for x in range(128):
        for y in range(128):
            entryHor.append(hor_EventsON[x][y])

    RecordONHor = {'spike_times': entryHor}




frequencies = [ 0.1, 0.5,  1.0,2.5, 5.0,10.0]
maxal = [20, 50,100]
for i in range(len(maxal)):
    maxi = maxal[i]



    freq = frequencies[3]
    # dT = int(frequencies[i]*10)
    ins = RecordONHor
    spikeTrain = spks.spks()

    ## neurons
    class Weights:
        pass

        sptc = 0.2  # was 0.6
        semd = 0.5  # was 0.4




    delay = 1
    delayFac = 1

    ## recorded input
    maxTimestamp = 0
    minTimestamp = sys.maxsize
    aedatLength = 0
    endTime = 0

    # set up simulation
    simulation_timestep = 1  # ms
    simulation_runtime = 1000  # ms 5000
    p.setup(timestep=simulation_timestep)
    p.set_number_of_neurons_per_core(p.extra_models.IF_curr_exp_sEMD, 20)  # was 100 for SpiNN3
    p.set_number_of_neurons_per_core(p.IF_curr_exp, maxi)  # was 100 SpiNN3
    p.set_number_of_neurons_per_core(p.SpikeSourceArray, 100)



    class Populations:
        pass

        dvs = p.Population(AEDATresolution[0] ** 2, p.SpikeSourceArray, ins, label='Input')

        semd_lr = p.Population(Sizes.pop_semd, p.extra_models.IF_curr_exp_sEMD, cell_params_semd, label="sEMD lr")
        semd_rl = p.Population(Sizes.pop_semd, p.extra_models.IF_curr_exp_sEMD, cell_params_semd, label="sEMD rl")
        semd_tb = p.Population(Sizes.pop_semd, p.extra_models.IF_curr_exp_sEMD, cell_params_semd, label="sEMD tb")
        semd_bt = p.Population(Sizes.pop_semd, p.extra_models.IF_curr_exp_sEMD, cell_params_semd, label="sEMD bt")
        sptc = p.Population(Sizes.pop_sptc, p.IF_curr_exp, cell_params_sptc, label="SPTC")




    # connection matrix

    # prepare connection matrix between dvs and sptc
    scaling_factor = Sizes.edge_dvs / Sizes.edge_sptc
    sptc = np.arange(Sizes.pop_sptc)
    sptc.resize(Sizes.edge_sptc, Sizes.edge_sptc)
    sptc = np.rot90(sptc, 0)
    sptc = np.kron(sptc, np.ones((int(scaling_factor), int(scaling_factor))))
    sptc.resize(Sizes.pop_dvs // 2)

    a = range(31,32**2, 32)
    b = range(0, 32**2, 32)
    class Connect:
        pass
        sptc = [(i, sptc[i], Weights.sptc, delay) for i in range(Sizes.pop_dvs // 2)]
        semd_lr_fac = [(i, i, Weights.semd, delayFac) for i in range(Sizes.pop_semd)]
        semd_lr_fac = np.delete(semd_lr_fac, a, 0)
        semd_lr_trig = [(i + 1, i, Weights.semd, delay) for i in range(Sizes.pop_semd)]
        semd_lr_trig = np.delete(semd_lr_trig, a, 0)
        semd_rl_fac = [(i + 1, i, Weights.semd, delayFac) for i in range(Sizes.pop_semd)]
        semd_rl_fac = np.delete(semd_rl_fac, b, 0)
        semd_rl_trig = [(i, i, Weights.semd, delay) for i in range(Sizes.pop_semd)]
        semd_rl_trig = np.delete(semd_rl_trig, b, 0)
        semd_tb_fac = [(i, i, Weights.semd, delayFac) for i in range(Sizes.pop_semd-32)]
        semd_tb_trig = [(i + 32, i, Weights.semd, delay) for i in range(Sizes.pop_semd-32)]
        semd_bt_fac = [(i + 32, i, Weights.semd, delayFac) for i in range(Sizes.pop_semd-32)]
        semd_bt_trig = [(i, i, Weights.semd, delay) for i in range(Sizes.pop_semd-32)]


    # projections
    p.Projection(Populations.dvs, Populations.sptc, p.FromListConnector(Connect.sptc), \
                 p.StaticSynapse(), receptor_type='excitatory')
    p.Projection(Populations.sptc, Populations.semd_lr, p.FromListConnector(Connect.semd_lr_fac) \
                 , p.StaticSynapse(), receptor_type='excitatory')
    p.Projection(Populations.sptc, Populations.semd_lr, p.FromListConnector(Connect.semd_lr_trig) \
                 , p.StaticSynapse(), receptor_type='excitatory2')
    p.Projection(Populations.sptc, Populations.semd_rl, p.FromListConnector(Connect.semd_rl_fac) \
                 , p.StaticSynapse(), receptor_type='excitatory')
    p.Projection(Populations.sptc, Populations.semd_rl, p.FromListConnector(Connect.semd_rl_trig) \
                 , p.StaticSynapse(), receptor_type='excitatory2')
    p.Projection(Populations.sptc, Populations.semd_tb, p.FromListConnector(Connect.semd_tb_fac) \
                 , p.StaticSynapse(), receptor_type='excitatory')
    p.Projection(Populations.sptc, Populations.semd_tb, p.FromListConnector(Connect.semd_tb_trig) \
                 , p.StaticSynapse(), receptor_type='excitatory2')
    p.Projection(Populations.sptc, Populations.semd_bt, p.FromListConnector(Connect.semd_bt_fac) \
                 , p.StaticSynapse(), receptor_type='excitatory')
    p.Projection(Populations.sptc, Populations.semd_bt, p.FromListConnector(Connect.semd_bt_trig) \
                 , p.StaticSynapse(), receptor_type='excitatory2')


    # records
    Populations.sptc.record(['spikes'])
    Populations.semd_lr.record(['spikes'])#,'gsyn_inh'])
    Populations.semd_rl.record(['spikes'])#,'gsyn_inh'])
    Populations.semd_tb.record(['spikes'])#,'gsyn_inh'])
    Populations.semd_bt.record(['spikes'])  # ,'gsyn_inh'])
    # Populations.semd_bt.record([ 'v'])
    # Populations.semd_lr.record(['v'])
    # Populations.semd_rl.record(['v'])
    # Populations.semd_tb.record([ 'v'])
    # Populations.semd_bt.record(['gsyn_exc'])
    # Populations.semd_lr.record(['gsyn_exc'])
    # Populations.semd_rl.record(['gsyn_exc'])
    # Populations.semd_tb.record(['gsyn_exc'])

    # run simulation
    p.run(simulation_runtime)


    class Data:
        pass

        # receive data from neurons
        sptc_spikes = Populations.sptc.get_data(['spikes'])
        semd_lr_spikes = Populations.semd_lr.get_data(['spikes'])
        semd_rl_spikes = Populations.semd_rl.get_data(['spikes'])
        semd_bt_spikes = Populations.semd_bt.get_data(['spikes'])
        semd_tb_spikes = Populations.semd_tb.get_data(['spikes'])
        # vTB = Populations.semd_tb.get_data(['v'])
        # vBT = Populations.semd_bt.get_data(['v'])
        # vLR = Populations.semd_lr.get_data(['v'])
        # vRL = Populations.semd_rl.get_data(['v'])
        # iTB = Populations.semd_tb.get_data(['gsyn_exc'])
        # iBT = Populations.semd_bt.get_data(['gsyn_exc'])
        # iLR = Populations.semd_lr.get_data(['gsyn_exc'])
        # iRL = Populations.semd_rl.get_data(['gsyn_exc'])



    spikeTrain.bt = Data.semd_bt_spikes.segments[0].spiketrains
    spikeTrain.tb = Data.semd_tb_spikes.segments[0].spiketrains
    spikeTrain.rl = Data.semd_rl_spikes.segments[0].spiketrains
    spikeTrain.lr = Data.semd_lr_spikes.segments[0].spiketrains
    spikeTrain.sptc = Data.sptc_spikes.segments[0].spiketrains

    idt = localtime()  # Local date and time
    name = format(idt.tm_hour)+'_'+format(idt.tm_min)+'simGratingNoisy.pickle'
    with open(name, 'wb') as f:
        pickle.dump(spikeTrain, f)

    fig = plt.figure()
    dirctions = ['tb', 'bt', 'rl', 'lr', 'sptc']

    for i in range(5):
        retina = [[0] * Sizes.edge_semd for a in range(Sizes.edge_semd)]
        trains = spikeTrain.give(dirctions[i])
        for index in range(len(trains)):
            f = []
            neuron = trains[index]
            retina[index // Sizes.edge_semd][index % Sizes.edge_semd] = len(neuron)
        sns.set()
        fig.add_subplot(2, 3, i + 1)
        ax = sns.heatmap(retina, cmap="Blues")
        ax.set_title(dirctions[i])

    p.end()

plt.show()
