"""
**********************************************************

Simple test for STDP :

Reproduces a classical plasticity experiment of plasticity induction by
pre/post synaptic pairing specifically :

 * At the begining of the simulation, external stimulations of
   the presynaptic population do not trigger activity in the
   postsynaptic population.

 * Then the presynaptic and postsynaptic populations are stimulated together
   by an external source so that the post-synaptic population spikes 10ms after the pre-synaptic population.

 * Ater training, only the pre-synaptic population is externally stimulated,
   but now it should trigger activity in the post-synaptic
   population (due to STDP learning)

*************************************************************
"""
# try:
#     import pyNN.spiNNaker as p
# except Exception:
import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

# SpiNNaker setup
p.setup(timestep=0.1, min_delay=1.0)


# Izhikevich Population parameters
model = p.extra_models.Izhikevich_cond
#a_tonic = 0.02
#b_tonic = 0.2
#c_tonic = -65.0
#d_tonic = 6.0
#v_init_tonic = -65.0
#u_init_tonic = b_tonic * v_init_tonic
#current_Pulse = 0
#tau_ex = 1.7
#tau_inh = 2.5
#cell_params = {'a': a_tonic, 'b': b_tonic, 'c': c_tonic,'d': d_tonic,
#                'v': v_init_tonic, 'u': u_init_tonic,
#                'tau_syn_E': tau_ex, 'tau_syn_I': tau_inh,
#                'i_offset': current_Pulse
#                }
snr_a=0.005
snr_b=0.32
snr_c=-65
snr_d=2
snr_v_init = -70
snr_u_init = snr_b * snr_v_init

tau_ampa = 6###excitatory synapse time constant
tau_gabaa= 4### inhibitory synapse time constant
E_ampa = 0.0
E_gabaa = -80.0
current_bias = 0.
cell_params = {'a': snr_a, 'b': snr_b, 'c': snr_c, 'd': snr_d,
                   'v': snr_v_init, 'u': snr_u_init,
                   'tau_syn_E': tau_ampa, 'tau_syn_I': tau_gabaa,
                   'i_offset': current_bias,
                   'e_rev_E': E_ampa, 'e_rev_I': E_gabaa,
                   }


## Weight of the static synapses
weight_spike_source_to_pop = 0.01
## Size of all populations are kept the same
pop_size = 40


## DEFINING PRE-TRAINING STIMULI
## Number of test stimulus to pre-synaptic population BEFORE Training. This does not evoke any response from the post-synaptic population.
n_preTraining = 5

## Define the Periodic input for the Pre-training period
rate_periodic_inp_preTraining = 10  ## The rate of periodic input in Hz
inp_isi_preTraining = (int(1000/rate_periodic_inp_preTraining)) ## This is therefore the inter-spike-interval for the periodic input
start_periodic_inp_preTraining = 200 ## This is in msec after start of simulation
duration_periodic_inp_preTraining = inp_isi_preTraining * (n_preTraining-1) ## Calculate the duration required for providing 5 pretraining stimuli
end_periodic_inp_preTraining = start_periodic_inp_preTraining + duration_periodic_inp_preTraining   ## Therefore now calculate the total duration of pretraining stimuli

## Now create the periodic spike source population
spike_source_periodic_preTraining = p.Population(pop_size, p.SpikeSourceArray, {'spike_times': [i for i in range(start_periodic_inp_preTraining,end_periodic_inp_preTraining,inp_isi_preTraining)]}, label='spike_source_Periodic_preTraining')


## DEFINING TRAINING STIMULI
n_Training = 20

## Define the Periodic input for TRAINING
rate_periodic_inp_Training = 20  ## The rate of periodic input in Hz
inp_isi_Training = (int(1000/rate_periodic_inp_Training)) ## This is therefore the inter-spike-interval for the periodic input
start_periodic_inp_Training = end_periodic_inp_preTraining + 700 ## This is in msec after start of simulation
duration_periodic_inp_Training = inp_isi_Training * (n_Training-1) ## Calculate the duration required for providing 20 training stimuli
end_periodic_inp_Training = start_periodic_inp_Training + duration_periodic_inp_Training   ## Therefore now calculate the total duration of training stimuli

## Now create the periodic spike source population
spike_source_periodic_Training = p.Population(pop_size, p.SpikeSourceArray, {'spike_times': [i for i in range(start_periodic_inp_Training,end_periodic_inp_Training,inp_isi_Training)]}, label='spike_source_Periodic_Training')


## DEFINING TESTING STIMULI
n_Testing = 5
## Define the Periodic input for TESTING
rate_periodic_inp_Testing = 10  ## The rate of periodic input in Hz
inp_isi_Testing = (int(1000/rate_periodic_inp_Testing)) ## This is therefore the inter-spike-interval for the periodic input
start_periodic_inp_Testing = end_periodic_inp_Training + 700 ## This is in msec after start of simulation
duration_periodic_inp_Testing = inp_isi_Testing * (n_Testing-1) ## Calculate the duration required for providing 5 test stimuli
end_periodic_inp_Testing = start_periodic_inp_Testing + duration_periodic_inp_Testing   ## Therefore now calculate the total duration of test stimuli

## Now create the periodic spike source population
spike_source_periodic_Testing = p.Population(pop_size, p.SpikeSourceArray, {'spike_times': [i for i in range(start_periodic_inp_Testing,end_periodic_inp_Testing,inp_isi_Testing)]}, label='spike_source_Periodic_Testing')


## Define the pre-synaptic population

pre_syn_pop = p.Population(pop_size, model(**cell_params),label='Pre-synaptic Population')
post_syn_pop = p.Population(pop_size, model(**cell_params),label='Post-synaptic Population')

# ADD THE PLASTIC CONNECTIONS BETWEEN THE PRE- AND THE POST-SYNAPTIC POPULATIONS
stdp_model = p.STDPMechanism(
     timing_dependence=p.SpikePairRule(
         tau_plus=20.0, tau_minus=20.0, A_plus=0.02, A_minus=0.02),
     weight_dependence=p.AdditiveWeightDependence(w_min=0.01, w_max=0.1))

plastic_projection = p.Projection(
     pre_syn_pop, post_syn_pop, p.FixedProbabilityConnector(p_connect=0.5),
     synapse_type=stdp_model)

## NOW DEFINE THE PROJECTIONS FROM SOURCE TO POPULATIONS

## FIRST JUST PROJECTING TO THE PRE-SYNAPTIC POPULATION
p.Projection(spike_source_periodic_preTraining, pre_syn_pop, p.FixedProbabilityConnector(p_connect=0.5), p.StaticSynapse(weight=weight_spike_source_to_pop), receptor_type='excitatory')
## NOW WE START TRAINING WITH 20 PERIODIC STIMULI TO BOTH PRE AND POST-SYNAPTIC POPULATION
p.Projection(spike_source_periodic_Training, pre_syn_pop, p.FixedProbabilityConnector(p_connect=0.5), p.StaticSynapse(weight=weight_spike_source_to_pop), receptor_type='excitatory')
p.Projection(spike_source_periodic_Training, post_syn_pop, p.FixedProbabilityConnector(p_connect=0.5), p.StaticSynapse(weight=weight_spike_source_to_pop, delay=10.0), receptor_type='excitatory')
## NOW WE TEST THE EFFECT OF TRAINING BY PROVIDING ANOTHER TRAIN OF INPUT STIMULI
p.Projection(spike_source_periodic_Testing, pre_syn_pop, p.FixedProbabilityConnector(p_connect=0.5), p.StaticSynapse(weight=weight_spike_source_to_pop), receptor_type='excitatory')


# RECORD SPIKES
pre_syn_pop.record(['spikes'])
spike_source_periodic_preTraining.record(['spikes'])
spike_source_periodic_Training.record(['spikes'])
spike_source_periodic_Testing.record(['spikes'])
post_syn_pop.record(['spikes'])

# SPECIFY RUNTIME AND RUN SIMULATION ON SPINNAKER
simtime = end_periodic_inp_Testing + 500.
p.run(simtime)

## GET THE RECORDED SPIKES
pre_syn_spikes=pre_syn_pop.get_data('spikes')
preTraining_source_spikes=spike_source_periodic_preTraining.get_data('spikes')
Training_source_spikes=spike_source_periodic_Training.get_data('spikes')
Testing_source_spikes=spike_source_periodic_Testing.get_data('spikes')
post_syn_spikes=post_syn_pop.get_data('spikes')

## PRINT THE WEIGHTS ON SCREEN
print("Weights:{}".format(plastic_projection.get('weight', 'list')))

## PLOT SPIKE RASTERS

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(pre_syn_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, simtime)),
          # raster plot of the postsynaptic neuron spike times
    Panel(post_syn_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, simtime)),
          # raster plot of periodic inputs
    Panel(preTraining_source_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, simtime)),
    Panel(Training_source_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, simtime)),
    Panel(Testing_source_spikes.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, simtime)),
    title="stdp example curr"
)
plt.show()
# plt.savefig('stdp_izkcond_example.png')

# RELEASE THE MACHINE
p.end()
