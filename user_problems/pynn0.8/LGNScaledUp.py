"""
Version uploaded on ModelDB October 2017.
Author:
Basabdatta Sen Bhattacharya, APT group, School of Computer Science, University of Manchester, 2017.

Please cite the original work on the model - details are:

B. Sen-Bhattacharya, T. Serrano-Gotarredona, L. Balassa, A. Bhattacharya, A.B. Stokes, A. Rowley, I. Sugiarto, S.B. Furber, "A spiking neural network model of the Lateral Geniculate Nucleus on the SpiNNaker machine", Frontiers in Neuroscience, vol. 11 (454), 2017.

Free online access: http://journal.frontiersin.org/article/10.3389/fnins.2017.00454/abstract

13th October: I have created this version today to be uploaded on to ModelDB. I am now using this basic template to ceate the oop version of the file.

OK - reporting end of day at 5:30 pm, I have now created the very first instance and provided intra-population projections as well as projections from the spike source.
Now, I need to complete the other functions to visualise the data etc  - keeping the BG class as the template - so need to complete accordingly, as well as build the lattice
after testing this first instance.

The other thing is that I wanted to create two separate functions for the poisson base input and periodic input. this is because the base poisson input is a new thing
that I am introducing and is not there in the original model. So that if required we can isolate this - and also for generic purpose isolation.
Need to define two separate functions for the extrinsic input.

16th October 2017:
This morning, I implemented the above-mentioned plan of two separate functions for background input and periodic input.
And then implemented getDisplaySpikes().
PLANNED JOB ACCOMPLISHED!

PLANS FOR THE WEEK OF 23RD OCTOBER:
(1) TEST THIS FOR MULTIPLE INSTANCES, SAY AROUND 10? OBVIOUSLY, THERE WILL BE NO INTER-NODE CONNECTIVITY
(2) IF SUCCESSFULLY DONE, SAVE AS A DIFFERENT FILE, AND THEN:
(3) CONNECT NODES AS LATTICE, AS DONE FOR THE BG.

23rd-24th - resumed work - actually worked on the single channel instance yesterday, in this folder, called
'SingleLGNChannelOriginalCode.py', and also uploaded a version on modelDB. The Figure-Panel command is very
slow in rendering, and I would rather use the old plot commands. Changing the getDisplay function accordingly.


"""

# !/usr/bin/python

import numpy

import matplotlib.pylab as plt
import pylab
from pylab import *
from pyNN.random import NumpyRNG, RandomDistribution

import spynnaker8 as p
import pyNN.utility.plotting as plot
from pyNN.utility.plotting import Figure, Panel


import time
start_time = time.time()

class lgn_microcol():

    def __init__(self,p,scale_fact):
        self.NumCellsTCR = int(8*scale_fact)
        self.NumCellsIN = int(2*scale_fact)
        self.NumCellsTRN = int(4*scale_fact)


        ''' Initialising Model connectivity parameters'''
        self.intra_pop_delay=4
        self.intra_nucleus_delay = 6
        self.inter_nucleus_delay = 8
        self.inter_pop_delay = 10

        self.tcr_weights = 5
        self.in_weights = 4
        self.input_delay = self.inter_pop_delay


        self.p_in2tcr=0.232
        self.p_trn2tcr=0.077###WHICH IS 1/4th of 0.309 THIS IS KEPT AT A REDUCED VALUE UNDER NORMAL SIMULATIONS - HOWEVER, FOR REDUCED EFFECT OF IN, THIS IS INCREASED TO 0.232 WHICH IS 3/4TH OF 30.9

        self.w_tcr2trn = 3.0
        self.w_trn2tcr = 2.0
        self.w_trn2trn = 2.0
        self.w_in2tcr= 8.0##SET TO 1 WHEN TESTING FOR REDUCED EFFECT OF THE IN ALONG WITH REDUCING P_IN2TCR
        self.w_in2in = 2.0

        ''' Initialising Izhikevich spiking neuron model parameters.
        We have used the current-based model here.'''

        # Tonic mode parameters
        self.tcr_a_tonic = 0.02
        self.tcr_b_tonic = 0.2
        self.tcr_c_tonic = -65.0
        self.tcr_d_tonic = 6.0
        self.tcr_v_init_tonic = -65.0

        self.in_a_tonic = 0.1
        self.in_b_tonic = 0.2
        self.in_c_tonic = -65.0
        self.in_d_tonic = 6.0
        self.in_v_init_tonic = -70.0

        self.trn_a_tonic = 0.02
        self.trn_b_tonic = 0.2
        self.trn_c_tonic = -65.0
        self.trn_d_tonic = 6.0
        self.trn_v_init_tonic = -75.0

        self.tcr_u_init_tonic = self.tcr_b_tonic * self.tcr_v_init_tonic
        self.in_u_init_tonic = self.in_b_tonic * self.in_v_init_tonic
        self.trn_u_init_tonic = self.trn_b_tonic * self.trn_v_init_tonic

        self.current_Pulse = 0.0 ##a constant dc bias current; this is used here for testing the RS and FS characteristics of IZK neurons
        self.tau_ex = 1.7 ### excitatory input time constant
        self.tau_inh= 2.5 ### inhibitory input time constant

        '''Defining each cell type as dictionary'''

        # THALAMOCORTICAL RELAY CELLS (TCR)

        self.TCR_cell_params = {'a': self.tcr_a_tonic, 'b': self.tcr_b_tonic, 'c': self.tcr_c_tonic,
                                'd': self.tcr_d_tonic, 'v_init': self.tcr_v_init_tonic, 'u_init': self.tcr_u_init_tonic, 								'tau_syn_E': self.tau_ex, 'tau_syn_I': self.tau_inh,
                                'i_offset': self.current_Pulse
                                }

        # THALAMIC INTERNEURONS (IN)

        self.IN_cell_params = {'a': self.in_a_tonic, 'b': self.in_b_tonic, 'c': self.in_c_tonic,
                                'd': self.in_d_tonic, 'v_init': self.in_v_init_tonic, 'u_init': self.in_u_init_tonic, 								'tau_syn_E': self.tau_ex, 'tau_syn_I': self.tau_inh,
                                'i_offset': self.current_Pulse
                                }

        # THALAMIC RETICULAR NUCLEUS (TRN)

        self.TRN_cell_params = {'a': self.trn_a_tonic, 'b': self.trn_b_tonic, 'c': self.trn_c_tonic,
                                'd': self.trn_d_tonic, 'v_init': self.trn_v_init_tonic, 'u_init': self.trn_u_init_tonic,
                                'tau_syn_E': self.tau_ex, 'tau_syn_I': self.tau_inh,
                                'i_offset': self.current_Pulse
                           }

        '''Creating populations of each cell type'''
        self.TCR_pop = p.Population(self.NumCellsTCR, p.Izhikevich(**self.TCR_cell_params), label='TCR_pop')
        self.IN_pop = p.Population(self.NumCellsIN, p.Izhikevich(**self.IN_cell_params), label='IN_pop')
        self.TRN_pop = p.Population(self.NumCellsTRN, p.Izhikevich(**self.TRN_cell_params), label='TRN_pop')


        '''TCR2TRN'''
        self.Proj1 = p.Projection(self.TCR_pop, self.TRN_pop, p.FixedProbabilityConnector(p_connect=0.35), synapse_type=p.StaticSynapse(weight=self.w_tcr2trn, delay=self.inter_nucleus_delay), receptor_type='excitatory')


        '''TRN2TCR'''
        self.Proj2 = p.Projection(self.TRN_pop, self.TCR_pop, p.FixedProbabilityConnector(p_connect=self.p_trn2tcr), synapse_type=p.StaticSynapse(weight=self.w_trn2tcr, delay=self.inter_nucleus_delay), receptor_type='inhibitory')


        '''TRN2TRN'''
        self.Proj3 = p.Projection(self.TRN_pop, self.TRN_pop, p.FixedProbabilityConnector(p_connect=0.2), synapse_type=p.StaticSynapse(weight=self.w_trn2trn, delay=self.intra_pop_delay), receptor_type='inhibitory')


        '''IN2TCR'''
        self.Proj4 = p.Projection(self.IN_pop, self.TCR_pop, p.FixedProbabilityConnector(p_connect=self.p_in2tcr), synapse_type=p.StaticSynapse(weight=self.w_in2tcr, delay=self.intra_nucleus_delay), receptor_type='inhibitory')


        '''IN2IN'''
        self.Proj5  = p.Projection(self.IN_pop, self.IN_pop, p.FixedProbabilityConnector(p_connect=0.236), synapse_type=p.StaticSynapse(weight=self.w_in2in, delay=self.intra_pop_delay), receptor_type='inhibitory')


    def recordData(self, spikepoissoninput, spikeperiodicinput):

        self.TCR_pop.record(['v', 'spikes'])
        self.IN_pop.record(['v', 'spikes'])
        self.TRN_pop.record(['v', 'spikes'])
        spikepoissoninput.record(['spikes'])
        spikeperiodicinput.record(['spikes'])


def baseExtrinsicInput(p, lgn_module, rate_Poisson_Inp_base, start_Poisson_Inp_base, duration_Poisson_Inp_base, numBasePoissonInput):
    spike_source_Poisson_base = p.Population(numBasePoissonInput, p.SpikeSourcePoisson,
                                                   {'rate': rate_Poisson_Inp_base,
                                                    'duration': duration_Poisson_Inp_base,
                                                    'start': start_Poisson_Inp_base},
                                                   label='spike_source_Poisson_base')

    p.Projection(spike_source_Poisson_base, lgn_module.TCR_pop,
                 p.FixedProbabilityConnector(p_connect=0.07),
                 synapse_type=p.StaticSynapse(weight=lgn_module.tcr_weights, delay=lgn_module.input_delay),
                 receptor_type='excitatory')

    p.Projection(spike_source_Poisson_base, lgn_module.IN_pop,
                 p.FixedProbabilityConnector(p_connect=0.47),
                 synapse_type=p.StaticSynapse(weight=lgn_module.in_weights, delay=lgn_module.input_delay),
                 receptor_type='excitatory')

    return spike_source_Poisson_base



def PeriodicInput(p, lgn_module, Start_Inp, End_Inp, Inp_isi, numPeriodicInput):
    spike_source_Periodic = p.Population(numPeriodicInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp, End_Inp, Inp_isi)]},
                                         label='spike_source_Periodic')

    p.Projection(spike_source_Periodic, lgn_module.TCR_pop,
                 p.FixedProbabilityConnector(p_connect=0.07),
                 synapse_type=p.StaticSynapse(weight=lgn_module.tcr_weights, delay=lgn_module.input_delay),
                 receptor_type='excitatory')

    p.Projection(spike_source_Periodic, lgn_module.IN_pop,
                 p.FixedProbabilityConnector(p_connect=0.47),
                 synapse_type=p.StaticSynapse(weight=lgn_module.in_weights, delay=lgn_module.input_delay),
                 receptor_type='excitatory')

    return spike_source_Periodic


def getDisplaySpikes(lgn_module):
    print 'within getdisplay function'

    # periodicsource_spikes = spike_source_periodic.spinnaker_get_data("spikes")
    # poissonsource_spikes = spike_source_poisson_base.spinnaker_get_data("spikes")
    TCR_spikes = lgn_module.TCR_pop.spinnaker_get_data("spikes")
    IN_spikes = lgn_module.IN_pop.spinnaker_get_data("spikes")
    TRN_spikes = lgn_module.TRN_pop.spinnaker_get_data("spikes")

    # extracting the membrane potential data (in millivolts)
    # TCR_membrane_volt = lgn_module.TCR_pop.spinnaker_get_data("v")
    # IN_membrane_volt = lgn_module.IN_pop.spinnaker_get_data("v")
    # TRN_membrane_volt = lgn_module.TRN_pop.spinnaker_get_data("v")

    # f0 = plt.plot(poissonsource_spikes[:, 1], poissonsource_spikes[:, 0], '.')

    f1 = plt.plot(TCR_spikes[:, 1], TCR_spikes[:, 0], '.')


    f2 = plt.plot(IN_spikes[:, 1], IN_spikes[:, 0], '.')


    f3 = plt.plot(TRN_spikes[:, 1], TRN_spikes[:, 0], '.')

    plt.show()

if __name__ == "__main__":
    TotalDuration=10000 ## total duration of simulation
    time_resol = 0.1 ## time-step of model equation solver
    TimeInt=1/time_resol
    rate_Poisson_Inp_base = 3
    start_Poisson_Inp_base = p.RandomDistribution("uniform", [500, 700])
    print start_Poisson_Inp_base
    duration_Poisson_Inp_base = 9200  ####TotalDuration

    Duration_Inp = 9900### this is in ms.
    Start_Inp = 700 ###p.RandomDistribution("uniform", [500, 700])###50  ##50 ms at both start and end are disregarded to avoid transients

    End_Inp = Start_Inp + Duration_Inp
    Rate_Inp = 10 ## setting the input frequency of the spike train input
    Inp_isi = (int(1000/Rate_Inp))
    scale_fact = 10
    numBasePoissonInput = 80##p.RandomDistribution("uniform", [10, 20])
    numPeriodicInput = 80##p.RandomDistribution("uniform", [10, 20])
    p.setup(timestep=time_resol, min_delay=1, max_delay=int(144*time_resol))
    lgn_node = lgn_microcol(p, scale_fact)
    spikepoissoninput = baseExtrinsicInput(p, lgn_node, rate_Poisson_Inp_base, start_Poisson_Inp_base, duration_Poisson_Inp_base, numBasePoissonInput)
    spikeperiodicinput = PeriodicInput(p, lgn_node, Start_Inp, End_Inp, Inp_isi, numPeriodicInput)
    lgn_node.recordData(spikepoissoninput, spikeperiodicinput)
    p.run(TotalDuration)
    print("--- %s SECONDS ELAPSED ---\n \n \n" % (time.time() - start_time))
    getDisplaySpikes(lgn_node)

    p.end()
