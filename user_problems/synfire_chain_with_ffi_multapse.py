#!/usr/bin/env python2
"""
Synfire Chain
according to:
    Kremkow, Perrinet, Masson & Aertsen.
    Functional consequences of correlated excitatory and inhibitory conductances in cortical networks.
    Journal of computational neuroscience (2010)
    vol. 28 (3) pp. 579-94

adapted by Bernhard Vogginger
"""

#from pyNN.nest import *
from spynnaker7.pyNN import *

import pyNN.random
import pylab
import numpy

rng = pyNN.random.NumpyRNG(seed=124578)

########################
## Experiment Parameters
########################

n_groups = 6 # Number of Synfire Groups
n_exc = 300 # Number of excitatory neurons per group
n_inh = 250 # Number of inhibitory neurons per group

sim_duration = 500.

# defining the initial pulse-packet
pp_a = 5 # Nr of pulses in the packet
pp_sigma = 5.0 # sigma of pulse-packet
pp_start = 50. # start = center of pulse-packet

# Neuron Parameters as in Kremkow et al. paper
cell_params={
    'cm'         : 0.290,      # nF
    'tau_m'      : 290.0/29.0, # pF / nS = ms
    'v_rest'     : -70.0,      # mV
    'v_thresh'   : -57.0,      # mV
    'tau_syn_E'  : 1.5,        # ms
    'tau_syn_I'  : 10.0,       # ms
    'tau_refrac' : 2.0,        # ms
    'v_reset'    : -70.0,      # mV
    'e_rev_E'    : 0.0,        # mV
    'e_rev_I'    : -75.0,      # mV
}

weight_exc = 0.01 # uS weight for excitatory to excitatory connections (edited)
weight_inh = 0.002 # uS weight for inhibitory to excitatory connections


################
# set up pyNN
################
setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
set_number_of_neurons_per_core("IF_cond_exp", 100)


# list of excitatory populations
exc_pops = []
# list of inhibitory populations
inh_pops = []
# and Assembly of all populations
all_populations = []

################
## Create Groups
################
print "Creating ", n_groups, " SynfireGroups"
for group_index in range(n_groups):
    # create the excitatory Population
    exc_pop = Population(n_exc, IF_cond_exp, cell_params,
                         label=("pop_exc_%s" % group_index))
    #exc_pop2 = Population(n_exc, SpikeSourcePoisson, {"rate": 500})
    #Projection(exc_pop2, exc_pop, OneToOneConnector( weights=weight_exc/1, delays=8. ), target='excitatory', rng = rng)

    exc_pops.append(exc_pop)  # append this Population to the list of excitatory populations
    all_populations += [ exc_pop ]  # and to the Assembly

	# create the inhibitory Population
    inh_pop = Population(n_inh, IF_cond_exp, cell_params,
                         label=("pop_inh_%s" % group_index))
    inh_pops.append(inh_pop)
    all_populations += [inh_pop]

	# connect Inhibitory to excitatory Population
    Projection(inh_pop, exc_pop,
               AllToAllConnector(weights=weight_inh, delays=8.),
               target='inhibitory', rng=rng)



###################################################
## Create Stimulus and connect it to first group
###################################################
print "Create Stimulus Population"
# We create a Population of SpikeSourceArrays of the same dimension as excitatory neurons in a synfire group
pop_stim = Population(n_exc, SpikeSourceArray, {}, label= "pop_stim")

# We create a normal distribution around pp_start with sigma = pp_sigma
rd = pyNN.random.RandomDistribution('normal', [pp_start, pp_sigma])
all_spiketimes = []
# for each cell in the population, we take pp_a values from the random distribution
for cell in range(len(pop_stim)):
    spiketimes = []
    for pulse in range(pp_a):
        spiketimes.append(rd.next())  # draw the next value from the random distribution
    spiketimes.sort()
    all_spiketimes.append(spiketimes)
all_spiketimes=numpy.array(all_spiketimes) # convert into a numpy array
pop_stim.tset('spike_times', all_spiketimes) # 'topographic' setting of parameters. all_spiketimes must have the same dimension as the Population


###########################################
## Connect Groups with the subsequent ones
###########################################
print "Connecting Groups with subsequent ones"
for group_index in range(n_groups-1):
#for group_index in range(n_groups):
    Projection(exc_pops[group_index%n_groups],
               exc_pops[(group_index+1)%n_groups],
               MultapseConnector(2400, weights=weight_exc, delays=10.),
               #FixedNumberPostConnector(80,weights=weight_exc,delays=10.),
               target='excitatory', rng = rng)
    Projection(exc_pops[group_index%n_groups],
               inh_pops[(group_index+1)%n_groups],
               MultapseConnector(1000, weights=weight_exc, delays=10.),
               #FixedNumberPostConnector(20,weights=weight_exc,delays=10.),
               target='excitatory', rng = rng)

# Make another projection for testing that connects to itself
#Projection(exc_pops[1], exc_pops[1],
#           MultapseConnector(600, weights=weight_exc, delays=10.),
#           FixedNumberPostConnector(
#               60,allow_self_connections=False,weights=weight_exc,delays=10.),
#           target='excitatory', rng = rng)


##########################################
## Connect the Stimulus to the first group
##########################################
print "Connecting Stimulus to first group"
Projection(pop_stim, inh_pops[0],
           MultapseConnector(750, weights=weight_exc, delays=20.),
           #FixedNumberPostConnector(15, weights=weight_exc, delays=20.),
           target='excitatory' ,rng = rng)
Projection(pop_stim, exc_pops[0],
           MultapseConnector(2500, weights=weight_exc, delays=20.),
           #FixedNumberPostConnector(60, allow_self_connections=False,
           #                        weights=weight_exc, delays=20.),
           target='excitatory' ,rng = rng)




###################
## Recording spikes
###################

pop_stim.record() # record input spikes for debugging

#all_populations.record() # record spikes of all populations
for p in all_populations:
    p.record()

###############
## Run
###############
print "Run the simulation"
run(sim_duration)


###############
## Plot
##############
print "Simulation finished, now collect all spikes and plot them"

pop_stim.printSpikes("stim.dat") # save stimulus
stim_spikes = pop_stim.getSpikes()
stim_spikes[:,0] -= n_exc

# collect all spikes and make a raster_plot
spklist_exc = []
spklist_inh = []
for group in range(n_groups):
    EXC_spikes=exc_pops[group].getSpikes(compatible_output=True)
    INH_spikes=inh_pops[group].getSpikes(compatible_output=True)
    EXC_spikes[:,0]+=group*(n_exc+n_inh)
    INH_spikes[:,0]+=group*(n_exc+n_inh) + n_exc
    spklist_exc+=EXC_spikes.tolist()
    spklist_inh+=INH_spikes.tolist()
# Create a NeuroTools SpikeList from it

#print EXC_spikes

pylab.figure()
pylab.plot([i[1] for i in spklist_exc], [i[0] for i in spklist_exc], "r.")
pylab.plot([i[1] for i in spklist_inh], [i[0] for i in spklist_inh], "b.")
pylab.plot([i[1] for i in stim_spikes], [i[0] for i in stim_spikes], "k.")
pylab.xlabel('Time/ms')
pylab.ylabel('spikes')
pylab.title('spikes')

for group in range(n_groups):
    pylab.axhline(y=(group+1)*(n_exc+n_inh), color="lightgrey")
    pylab.axhline(y=(group+1)*(n_exc+n_inh)-n_inh, color="lightgrey")

pylab.axhline(y=0, color="grey",linewidth=1.5)
pylab.show()

end()
