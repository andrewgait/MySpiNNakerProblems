import spynnaker8 as p
import matplotlib.pyplot as plt
import numpy as np
from numpy import *
import time
from pyNN.random import RandomDistribution, NumpyRNG
start_time = time.time()

from spinn_front_end_common.utilities import globals_variables
from quantities import ms
import neo

#for plotting
from pyNN.utility.plotting import Figure, Panel, Histogram
# get_ipython().run_line_magic('matplotlib', 'inline')

TotalDuration = 1000 ####10000  ### TOTAL RUN TIME
TimeInt = 0.1    ### SIMULATION TIME STEP
TotalDataPoints = int(TotalDuration*(1/TimeInt))
countt=4
reward_value=0.05

print(TotalDataPoints)

'''DEFINING FUNCTIONS FOR DATA STRUCTURING AND SAVING'''
my_resol = 1000## 1000 DATAPOINTS IS EQUIVALENT TO 100 MS
checkpoint = int(TotalDataPoints/my_resol) ## checking for each 100 ms


def my_condition(x, lower_bound, upper_bound):
    return x>=lower_bound and x<upper_bound

def my_firingrate(my_data, checkpoint, my_resol):
    global countt
    lower_bound = 0
    my_hist = np.zeros((checkpoint))
    for loop in range(0,checkpoint):
        upper_bound = lower_bound + my_resol
        my_hist[loop] = sum(1 for x in my_data if my_condition(x, lower_bound, upper_bound))
        if countt > 0:
            print("my_hist[loop]",my_hist[loop])
            countt=countt-1
    #     y[lower_bound:upper_bound]=my_hist[loop] ## assigning same values to the indices in the filler zone
        lower_bound = upper_bound
    return my_hist/100

# print(checkpoint)
# p.end()

Duration_Inp_train = 9200### this is in ms.
Start_Inp_train = 1000 ###p.RandomDistribution("uniform", [500, 700])###50  ##50 ms at both start and end are disregarded to avoid transients
rng = np.random.default_rng(85524)
Start_Inp_train = rng.integers(low=500, high=700)
End_Inp_train = Start_Inp_train + Duration_Inp_train
Rate_Inp_train1 = 14 ## setting the input frequency of the spike train input
Rate_Inp_train2 = 15
Rate_Inp_train3 = 16
Rate_Inp_base=3

Inp_isi_train1 = (int(1000/Rate_Inp_train1))
Inp_isi_train2 = (int(1000/Rate_Inp_train2))
Inp_isi_train3 = (int(1000/Rate_Inp_train3))
Inp_isi_base=(int(1000/Rate_Inp_base))

'''PARAMETERS USED IN DEFINING THE BASIC MODEL UNITS: IZHIKEVICH NEURONS'''
tau_ampa = 6.0### ampa synapse time constant
E_ampa = 0.0 ## ampa synapse reversal potential


tau_gabaa= 4.0### gaba synapse time constant
E_gabaa = -80.0 ## gaba synapse reversal potential

strd1_a=0.02
strd1_b=0.2
strd1_c=-65.0
strd1_d=8.0
strd1_v_init = -80.0
strd1_u_init = strd1_b * strd1_v_init


strd2_a=0.02
strd2_b=0.2
strd2_c=-65.0
strd2_d=8.0
strd2_v_init = -80.0
strd2_u_init = strd2_b * strd2_v_init

current_bias_str = -30.0

fsi_a=0.1
fsi_b=0.2
fsi_c=-65.0
fsi_d=8.0
fsi_v_init = -70.0
fsi_u_init = fsi_b * fsi_v_init

current_bias_fsi = -10.0

gpe_a=0.005
gpe_b=0.585
gpe_c=-65.0
gpe_d=4.0
gpe_v_init = -70.0
gpe_u_init = gpe_b * gpe_v_init

current_bias_gpe = 2.0

snr_a = 0.005
snr_b = 0.32
snr_c = -65.0
snr_d = 2.0
snr_v_init = -70.0
snr_u_init = snr_b * snr_v_init

current_bias_snr = 5.0

stn_a=0.005
stn_b=0.265
stn_c=-65.0
stn_d=2.0
stn_v_init = -60.0
stn_u_init = stn_b * stn_v_init

current_bias_stn = 5.0

snc_a=0.0025
snc_b=0.2
snc_c=-55
snc_d=2
snc_v_init=-70.0
snc_u_init = snc_b * snc_v_init

current_bias_snc = 4.65 ###in literature 9.0

'''SETTING NUMBER OF NEURONS PER CHANNEL'''

numCellsPerCol_STR = 1255 ##1255 #### 90% of 50% of 2790000 = 1255500
numCellsPerCol_FSI = 84####139
numCellsPerCol_STN = 14 ###13560
numCellsPerCol_SNR = 27 ####26320
numCellsPerCol_GPe = 46 ###45960
numCellsPerCol_SNC=8
numPoissonInput = 25
plastic_weights=1.5

'''NOW START RUNNING MULTIPLE TRIALS, AND INITIALISE THE ARRAYS'''
numtrials = 1

gpe_hist1 = np.zeros((numtrials, checkpoint))
snr_hist1 = np.zeros((numtrials, checkpoint))
stn_hist1 = np.zeros((numtrials, checkpoint))
fsi_hist1 = np.zeros((numtrials, checkpoint))

def create_network(phi_max_dop,g_cort2strd1, g_cort2strd2, g_cort2fsi, g_cort2stn,g_strd12snr,
                   g_strd22gpe,g_str2str,g_gpe2stn,
                   g_gpe2gpe,g_gpe2snr,g_gpe2fsi,g_gaba_snr,g_snr2snr,g_stn2snr_diffuse,
                   g_stn2gpe_diffuse,Rate_Poisson_Inp_train):
    '''NOW START RUNNING MULTIPLE TRIALS, AND INITIALISE THE ARRAYS'''
    numtrials = 1

    gpe_hist1 = np.zeros((numtrials, checkpoint))
    snr_hist1 = np.zeros((numtrials, checkpoint))
    stn_hist1 = np.zeros((numtrials, checkpoint))
    strd1_hist1=np.zeros((numtrials, checkpoint))
    strd2_hist1=np.zeros((numtrials, checkpoint))

    fsi_hist1 = np.zeros((numtrials, checkpoint))


    Base_3hzprojections_in_channel1=[]
    spike_source_Periodic_train14=[]
    spike_source_Periodic_train15=[]
    spike_source_Periodic_train16=[]

    for thisTrial in range(0, numtrials):

        ''' SET UP SPINNAKER AND BEGIN SIMULATION'''
        p.setup(timestep=0.1)
        p.set_number_of_neurons_per_core(p.extra_models.IZK_cond_exp_izhikevich_neuromodulation,20)

        '''STRIATUM OF THE BASAL GANGLIA: MEDIUM SPINY NEURONS (MSN - D1 / D2)'''

        strd1_cell_params = {'a': strd1_a,
                             'b': strd1_b,
                             'c': strd1_c,
                             'd': strd1_d,
                             'v': strd1_v_init,
                             'u': strd1_u_init,
                             'tau_syn_E': tau_ampa,
                             'tau_syn_I': tau_gabaa,
                             'i_offset': current_bias_str,
                             'isyn_exc': E_ampa,
                             'isyn_inh': E_gabaa
                            }

        strd2_cell_params = {'a': strd2_a,
                             'b': strd2_b,
                             'c': strd2_c,
                             'd': strd2_d,
                             'v': strd2_v_init,
                             'u': strd2_u_init,
                             'tau_syn_E': tau_ampa,
                             'tau_syn_I': tau_gabaa,
                             'i_offset': current_bias_str,
                             'isyn_exc': E_ampa,
                             'isyn_inh': E_gabaa
                            }

        '''FAST SPIKING INTERNEURONS OF THE STRIATUM'''

        fsi_cell_params = { 'a': fsi_a,
                            'b': fsi_b,
                            'c': fsi_c,
                            'd': fsi_d,
                            'v': fsi_v_init,
                            'u': fsi_u_init,
                            'tau_syn_E': tau_ampa,
                            'tau_syn_I': tau_gabaa,
                            'i_offset': current_bias_fsi,
                            'isyn_exc': E_ampa,
                            'isyn_inh': E_gabaa
                         }


        '''GLOBAL PALLIDUS - EXTERNA OF THE BASAL GANGLIA'''

        gpe_cell_params = {'a': gpe_a,
                           'b': gpe_b,
                           'c': gpe_c,
                           'd': gpe_d,
                           'v': gpe_v_init,
                           'u': gpe_u_init,
                           'tau_syn_E': tau_ampa,
                           'tau_syn_I': tau_gabaa,
                           'i_offset': current_bias_gpe,
                           'isyn_exc': E_ampa,
                           'isyn_inh': E_gabaa
                           }


        '''SUBSTANTIA NIAGRA OF THE BASAL GANGLIA'''

        snr_cell_params = {'a': snr_a,
                           'b': snr_b,
                           'c': snr_c,
                           'd': snr_d,
                           'v': snr_v_init,
                           'u': snr_u_init,
                           'tau_syn_E': tau_ampa,
                           'tau_syn_I': tau_gabaa,
                           'i_offset': current_bias_snr,
                           'isyn_exc': E_ampa,
                           'isyn_inh': E_gabaa
                         }

        '''SUB-THALAMIC NUCLEUS OF THE BASAL GANGLIA'''

        stn_cell_params = {'a': stn_a,
                           'b': stn_b,
                           'c': stn_c,
                           'd': stn_d,
                           'v': stn_v_init,
                           'u': stn_u_init,
                           'tau_syn_E': tau_ampa,
                           'tau_syn_I': tau_gabaa,
                           'i_offset': current_bias_stn,
                           'isyn_exc': E_ampa,
                           'isyn_inh': E_gabaa
                          }
        snc_cell_params = {'a': snc_a,
                       'b': snc_b,
                       'c': snc_c,
                       'd': snc_d,
                       'v': snc_v_init,
                       'u': snc_u_init,
                       'tau_syn_E': tau_ampa,
                       'tau_syn_I': tau_gabaa,
                       'i_offset': current_bias_snc,
                       'isyn_exc': E_ampa,
                       'isyn_inh': E_gabaa
                      }


        ''' THE FIRST CHANNEL'''
#         strd1_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.IZK_cond_exp_izhikevich_neuromodulation, strd1_cell_params, label='strd1_pop1')
#         strd2_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.IZK_cond_exp_izhikevich_neuromodulation, strd2_cell_params, label='strd2_pop1')
        gpe_pop1 = p.Population(numCellsPerCol_GPe, p.extra_models.Izhikevich_cond, gpe_cell_params, label='gpe_pop1')
        snr_pop1 = p.Population(numCellsPerCol_SNR, p.extra_models.Izhikevich_cond, snr_cell_params, label='snr_pop1')
        stn_pop1 = p.Population(numCellsPerCol_STN, p.extra_models.Izhikevich_cond, stn_cell_params, label='stn_pop1')
        fsi1_pop1 = p.Population(numCellsPerCol_FSI, p.extra_models.Izhikevich_cond, fsi_cell_params, label='fsi1_pop1')


        ''' THE SECOND CHANNEL'''


        ''' THE THIRD CHANNEL'''


        '''SETTING THE DOPAMINE LEVELS AND CONDUCTANCE PARAMETERS'''

        '''SETTING NETWORK CONDUCTANCE PARAMETERS'''



        #################DEFINING DISTRIBUTION OF DELAY PARAMETERS
#       intra_pop_delay = RandomDistribution('uniform', (1,3), rng=NumpyRNG(seed=85520))

        distr_strd1=RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))

#    # distr_strd1 = p.RandomDistribution("uniform", [9, 12])

        distr_strd2 = RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85521))#p.RandomDistribution("uniform", [9, 12])

        distr_stn = RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85522))#p.RandomDistribution("uniform", [9, 12])

        distr_fsi  = RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85523))#p.RandomDistribution("uniform", [9, 12])

        pconn_cort2str = 0.15
        pconn_cort2stn = 0.2

#         poplist_ch1 = [strd1_pop1, strd2_pop1, fsi1_pop1, stn_pop1]

        g_pop = [g_cort2strd1, g_cort2strd2, g_cort2fsi, g_cort2stn]
        distr_pop = [distr_strd1, distr_strd2, distr_fsi, distr_stn]

        if(Rate_Poisson_Inp_train==14):

            spike_source_Periodic_train14_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           End_Inp_train,
                                                                           Inp_isi_train1)]},
                                         label='spike_source_Periodic_14_1')
            spike_source_Periodic_train14_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           End_Inp_train,
                                                                           Inp_isi_train1)]},
                                         label='spike_source_Periodic_14_2')


            spike_source_Periodic_train15_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_15_1')
            spike_source_Periodic_train15_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_15_2')
            spike_source_Periodic_train16_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_16_1')
            spike_source_Periodic_train16_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_16_2')




        elif(Rate_Poisson_Inp_train==15):
            spike_source_Periodic_train14_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_14_1')
            spike_source_Periodic_train14_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_14_2')


            spike_source_Periodic_train15_first = p.Population(numPoissonInput,
                                                               p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           End_Inp_train,
                                                                           Inp_isi_train2)]},
                                         label='spike_source_Periodic_15_1')
            spike_source_Periodic_train15_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           End_Inp_train,
                                                                           Inp_isi_train2)]},
                                         label='spike_source_Periodic_15_2')
            spike_source_Periodic_train16_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_16_1')

            spike_source_Periodic_train16_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_16_2')


        elif(Rate_Poisson_Inp_train==16):
            spike_source_Periodic_train14_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_14_1')
            spike_source_Periodic_train14_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_14_2')


            spike_source_Periodic_train15_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_15_1')
            spike_source_Periodic_train15_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           Start_Inp_train+1,
                                                                           1)]},
                                         label='spike_source_Periodic_15_2')


            spike_source_Periodic_train16_first = p.Population(numPoissonInput, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           End_Inp_train,
                                                                           Inp_isi_train3)]},
                                         label='spike_source_Periodic_16_1')
            spike_source_Periodic_train16_second = p.Population(2, p.SpikeSourceArray,
                                         {'spike_times': [i for i in range(Start_Inp_train,
                                                                           End_Inp_train,
                                                                           Inp_isi_train3)]},
                                         label='spike_source_Periodic_16_2')




        '''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION OF 5 SECONDS'''
#         Rate_Poisson_Inp_base = 3
        #start_Poisson_Inp_base = 500#RandomDistribution('uniform', (500, 700), rng=NumpyRNG(seed=85524)) ###50

        ######projections for CHANEL 1


        ######projections for CHANEL 2

        ######projections for CHANEL 3


        '''CHANNEL 1 RECEIVES FIIRST COMPETING INPUT '''

        '''Creation of Rewad population'''
        if(Rate_Poisson_Inp_train==14):
            reward_pop=p.Population(numCellsPerCol_SNC,p.extra_models.Izhikevich_cond, snc_cell_params, label='reward_pop1')
            strd1_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.IZK_cond_exp_izhikevich_neuromodulation, strd1_cell_params, label='strd1_pop1')
            strd2_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.IZK_cond_exp_izhikevich_neuromodulation, strd2_cell_params, label='strd2_pop1')
            poplist_ch1 = [strd1_pop1, strd2_pop1, fsi1_pop1, stn_pop1]
            synapse_dynamics_reward = p.STDPMechanism(
                timing_dependence=p.extra_models.TimingIzhikevichNeuromodulation(
                    tau_plus=10, tau_minus=12, A_plus=1, A_minus=1,
                    tau_c=1000, tau_d=50),
                weight_dependence=p.MultiplicativeWeightDependence(w_min=0, w_max=1),
                weight=0.015, neuromodulation=True)
            '''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION OF 5 SECONDS'''
            Rate_Poisson_Inp_base = 3
            #start_Poisson_Inp_base = 500#RandomDistribution('uniform', (500, 700), rng=NumpyRNG(seed=85524)) ###50
            rng = np.random.default_rng(85524)
            start_Poisson_Inp_base = rng.integers(low=500, high=700)
            Duration_Poisson_Inp_base = 9200
            spike_source_Poisson_base1 = p.Population(numPoissonInput, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1')
            spike_source_Poisson_base2 = p.Population(2, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2')


            ######projections for CHANEL 1
            for count1 in range(0, 4):
                if count1 < 2:
                    Base_3hzprojections_in_channel1.append(p.Projection(spike_source_Poisson_base1, poplist_ch1[count1],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 synapse_type=synapse_dynamics_reward,
                                 receptor_type='excitatory'))
                elif(count1==2):
                    Base_3hzprojections_in_channel1.append(p.Projection(spike_source_Poisson_base1, poplist_ch1[count1],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count1], delay=distr_pop[count1]),
                                 receptor_type='excitatory'))

                else:
                    Base_3hzprojections_in_channel1.append(p.Projection(spike_source_Poisson_base2, poplist_ch1[count1],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count1], delay=distr_pop[count1]),
                                 receptor_type ='excitatory'))


            ######projections for CHANEL 1 for 14hz
            for count00 in range(0, 4):
                if count00 < 2:
                    spike_source_Periodic_train14.append(p.Projection(
                        spike_source_Periodic_train14_first, poplist_ch1[count00],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 synapse_type=synapse_dynamics_reward,
                                 receptor_type='excitatory'))
                elif (count00==2):
                    spike_source_Periodic_train14.append(p.Projection(
                        spike_source_Periodic_train14_first, poplist_ch1[count00],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count00], delay=distr_pop[count00]),
                                 receptor_type='excitatory'))
                else:
                    spike_source_Periodic_train14.append(p.Projection(
                        spike_source_Periodic_train14_second, poplist_ch1[count00],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count00], delay=distr_pop[count00]),
                                 receptor_type='excitatory'))
            ######projections for CHANEL 1 for 15hz
            for count01 in range(0, 4):
                if count01 < 2:
                    spike_source_Periodic_train15.append(p.Projection(spike_source_Periodic_train15_first,
                                                                      poplist_ch1[count01],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 synapse_type=synapse_dynamics_reward,
                                 receptor_type='excitatory'))
                elif(count01==2):
                    spike_source_Periodic_train15.append(p.Projection(spike_source_Periodic_train15_first,
                                                                      poplist_ch1[count01],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count01], delay=distr_pop[count01]),
                                 receptor_type='excitatory'))

                else:

                    spike_source_Periodic_train15.append(p.Projection(spike_source_Periodic_train15_second,
                                                                      poplist_ch1[count01],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count01], delay=distr_pop[count01]),
                                 receptor_type='excitatory'))
            ######projections for CHANEL 1 for 16hz
            for count02 in range(0, 4):
                if count02 < 2:
                    spike_source_Periodic_train16.append(p.Projection(spike_source_Periodic_train16_first,
                                                                      poplist_ch1[count02],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 synapse_type=synapse_dynamics_reward,
                                 receptor_type='excitatory'))

                elif(count02==2):
                    spike_source_Periodic_train16.append(p.Projection(spike_source_Periodic_train16_first,
                                                                      poplist_ch1[count02],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count02], delay=distr_pop[count02]),
                                 receptor_type='excitatory'))

                else:
                    spike_source_Periodic_train16.append(p.Projection(spike_source_Periodic_train16_second,
                                                                      poplist_ch1[count02],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count02], delay=distr_pop[count02]),
                                 receptor_type='excitatory'))


            '''Projection from reward pop to channel1'''
            reward_projections_strd1_pop1=p.Projection(reward_pop,strd1_pop1,
                                                       p.AllToAllConnector(),
                                  synapse_type=p.StaticSynapse(weight=reward_value),
                                  receptor_type='reward', label='reward_synapses')
            reward_projections_strd2_pop1=p.Projection(reward_pop,strd2_pop1,p.AllToAllConnector(),
                                  synapse_type=p.StaticSynapse(weight=reward_value),
                                  receptor_type='reward', label='reward_synapses')
            '''Projectons from SNR TO REWARD POPULATION of channel1'''
            snr_to_reward_pop1_projection=p.Projection(snr_pop1,reward_pop,p.AllToAllConnector(),
                                  synapse_type=p.StaticSynapse(weight=reward_value),###weight needs to be changed
                                  receptor_type='excitatory', label='snrpop1_to_rewardpop')
        else:
            '''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION OF 5 SECONDS'''
            #Rate_Poisson_Inp_base = 3
            #start_Poisson_Inp_base = 500#RandomDistribution('uniform', (500, 700), rng=NumpyRNG(seed=85524)) ###50
            strd1_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.Izhikevich_cond, strd1_cell_params, label='strd1_pop1')
            strd2_pop1 = p.Population(numCellsPerCol_STR, p.extra_models.Izhikevich_cond, strd2_cell_params, label='strd2_pop1')
            poplist_ch1 = [strd1_pop1, strd2_pop1, fsi1_pop1, stn_pop1]
            rng = np.random.default_rng(85524)
            start_Poisson_Inp_base = rng.integers(low=500, high=700)
            Duration_Poisson_Inp_base = 9200
            spike_source_Poisson_base1 = p.Population(numPoissonInput, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1')
            spike_source_Poisson_base2 = p.Population(2, p.SpikeSourcePoisson, {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2')

            ######projections for CHANEL 1
            for count1 in range(0, 4):
                if count1 < 3:
                    Base_3hzprojections_in_channel1.append(p.Projection(spike_source_Poisson_base1, poplist_ch1[count1],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count1], delay=distr_pop[count1]),
                                 receptor_type='excitatory'))
                else:
                    Base_3hzprojections_in_channel1.append(p.Projection(spike_source_Poisson_base2, poplist_ch1[count1],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count1], delay=distr_pop[count1]),
                                 receptor_type ='excitatory'))
            for count00 in range(0, 4):
                if count00 < 3:
                    spike_source_Periodic_train14.append(p.Projection(
                        spike_source_Periodic_train14_first, poplist_ch1[count00],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count00], delay=distr_pop[count00]),
                                 receptor_type='excitatory'))

                else:
                    spike_source_Periodic_train14.append(p.Projection(
                        spike_source_Periodic_train14_second, poplist_ch1[count00],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count00], delay=distr_pop[count00]),
                                 receptor_type='excitatory'))
            ######projections for CHANEL 1 for 15hz
            for count01 in range(0, 4):
                if count01 < 3:
                    spike_source_Periodic_train15.append(p.Projection(spike_source_Periodic_train15_first, poplist_ch1[count01],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count01], delay=distr_pop[count01]),
                                 receptor_type='excitatory'))

                else:

                    spike_source_Periodic_train15.append(p.Projection(spike_source_Periodic_train15_second, poplist_ch1[count01],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count01], delay=distr_pop[count01]),
                                 receptor_type='excitatory'))
            ######projections for CHANEL 1 for 16hz
            for count02 in range(0, 4):
                if count02 < 3:
                    spike_source_Periodic_train16.append(p.Projection(spike_source_Periodic_train16_first,
                                                                      poplist_ch1[count02],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2str),
                                 p.StaticSynapse(weight=g_pop[count02], delay=distr_pop[count02]),
                                 receptor_type='excitatory'))


                else:
                    spike_source_Periodic_train16.append(p.Projection(spike_source_Periodic_train16_second,
                                                                      poplist_ch1[count02],
                                 p.FixedProbabilityConnector(p_connect=pconn_cort2stn),
                                 p.StaticSynapse(weight=g_pop[count02], delay=distr_pop[count02]),
                                 receptor_type='excitatory'))



        '''INTRA-CHANNEL PROJECTIONS'''

        distr_strd12snr =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
        distr_strd22gpe =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
        distr_str2str = RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [2, 3])

        '''projections of chanel1'''

        projections_strd1_pop1_snr_pop1=p.Projection(strd1_pop1, snr_pop1,
                     p.FixedProbabilityConnector(p_connect=0.15),
                     p.StaticSynapse(weight = g_strd12snr, delay=distr_strd12snr),
                     receptor_type='inhibitory')
        projections_strd2_pop1_gpe_pop1=p.Projection(strd2_pop1, gpe_pop1,
                     p.FixedProbabilityConnector(p_connect=0.15),
                     p.StaticSynapse(weight = g_strd22gpe, delay=distr_strd22gpe),
                     receptor_type='inhibitory')
        projections_strd1_pop1_strd1_pop1=p.Projection(strd1_pop1, strd1_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')
        projections_strd1_pop1_strd2_pop1=p.Projection(strd1_pop1, strd2_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')
        projections_strd2_pop1_strd1_pop1=p.Projection(strd2_pop1, strd1_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')
        projections_strd2_pop1_strd2_pop1=p.Projection(strd2_pop1, strd2_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')

        '''projections of chanel2'''


        '''projections of chanel-3'''



        ################     EFFERENTS OF FAST SPIKING INTERNEURONS       ####################

        '''projections in chanel 1'''
        projections_fsi1_pop1_strd1_pop1=p.Projection(fsi1_pop1, strd1_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')

        projections_fsi1_pop1_strd2_pop1=p.Projection(fsi1_pop1, strd2_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')


        projections_fsi1_pop1_fsi1_pop1=p.Projection(fsi1_pop1, fsi1_pop1,
                     p.FixedProbabilityConnector(p_connect=0.1),
                     p.StaticSynapse(weight = g_str2str, delay=distr_str2str),
                     receptor_type='inhibitory')


        '''projections in chanel 2'''



        '''projections in chanel 3'''



        ################     EFFERENTS OF GLOBAL PALLIDUS - EXTERNA       ####################

#         g_gaba_gpe = (1.0 / 1.75) * g_gaba
#         g_gpe2stn = g_gaba_gpe
#         g_gpe2gpe = g_gaba_gpe
#         g_gpe2snr = g_gaba_gpe
#         g_gpe2fsi = g_gaba_gpe


        distr_gpe2stn =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
        distr_gpe2gpe =  RandomDistribution('uniform', (2,3), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [2, 3])
        distr_gpe2snr =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
        distr_gpe2fsi =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])

        '''projections in chanel 1'''
        projections_gpe_pop1_stn_pop1=p.Projection(gpe_pop1, stn_pop1,
                     p.FixedProbabilityConnector(p_connect=0.25),
                     p.StaticSynapse(weight=g_gpe2stn, delay=distr_gpe2stn),
                     receptor_type='inhibitory')
        projections_gpe_pop1_gpe_pop1=p.Projection(gpe_pop1, gpe_pop1,
                     p.FixedProbabilityConnector(p_connect=0.25),
                     p.StaticSynapse(weight=g_gpe2gpe, delay=distr_gpe2gpe),
                     receptor_type='inhibitory')
        projections_gpe_pop1_snr_pop1=p.Projection(gpe_pop1, snr_pop1,
                     p.FixedProbabilityConnector(p_connect=0.25),
                     p.StaticSynapse(weight=g_gpe2snr, delay=distr_gpe2snr),
                     receptor_type='inhibitory')
        projections_gpe_pop1_fsi1_pop1=p.Projection(gpe_pop1, fsi1_pop1,
                     p.FixedProbabilityConnector(p_connect=0.05),
                     p.StaticSynapse(weight=g_gpe2fsi, delay=distr_gpe2fsi),
                     receptor_type='inhibitory')


        '''projections in chanel 2'''



        '''projections in chanel 3'''


        ################     EFFERENTS OF SUBSTANTIA NIGRA PARS RETICULATA       ####################

#         g_gaba_snr = (1 / 1.75) * g_gaba
#         g_snr2snr = g_gaba_snr

        distr_snr2snr = p.RandomDistribution("uniform", [2, 3])
        '''projections in chanel 1'''
        projections_snr_pop1_snr_pop1=p.Projection(snr_pop1, snr_pop1,
                     p.FixedProbabilityConnector(p_connect=0.25),
                     p.StaticSynapse(weight=g_snr2snr, delay=distr_snr2snr),
                     receptor_type='inhibitory')

        '''projections in chanel 2'''

        '''projections in chanel 3'''


        ##################################################################
        ################     EFFERENTS OF SUB-THALAMIC NUCLEUS       ####################

        '''INTER-CHANNEL CONNECTIVITY: DIFFUSE EFFERENTS FROM THE STN'''


        distr_stn2gpe_diffuse =  RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [9, 12])
        distr_stn2snr_diffuse =  RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [9, 12])
        distr_stn2gpe =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])
        distr_stn2snr =  RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))#p.RandomDistribution("uniform", [5, 7])

        p_conn_diffuse=0.5

#         g_stn2snr_diffuse = (g_ampa * (1 - (mod_ampa_d2 * phi_stn_dop))) / 6.0
#         g_stn2gpe_diffuse = (g_ampa * (1 - (mod_ampa_d2 * phi_stn_dop))) / 6.0

        '''projections from chanel 1 to chanel 1'''
        projections_stn_pop1_gpe_pop1=p.Projection(stn_pop1, gpe_pop1,
                     p.FixedProbabilityConnector(p_connect=p_conn_diffuse),
                     p.StaticSynapse(weight=g_stn2gpe_diffuse, delay=distr_stn2gpe),
                     receptor_type='excitatory')
        projections_stn_pop1_snr_pop1=p.Projection(stn_pop1, snr_pop1,
                     p.FixedProbabilityConnector(p_connect=p_conn_diffuse),
                     p.StaticSynapse(weight=g_stn2snr_diffuse, delay=distr_stn2snr),
                     receptor_type='excitatory')

        '''projections from chanel 1 to chanel 2'''

        '''projections from chanel 1 to chanel 3'''


        '''projections from chanel 2 to chanel 1'''


        '''projections from chanel 2 to chanel 2'''


        '''projections from chanel 2 to chanel 3'''

        '''projections from chanel 3 to chanel 1'''

        '''projections from chanel 3 to chanel 2'''

        '''projections from chanel 3 to chanel 3'''


        '''RECORD THE SPIKE RASTER'''

#         spike_source_Poisson_base1.record(['spikes'])
        strd1_pop1.record(['spikes'])
        strd2_pop1.record(['spikes'])
        fsi1_pop1.record(['spikes'])
        gpe_pop1.record(['spikes'])
        snr_pop1.record(['spikes'])
        stn_pop1.record(['spikes'])



        p.run(TotalDuration)


        '''DOWNLOAD THE SPIKE RASTER'''

        # spike_source_Poisson_raster1 = np.asarray(spike_source_Poisson_base1.spinnaker_get_data("spikes"))
        #
        strd1_spike_raster1 = np.asarray(strd1_pop1.spinnaker_get_data("spikes"))
        strd2_spike_raster1 = np.asarray(strd2_pop1.spinnaker_get_data("spikes"))
        stn_spike_raster1 = np.asarray(stn_pop1.spinnaker_get_data("spikes"))
        gpe_spike_raster1 = np.asarray(gpe_pop1.spinnaker_get_data("spikes"))

        snr_spike_raster1 = np.asarray(snr_pop1.spinnaker_get_data("spikes"))
        fsi1_spike_raster1 = np.asarray(fsi1_pop1.spinnaker_get_data("spikes"))






        ''' NOW GENERATE AND SAVE THE HISTOGRAM OF FIRING RATES. THIS IS THEN USED TO PLOT THE FIRING RATES AS IN
        FIGURE 6 OF [TS13]'''

        ## SAVING THE GPe
        my_data = gpe_spike_raster1[:, 1]  ## just extract the times of each spike
        print("Mydate before *10",my_data)
        my_data = my_data * 10  ## the times are generated at resolution of 0.1,i.e. with a decimal. remove this
        print("My data after *10",my_data)

        gpe_hist1[thisTrial, :] = my_firingrate(my_data, checkpoint, my_resol)

        ## SAVING THE SNR
        my_data = snr_spike_raster1[:, 1]  ## just extract the times of each spike
        my_data = my_data * 10  ## the times are generated at resolution of 0.1,i.e. with a decimal. remove this

        snr_hist1[thisTrial, :] = my_firingrate(my_data, checkpoint, my_resol)



        ## SAVING THE STN
        my_data = stn_spike_raster1[:, 1]  ## just extract the times of each spike
        my_data = my_data * 10  ## the times are generated at resolution of 0.1,i.e. with a decimal. remove this

        stn_hist1[thisTrial, :] = my_firingrate(my_data, checkpoint, my_resol)


        ## SAVING THE FSI
        my_data = fsi1_spike_raster1[:, 1]  ## just extract the times of each spike
        my_data = my_data * 10  ## the times are generated at resolution of 0.1,i.e. with a decimal. remove this

        fsi_hist1[thisTrial, :] = my_firingrate(my_data, checkpoint, my_resol)

        ##SAVING THE STRD1
        my_data = strd1_spike_raster1[:, 1]  ## just extract the times of each spike
        my_data = my_data * 10  ## the times are generated at resolution of 0.1,i.e. with a decimal. remove this

        strd1_hist1[thisTrial, :] = my_firingrate(my_data, checkpoint, my_resol)

        ##SAVING THE STRD2
        my_data = strd2_spike_raster1[:, 1]  ## just extract the times of each spike
        my_data = my_data * 10  ## the times are generated at resolution of 0.1,i.e. with a decimal. remove this

        strd2_hist1[thisTrial, :] = my_firingrate(my_data, checkpoint, my_resol)

        '''RELEASE THE MACHINE'''

        #p.end()

        return (Base_3hzprojections_in_channel1[0], Base_3hzprojections_in_channel1[1],
                Base_3hzprojections_in_channel1[2], Base_3hzprojections_in_channel1[3],
                spike_source_Periodic_train14[0],spike_source_Periodic_train14[1],
                spike_source_Periodic_train14[2], spike_source_Periodic_train14[3],
                spike_source_Periodic_train15[0], spike_source_Periodic_train15[1],
                spike_source_Periodic_train15[2], spike_source_Periodic_train15[3],
                spike_source_Periodic_train16[0], spike_source_Periodic_train16[1],
                spike_source_Periodic_train16[2], spike_source_Periodic_train16[3],
                projections_strd1_pop1_snr_pop1, projections_strd2_pop1_gpe_pop1,
                projections_strd1_pop1_strd1_pop1, projections_strd1_pop1_strd2_pop1,
                projections_strd2_pop1_strd1_pop1, projections_strd2_pop1_strd2_pop1,
                projections_fsi1_pop1_strd1_pop1,projections_fsi1_pop1_strd2_pop1,
                projections_fsi1_pop1_fsi1_pop1, projections_gpe_pop1_stn_pop1,
                projections_gpe_pop1_gpe_pop1, projections_gpe_pop1_snr_pop1,
                projections_gpe_pop1_fsi1_pop1, projections_snr_pop1_snr_pop1,
                projections_stn_pop1_gpe_pop1, projections_stn_pop1_snr_pop1,
                gpe_hist1, snr_hist1, stn_hist1, fsi_hist1, strd1_hist1, strd2_hist1)

    # folderpath = './DataFolder'

    # np.savetxt(folderpath + 'GPehist1.csv', gpe_hist1)
    # np.savetxt(folderpath + 'GPehist2.csv', gpe_hist2)
    # np.savetxt(folderpath + 'GPehist3.csv', gpe_hist3)
    # np.savetxt(folderpath + 'SNRhist1.csv', snr_hist1)
    # np.savetxt(folderpath + 'SNRhist2.csv', snr_hist2)
    # np.savetxt(folderpath + 'SNRhist3.csv', snr_hist3)
    # np.savetxt(folderpath + 'STNhist1.csv', stn_hist1)
    # np.savetxt(folderpath + 'STNhist2.csv', stn_hist2)
    # np.savetxt(folderpath + 'STNhist3.csv', stn_hist3)
    # np.savetxt(folderpath + 'FSIhist1.csv', fsi_hist1)
    # np.savetxt(folderpath + 'FSIhist2.csv', fsi_hist2)
    # np.savetxt(folderpath + 'FSIhist3.csv', fsi_hist3)



    # print("--- %s SECONDS ELAPSED ---\n \n \n" % (time.time() - start_time))

'''SETTING THE DOPAMINE LEVELS AND CONDUCTANCE PARAMETERS'''
g_ampa = 0.5

mod_ampa_d2 = 0.2  ###00.156 in humphries nnet 2009

phi_max_dop = 5  ##(Scaled within 0 to 5)
phi_msn_dop = 0.55 * phi_max_dop
phi_fsi_dop = 0.75 * phi_max_dop
phi_stn_dop = 0.4 * phi_max_dop  ###(Note that this is scaled between 0 and 16.67)

'''SETTING NETWORK CONDUCTANCE PARAMETERS'''

g_cort2strd1 = g_ampa  # 0.5
g_cort2strd2 = g_ampa * (1 - (mod_ampa_d2 * phi_msn_dop)) # 0.225
g_cort2fsi = g_ampa * (1 - (mod_ampa_d2 * phi_fsi_dop)) # 0.125
g_cort2stn = g_ampa * (1 - (mod_ampa_d2 * phi_stn_dop)) # 0.3


'''INTRA-CHANNEL PROJECTIONS'''

################     EFFERENTS OF STRIATUM        ####################


g_gaba = 0.5 * g_ampa  ### the gaba conductance

mod_gaba = 0.073  ##0.625 ### the level of modulation of dopamine of gaba via the D2 and D1 receptors

g_strd12snr = g_gaba * (1 + mod_gaba * phi_msn_dop)
g_strd22gpe = g_gaba * (1 - mod_gaba * phi_msn_dop)
g_str2str = (1.0/2.55) * g_gaba  # 0.098


################     EFFERENTS OF GLOBAL PALLIDUS - EXTERNA       ####################

g_gaba_gpe = (1.0 / 1.75) * g_gaba
g_gpe2stn = g_gaba_gpe
g_gpe2gpe = g_gaba_gpe
g_gpe2snr = g_gaba_gpe
g_gpe2fsi = g_gaba_gpe

 ################     EFFERENTS OF SUBSTANTIA NIGRA PARS RETICULATA       ####################

g_gaba_snr = (1 / 1.75) * g_gaba
g_snr2snr = g_gaba_snr

################     EFFERENTS OF SUB-THALAMIC NUCLEUS       ####################

g_stn2snr_diffuse = (g_ampa * (1 - (mod_ampa_d2 * phi_stn_dop))) / 6.0
g_stn2gpe_diffuse = (g_ampa * (1 - (mod_ampa_d2 * phi_stn_dop))) / 6.0

#
Rate_Poisson_Inp_train=14

(Base_3hzprojections_in_channel1_0,Base_3hzprojections_in_channel1_1,Base_3hzprojections_in_channel1_2,
 Base_3hzprojections_in_channel1_3,spike_source_Periodic_train14_0,spike_source_Periodic_train14_1,
 spike_source_Periodic_train14_2,spike_source_Periodic_train14_3,spike_source_Periodic_train15_0,
 spike_source_Periodic_train15_1,spike_source_Periodic_train15_2,spike_source_Periodic_train15_3,
 spike_source_Periodic_train16_0,spike_source_Periodic_train16_1,spike_source_Periodic_train16_2,
 spike_source_Periodic_train16_3,
 projections_strd1_pop1_snr_pop1,projections_strd2_pop1_gpe_pop1,projections_strd1_pop1_strd1_pop1,
 projections_strd1_pop1_strd2_pop1,projections_strd2_pop1_strd1_pop1,projections_strd2_pop1_strd2_pop1,
 projections_fsi1_pop1_strd1_pop1,projections_fsi1_pop1_strd2_pop1,projections_fsi1_pop1_fsi1_pop1,
 projections_gpe_pop1_stn_pop1,projections_gpe_pop1_gpe_pop1,projections_gpe_pop1_snr_pop1,
 projections_gpe_pop1_fsi1_pop1,projections_snr_pop1_snr_pop1,
 projections_stn_pop1_gpe_pop1,projections_stn_pop1_snr_pop1,
 gpe_hist1,snr_hist1,stn_hist1,fsi_hist1,strd1_hist1,strd2_hist1)=create_network(
    phi_max_dop,g_cort2strd1, g_cort2strd2, g_cort2fsi, g_cort2stn,g_strd12snr,g_strd22gpe,
    g_str2str,g_gpe2stn,g_gpe2gpe,g_gpe2snr,g_gpe2fsi,g_gaba_snr,g_snr2snr,g_stn2snr_diffuse,
    g_stn2gpe_diffuse,Rate_Poisson_Inp_train)

countt=4

# Base_3hzprojections_in_channel1_listt=[Base_3hzprojections_in_channel1_strd1_w_d,Base_3hzprojections_in_channel1_strd2_w_d,
#                                 Base_3hzprojections_in_channel1_fsi1_w_d,Base_3hzprojections_in_channel1_stn_w_d]

p.end()

snr_hist1_Avg=np.mean(snr_hist1,axis=0)
gpe_hist1_Avg=np.mean(gpe_hist1,axis=0)
stn_hist1_Avg=np.mean(stn_hist1,axis=0)
strd1_hist1_Avg=np.mean(strd1_hist1,axis=0)
strd2_hist1_Avg=np.mean(strd2_hist1,axis=0)

print('snr_hist1_Avg', snr_hist1_Avg)

plt.plot(stn_hist1_Avg,color='r', label='Stn')
plt.plot(snr_hist1_Avg,color='b', label='snr')
plt.plot(gpe_hist1_Avg,color='g', label='Gpe')
# plt.plot(Time,strd1_hist1_Avg,color='c', label='Strd1')
# plt.plot(Time,strd2_hist1_Avg,color='m',label='Strd2')
plt.legend()

plt.plot(strd1_hist1_Avg,color='m',label='Strd1')
plt.legend()

plt.plot(strd2_hist1_Avg,color='y',label='Strd2')
plt.legend()

plt.show()

