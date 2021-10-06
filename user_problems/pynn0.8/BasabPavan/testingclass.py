'''
13th October: We have now moved to PyNN 8, and I am just bit by bit changing the syntax here so that this is compatible with PyNN 8. Also, emulating this as a template to scale up the LGN model.

26th - 27th July 2017:
Resumed the work - had to divert attention to the publication of the initial model on spinnaker.
Now, we rather used the BG1Ch.py to transfer the code and parameters. The code today is complete,
and can instantiate objects of a BG class manually.

The extrinsic poisson inputs are being defined from within the main function (scroll down to the bottom of the code)
and the projections are defined in a separate function. This is intentional, as for now, we would like to keep the
parameters of Poisson inputs visible, without having to tamper with the Class definition itself. We may need to vary
these during testing.

The next step is to put this into loop, i.e. the user needs mention how many instances required,
and this gets created, and executed, and spike data collected. This is implemented using a separate file.
Building on this file.

Note that there are no trial run loops currently, this will be in a separate version of the code.

31st MAY 2017:
STARTED LOOKING INTO WRITING THE OBJECT ORIENTED VERSION OF THE SCRIPT V2.2.



'''


# !/usr/bin/python

import numpy as np
import matplotlib.pylab as plt
import pylab
from pylab import *
import spynnaker8 as p
from pyNN.random import NumpyRNG, RandomDistribution

import time
start_time = time.time()


class bgChannel():

    def __init__(self, p, g_ampa, phi_max_dop):
        self.numCellsPerCol_MSN = 1255
        self.numCellsPerCol_FSI = 84
        self.numCellsPerCol_STN = 14
        self.numCellsPerCol_SNR = 27
        self.numCellsPerCol_GPe = 46
        self.numPoissonInput = 25

        '''PARAMETERS USED IN DEFINING THE BASIC MODEL UNITS: IZHIKEVICH NEURONS'''
        self.tau_ampa = 4  ### ampa synapse time constant
        self.E_ampa = 0  ## ampa synapse reversal potential

        self.tau_gaba_a = 6
        self.E_gaba_a = -80

        self.tau_nmda = 0
        self.E_nmda = 0

        '''CONDUCTANCE PARAMETERS'''

        self.mod_ampa_d2 = 0.2

        self.g_nmda = 0.5 * g_ampa
        self.mod_nmda_d1 = 0.3

        self.g_gaba = 0.5 * g_ampa  ###(==0.25) ### the gaba conductance

        self.mod_gaba_d1 = 0.032  ### the level of modulation of dopamine of gaba via the D1 receptors
        self.mod_gaba = 0.073  ### 0.2###0.156##0.625 ### the level of modulation of dopamine of gaba via the D2 and D1 receptors

        self.g_gaba_gpe = (1.0 / 1.75) * self.g_gaba
        self.g_gpe2stn = self.g_gaba_gpe
        self.g_gpe2gpe = self.g_gaba_gpe
        self.g_gpe2snr = self.g_gaba_gpe
        self.g_gpe2fsi = self.g_gaba_gpe

        self.g_gaba_snr = (1 / 1.75) * self.g_gaba
        self.g_snr2snr = self.g_gaba_snr



        '''SETTING DOPAMINE MODULATION PARAMETERS'''

        self.phi_msn_dop = 0.55 * phi_max_dop
        self.phi_fsi_dop = 0.75 * phi_max_dop
        self.phi_stn_dop = 0.4 * phi_max_dop


        '''SETTING NETWORK CONDUCTANCE PARAMETERS - MODULATED BY DOPAMINE'''

        self.g_cort2msnd1 = g_ampa ###g_nmda * (1 + (mod_nmda_d1 * phi_1)) + g_ampa ###0.4875###
        self.g_cort2msnd2 = g_ampa * (1 - (self.mod_ampa_d2 * self.phi_msn_dop)) ###+ g_nmda ####0.2250####
        self.g_cort2fsi = g_ampa * (1 - (self.mod_ampa_d2 * self.phi_fsi_dop)) ### 0.1250 ###
        self.g_cort2stn = g_ampa * (1 - (self.mod_ampa_d2 * self.phi_stn_dop)) ####+ g_nmda ### 0.3 ###
        self.g_msnd12snr = self.g_gaba * (1 + self.mod_gaba * self.phi_msn_dop)  ####0.3###0.286 ###g_gaba*2.0 ###0.12
        self.g_msnd22gpe = self.g_gaba * (1 - self.mod_gaba * self.phi_msn_dop)  ###0.2###0.286 ###g_gaba*2.0 ###0.1
        self.g_msn2msn = (1.0 / 2.55) * self.g_gaba  ####g_gaba * (1 -  mod_gaba_d2 * phi_2_msn) ###0.098 ###

        self.distr_snr2snr = p.RandomDistribution("uniform", [2, 3])

        self.g_stn2snr_diffuse = (g_ampa * (1 - (self.mod_ampa_d2 * self.phi_stn_dop))) / 6.0
        self.g_stn2gpe_diffuse = (g_ampa * (1 - (self.mod_ampa_d2 * self.phi_stn_dop))) / 6.0

        '''DEFINING DISTRIBUTION OF DELAY PARAMETERS'''

        self.distr_msnd1 = p.RandomDistribution("uniform", [9, 12])

        self.distr_msnd2 = p.RandomDistribution("uniform", [9, 12])

        self.distr_stn = p.RandomDistribution("uniform", [9, 12])

        self.distr_fsi  = p.RandomDistribution("uniform", [9, 12])

        self.distr_msnd12snr = p.RandomDistribution("uniform", [5, 7])
        self.distr_msnd22gpe = p.RandomDistribution("uniform", [5, 7])
        self.distr_msn2msn = p.RandomDistribution("uniform", [2, 3])



        self.distr_gpe2stn = p.RandomDistribution("uniform", [5, 7])
        self.distr_gpe2gpe = p.RandomDistribution("uniform", [2, 3])
        self.distr_gpe2snr = p.RandomDistribution("uniform", [5, 7])
        self.distr_gpe2fsi = p.RandomDistribution("uniform", [5, 7])

        self.distr_stn2gpe = p.RandomDistribution("uniform", [5, 7])
        self.distr_stn2snr = p.RandomDistribution("uniform", [5, 7])


        '''SETTING PROBABILITY OF CONNECTION'''

        self.pconn_cort2msn = 0.15
        self.pconn_cort2stn = 0.2

        self.p_conn_diffuse = 0.5

        '''DEFINING POPULATION ATTRIBUTES FOR EACH CELL TYPE'''
        self.msnd1_a = 0.02
        self.msnd1_b=0.2
        self.msnd1_c=-65
        self.msnd1_d=8
        self.msnd1_v_init = -80
        self.msnd1_u_init = self.msnd1_b * self.msnd1_v_init

        self.msnd2_a=0.02
        self.msnd2_b=0.2
        self.msnd2_c=-65
        self.msnd2_d=8
        self.msnd2_v_init = -80
        self.msnd2_u_init = self.msnd2_b * self.msnd2_v_init

        self.current_bias_msn = -30

        self.msnd1_cell_params = {'a': self.msnd1_a, 'b': self.msnd1_b, 'c': self.msnd1_c, 'd': self.msnd1_d,
                                  'v_init': self.msnd1_v_init, 'u_init': self.msnd1_u_init,
                                  'tau_syn_E': self.tau_ampa, 'tau_syn_I': self.tau_gaba_a,
                                  'i_offset': self.current_bias_msn,
                                  'e_rev_E': self.E_ampa, 'e_rev_I': self.E_gaba_a,
                                  }
        self.msnd2_cell_params = {'a': self.msnd2_a, 'b': self.msnd2_b, 'c': self.msnd2_c, 'd': self.msnd2_d,
                                    'v_init': self.msnd2_v_init, 'u_init': self.msnd2_u_init,
                                    'tau_syn_E': self.tau_ampa, 'tau_syn_I': self.tau_gaba_a,
                                    'i_offset': self.current_bias_msn,
                                    'e_rev_E': self.E_ampa, 'e_rev_I': self.E_gaba_a,
                                  }

        self.fsi_a=0.1
        self.fsi_b=0.2
        self.fsi_c=-65
        self.fsi_d=8
        self.fsi_v_init = -70
        self.fsi_u_init = self.fsi_b * self.fsi_v_init

        self.current_bias_fsi = -10

        self.fsi_cell_params = {'a': self.fsi_a, 'b': self.fsi_b, 'c': self.fsi_c, 'd': self.fsi_d,
                           'v_init': self.fsi_v_init, 'u_init': self.fsi_u_init,
                           'tau_syn_E': self.tau_ampa, 'tau_syn_I': self.tau_gaba_a,
                           'i_offset': self.current_bias_fsi,
                           'e_rev_E': self.E_ampa, 'e_rev_I': self.E_gaba_a,
                           }

        self.gpe_a=0.005
        self.gpe_b=0.585
        self.gpe_c=-65
        self.gpe_d=4
        self.gpe_v_init = -70
        self.gpe_u_init = self.gpe_b * self.gpe_v_init

        self.current_bias_gpe = 2

        '''GLOBAL PALLIDUS - EXTERNA OF THE BASAL GANGLIA'''

        self.gpe_cell_params = {'a': self.gpe_a, 'b': self.gpe_b, 'c': self.gpe_c, 'd': self.gpe_d,
                           'v_init': self.gpe_v_init, 'u_init': self.gpe_u_init,
                           'tau_syn_E': self.tau_ampa, 'tau_syn_I': self.tau_gaba_a,
                           'i_offset': self.current_bias_gpe,
                           'e_rev_E': self.E_ampa, 'e_rev_I': self.E_gaba_a,
                           }

        self.snr_a = 0.005
        self.snr_b = 0.32
        self.snr_c = -65
        self.snr_d = 2
        self.snr_v_init = -70
        self.snr_u_init = self.snr_b * self.snr_v_init

        self.current_bias_snr = 5

        '''SUBSTANTIA NIAGRA OF THE BASAL GANGLIA'''

        self.snr_cell_params = {'a': self.snr_a, 'b': self.snr_b, 'c': self.snr_c, 'd': self.snr_d,
                           'v_init': self.snr_v_init, 'u_init': self.snr_u_init,
                           'tau_syn_E': self.tau_ampa, 'tau_syn_I': self.tau_gaba_a,
                           'i_offset': self.current_bias_snr,
                           'e_rev_E': self.E_ampa, 'e_rev_I': self.E_gaba_a,
                           }

        self.stn_a=0.005
        self.stn_b=0.265
        self.stn_c=-65.0
        self.stn_d=2.0
        self.stn_v_init = -60.0
        self.stn_u_init = self.stn_b * self.stn_v_init

        self.current_bias_stn = 5

        '''SUB-THALAMIC NUCLEUS OF THE BASAL GANGLIA'''

        self.stn_cell_params = {'a': self.stn_a, 'b': self.stn_b, 'c': self.stn_c, 'd': self.stn_d,
                           'v_init': self.stn_v_init, 'u_init': self.stn_u_init,
                           'tau_syn_E': self.tau_ampa, 'tau_syn_I': self.tau_gaba_a,
                           'i_offset': self.current_bias_stn,
                           'e_rev_E': self.E_ampa, 'e_rev_I': self.E_gaba_a,
                           }

        self.msnd1_pop = p.Population(self.numCellsPerCol_MSN, p.IZK_cond_exp, self.msnd1_cell_params, label='msnd1_pop')
        self.msnd2_pop = p.Population(self.numCellsPerCol_MSN, p.IZK_cond_exp, self.msnd2_cell_params, label='msnd2_pop')
        self.fsi_pop = p.Population(self.numCellsPerCol_FSI, p.IZK_cond_exp, self.fsi_cell_params, label='fsi_pop')
        self.gpe_pop = p.Population(self.numCellsPerCol_GPe, p.IZK_cond_exp, self.gpe_cell_params, label='gpe_pop')
        self.snr_pop = p.Population(self.numCellsPerCol_SNR, p.IZK_cond_exp, self.snr_cell_params, label='snr_pop')
        self.stn_pop = p.Population(self.numCellsPerCol_STN, p.IZK_cond_exp, self.stn_cell_params, label='stn_pop')


        p.Projection(self.msnd1_pop, self.msnd1_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')
        p.Projection(self.msnd1_pop, self.msnd2_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')
        p.Projection(self.msnd2_pop, self.msnd1_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')
        p.Projection(self.msnd2_pop, self.msnd2_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')
        p.Projection(self.msnd1_pop, self.snr_pop,
                     p.FixedProbabilityConnector(p_connect=0.15, weights=self.g_msnd12snr, delays=self.distr_msnd12snr), target='inhibitory')
        p.Projection(self.msnd2_pop, self.gpe_pop,
                     p.FixedProbabilityConnector(p_connect=0.15, weights=self.g_msnd22gpe, delays=self.distr_msnd22gpe), target='inhibitory')


        p.Projection(self.fsi_pop, self.msnd1_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')

        p.Projection(self.fsi_pop, self.msnd2_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')


        p.Projection(self.fsi_pop, self.fsi_pop,
                     p.FixedProbabilityConnector(p_connect=0.1, weights=self.g_msn2msn, delays=self.distr_msn2msn), target='inhibitory')

        p.Projection(self.gpe_pop, self.stn_pop,
                     p.FixedProbabilityConnector(p_connect=0.25, weights=self.g_gpe2stn, delays=self.distr_gpe2stn), target='inhibitory')
        p.Projection(self.gpe_pop, self.gpe_pop,
                     p.FixedProbabilityConnector(p_connect=0.25, weights=self.g_gpe2gpe, delays=self.distr_gpe2gpe), target='inhibitory')
        p.Projection(self.gpe_pop, self.snr_pop,
                     p.FixedProbabilityConnector(p_connect=0.25, weights=self.g_gpe2snr, delays=self.distr_gpe2snr), target='inhibitory')
        p.Projection(self.gpe_pop, self.fsi_pop,
                     p.FixedProbabilityConnector(p_connect=0.05, weights=self.g_gpe2fsi, delays=self.distr_gpe2fsi), target='inhibitory')

        p.Projection(self.snr_pop, self.snr_pop,
                     p.FixedProbabilityConnector(p_connect=0.25, weights=self.g_snr2snr, delays=self.distr_snr2snr), target='inhibitory')

        p.Projection(self.stn_pop, self.gpe_pop,
                     p.FixedProbabilityConnector(p_connect=self.p_conn_diffuse, weights=self.g_stn2gpe_diffuse, delays=self.distr_stn2gpe), target='excitatory')
        p.Projection(self.stn_pop, self.snr_pop,
                     p.FixedProbabilityConnector(p_connect=self.p_conn_diffuse, weights=self.g_stn2snr_diffuse, delays=self.distr_stn2snr), target='excitatory')

    '''RECORD THE SPIKE RASTER'''
    def recordSpikes(self):
        self.msnd1_pop.record()
        self.msnd2_pop.record()
        self.fsi_pop.record()
        self.gpe_pop.record()
        self.snr_pop.record()
        self.stn_pop.record()

def getDisplaySpikes(bgChannelX):
    bgChannelX.msnd1_spike_raster = np.asarray(bgChannelX.msnd1_pop.getSpikes())
    bgChannelX.msnd2_spike_raster = np.asarray(bgChannelX.msnd2_pop.getSpikes())
    bgChannelX.stn_spike_raster = np.asarray(bgChannelX.stn_pop.getSpikes())
    bgChannelX.gpe_spike_raster = np.asarray(bgChannelX.gpe_pop.getSpikes())
    bgChannelX.snr_spike_raster = np.asarray(bgChannelX.snr_pop.getSpikes())
    bgChannelX.fsi_spike_raster = np.asarray(bgChannelX.fsi_pop.getSpikes())

    f1 = plt.figure
    n_plots_1 = 3
    plot = 1
    numcols = 2

    plt.subplot( n_plots_1,  numcols,  plot)
    plot += 1
    if len( bgChannelX.msnd1_spike_raster) > 0:
        plt.scatter( bgChannelX.msnd1_spike_raster[:, 1],  bgChannelX.msnd1_spike_raster[:, 0], color='purple', s=1)
    plt.title('Spike raster for MSN-D1')
    plt.xlim(0, TotalDuration)

    plt.subplot(n_plots_1, numcols, plot)
    plot += 1
    if len(bgChannelX.msnd2_spike_raster) > 0:
        plt.scatter(bgChannelX.msnd2_spike_raster[:, 1], bgChannelX.msnd2_spike_raster[:, 0], color='blue', s=1)
    plt.title('Spike raster for MSN-D2')
    plt.xlim(0, TotalDuration)

    plt.subplot(n_plots_1, numcols, plot)
    plot += 1
    if len(bgChannelX.fsi_spike_raster) > 0:
        plt.scatter(bgChannelX.fsi_spike_raster[:, 1], bgChannelX.fsi_spike_raster[:, 0], color='indigo', s=1)
    plt.title('Spike raster for FSI')
    plt.xlim(0, TotalDuration)

    plt.subplot(n_plots_1, numcols, plot)
    plot += 1
    if len(bgChannelX.stn_spike_raster) > 0:
        plt.scatter(bgChannelX.stn_spike_raster[:, 1], bgChannelX.stn_spike_raster[:, 0], color='green', s=1)
    plt.title('Spike raster for STN')
    plt.xlim(0, TotalDuration)

    plt.subplot(n_plots_1, numcols, plot)
    plot += 1
    if len(bgChannelX.snr_spike_raster) > 0:
        plt.scatter(bgChannelX.snr_spike_raster[:, 1], bgChannelX.snr_spike_raster[:, 0], color='red', s=1)
    plt.title('Spike raster for SNr')
    plt.xlim(0, TotalDuration)

    plt.subplot(n_plots_1, numcols, plot)
    plot += 1
    if len(bgChannelX.gpe_spike_raster) > 0:
        plt.scatter(bgChannelX.gpe_spike_raster[:, 1], bgChannelX.gpe_spike_raster[:, 0], color='orange', s=1)
    plt.title('Spike raster for GP-e')
    plt.xlim(0, TotalDuration)

    plt.show(f1)

def extrinsicInput(p, bgChannelX, Rate_Poisson_Inp_base, start_Poisson_Inp_base, Duration_Poisson_Inp_base, numPoissonInput_Str, numPoissonInput_stn):
    spike_source_Poisson_base1 = p.Population(numPoissonInput_Str, p.SpikeSourcePoisson,
                                                   {'rate': Rate_Poisson_Inp_base,
                                                    'duration': Duration_Poisson_Inp_base,
                                                    'start': start_Poisson_Inp_base},
                                                   label='spike_source_Poisson_base1')
    spike_source_Poisson_base2 = p.Population(numPoissonInput_stn, p.SpikeSourcePoisson,
                                                   {'rate': Rate_Poisson_Inp_base,
                                                    'duration': Duration_Poisson_Inp_base,
                                                    'start': start_Poisson_Inp_base},
                                                   label='spike_source_Poisson_base2')

    p.Projection(spike_source_Poisson_base1, bgChannelX.msnd1_pop,
                 p.FixedProbabilityConnector(p_connect=bgChannelX.pconn_cort2msn, weights=bgChannelX.g_cort2msnd1,
                                             delays=bgChannelX.distr_msnd1), target='excitatory')

    p.Projection(spike_source_Poisson_base1, bgChannelX.msnd2_pop,
                 p.FixedProbabilityConnector(p_connect=bgChannelX.pconn_cort2msn, weights=bgChannelX.g_cort2msnd2,
                                             delays=bgChannelX.distr_msnd2), target='excitatory')

    p.Projection(spike_source_Poisson_base1, bgChannelX.fsi_pop,
                 p.FixedProbabilityConnector(p_connect=bgChannelX.pconn_cort2msn, weights=bgChannelX.g_cort2fsi,
                                             delays=bgChannelX.distr_fsi), target='excitatory')

    p.Projection(spike_source_Poisson_base2, bgChannelX.stn_pop,
                 p.FixedProbabilityConnector(p_connect=bgChannelX.pconn_cort2msn, weights=bgChannelX.g_cort2stn,
                                             delays=bgChannelX.distr_stn), target='excitatory')
if __name__ == "__main__":
    TotalDuration = 10000  ###TOTAL RUN TIME
    TimeInt = 0.1  ### SIMULATION TIME STEP
    TotalDataPoints = int(TotalDuration * (1 / TimeInt))
    g_ampa = 0.5

    phi_max_dop = 5

    numPoissonInput_Str = 25
    numPoissonInput_stn = 2

    '''BASE POISSON INPUTS TO ALL CHANNELS FOR THE ENTIRE SIMULATION DURATION '''
    Rate_Poisson_Inp_base = 3
    start_Poisson_Inp_base = p.RandomDistribution("uniform", [500, 700])  ###0
    Duration_Poisson_Inp_base = 9200  ####TotalDuration

    '''POISSON INPUT TO first CHANNEL '''
    Rate_Poisson_Inp_1 = 15
    start_Poisson_Inp_1 = p.RandomDistribution("uniform", [2500, 2700])  ###0
    Duration_Poisson_Inp_1 = 7200  ####TotalDuration

    ''' SET UP SPINNAKER AND BEGIN SIMULATION'''
    p.setup(timestep=0.1, min_delay=1.0, max_delay=14.0)

    bgChannel_1 = bgChannel(p, g_ampa, phi_max_dop)
    bgChannel_2 = bgChannel(p, g_ampa, phi_max_dop)


    extrinsicInput(p, bgChannel_1, Rate_Poisson_Inp_base, start_Poisson_Inp_base, Duration_Poisson_Inp_base,
                   numPoissonInput_Str, numPoissonInput_stn)

    extrinsicInput(p, bgChannel_2, Rate_Poisson_Inp_base, start_Poisson_Inp_base, Duration_Poisson_Inp_base,
                   numPoissonInput_Str, numPoissonInput_stn)
    extrinsicInput(p, bgChannel_2, Rate_Poisson_Inp_1, start_Poisson_Inp_1, Duration_Poisson_Inp_1,
                  numPoissonInput_Str, numPoissonInput_stn)

    bgChannel_1.recordSpikes()
    bgChannel_2.recordSpikes()
    p.run(TotalDuration)

    getDisplaySpikes(bgChannel_1)
    getDisplaySpikes(bgChannel_2)
    p.end()






