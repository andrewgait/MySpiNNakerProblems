import spynnaker8 as pynn
import numpy as np
import matplotlib.pyplot as plt
import Parameters_small as p
from pyNN.random import NumpyRNG,RandomDistribution
from pyNN.utility import get_script_args,Timer
from pyNN.utility.plotting import Figure,Panel


simulator_Name='spiNNaker'

extra={}

rank=pynn.setup(timestep=p.dt,max_delay=p.delay_ex,**extra)

pynn.set_number_of_neurons_per_core(pynn.IF_curr_exp,100)
pynn.set_number_of_neurons_per_core(pynn.SpikeSourcePoisson,100)

import socket

host_name=socket.gethostname()

print "Host #%d is on %s"%(rank+1,host_name)

if extra.has_key('threads'):
   print "%d Initialising the simulator with %d threads..."%(rank,extra['threads'])
else:
   print "%d Initialising the simulator with single thread..."%(rank)


def nprint(s):
    if (rank==0):
       print s

print "%d Settign up random number generator"%(rank)
rng=NumpyRNG(seed=1,parallel_safe=True)


print "%d Creating excitatory population with %d neurons."%(rank,p.N_pyr)

E_net=pynn.Population(p.N_pyr,pynn.IF_curr_exp(**p.neuron_params),label="E_pop")

print "%d Creating PV population with %d neurons."%(rank,p.N_PV)

PV_net=pynn.Population(p.N_PV,pynn.IF_curr_exp(**p.neuron_params),label="PV_pop")

print "%d Creating VIP population with %d neurons."%(rank,p.N_VIP)

VIP_net=pynn.Population(p.N_VIP,pynn.IF_curr_exp(**p.neuron_params),label="VIP_pop")

print "%d Creating SST population with %d neurons."%(rank,p.N_SST)

SST_net=pynn.Population(p.N_SST,pynn.IF_curr_exp(**p.neuron_params),label="SST_pop")

print "%d Initialising membrane potentials to random values between %g mV and %g mV."%(rank,p.V_reset,p.V_th)

uniDistr_pyr=RandomDistribution('uniform',[p.V_reset,p.V_th],rng)

uniDistr_pv=RandomDistribution('uniform',[p.V_reset,p.V_th],rng)

uniDistr_vip=RandomDistribution('uniform',[p.V_reset,p.V_th],rng)

uniDistr_sst=RandomDistribution('uniform',[p.V_reset,p.V_th],rng)

E_net.initialize(v=uniDistr_pyr)

PV_net.initialize(v=uniDistr_pv)

VIP_net.initialize(v=uniDistr_vip)

SST_net.initialize(v=uniDistr_sst)

print "%d Creating poisson generators for background inputs"%(rank)


expoisson=pynn.Population(1,pynn.SpikeSourcePoisson(rate=p.p_bgexrate),label="expoisson")

pvpoisson=pynn.Population(1,pynn.SpikeSourcePoisson(rate=p.p_bgpvrate),label="pvpoisson")

vippoisson=pynn.Population(1,pynn.SpikeSourcePoisson(rate=p.p_bgviprate),label="vippoisson")

sstpoisson=pynn.Population(1,pynn.SpikeSourcePoisson(rate=p.p_bgsstrate),label="sstpoisson")


print "%d Creating Layer 4 neurons"%(rank)


L4exex=pynn.Population(p.N_pyr,pynn.SpikeSourcePoisson(rate=p.ex_rateL4exex),label="L4exex")
L4exinPV=pynn.Population(p.N_PV,pynn.SpikeSourcePoisson(rate=p.ex_rateL4exin),label="L4exinPV")
L4exinVIP=pynn.Population(p.N_VIP,pynn.SpikeSourcePoisson(rate=p.ex_rateL4exin),label="L4exinVIP")
L4exinSST=pynn.Population(p.N_SST,pynn.SpikeSourcePoisson(rate=p.ex_rateL4exin),label="L4exinSST")
L4inex=pynn.Population(p.N_pyr,pynn.SpikeSourcePoisson(rate=p.ex_rateL4inex),label="L4inex")
L4ininPV=pynn.Population(p.N_PV,pynn.SpikeSourcePoisson(rate=p.ex_rateL4inin),label="L4ininPV")
L4ininVIP=pynn.Population(p.N_VIP,pynn.SpikeSourcePoisson(rate=p.ex_rateL4inin),label="L4ininVIP")
L4ininSST=pynn.Population(p.N_SST,pynn.SpikeSourcePoisson(rate=p.ex_rateL4inin),label="L4ininVIP")



print "%d Setting up recording in excitatory population."%(rank)

E_net.record("spikes")

print "%d Setting up recording in PV neurons."%(rank)

PV_net.record("spikes")

print "%d Setting up recording in VIP neurons."%(rank)

VIP_net.record("spikes")

print "%d Setting up recording in SST neurons."%(rank)

SST_net.record("spikes")


# Connectors for Layer 2/3 Neurons
PVPVconnector=pynn.FixedProbabilityConnector(p.ep_PVPV*p.ep_pr)
PVPyrconnector=pynn.FixedProbabilityConnector(p.ep_PVPyr*p.ep_pr)
VIPSSTconnector=pynn.FixedProbabilityConnector(p.ep_VIPSST*p.ep_pr)
SSTPVconnector=pynn.FixedProbabilityConnector(p.ep_SSTPV*p.ep_pr)
SSTVIPconnector=pynn.FixedProbabilityConnector(p.ep_SSTVIP*p.ep_pr)
SSTPyrconnector=pynn.FixedProbabilityConnector(p.ep_SSTPyr*p.ep_pr)
PyrInconnector=pynn.FixedProbabilityConnector(p.ep_PyrIn)
PyrPyrconnector=pynn.FixedProbabilityConnector(p.ep_PyrPyr)

L4_connector=pynn.OneToOneConnector()           # Connectors for Layer 4 inputs to Layer 2/3 neurons

ext_connector=pynn.AllToAllConnector()          # Connectors for background inputs to Layer 2/3 neurons


# Pyr Neurons
E_to_E=pynn.Projection(E_net,E_net,PyrPyrconnector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))

E_to_PV=pynn.Projection(E_net,PV_net,PyrInconnector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))

E_to_VIP=pynn.Projection(E_net,VIP_net,PyrInconnector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))

E_to_SST=pynn.Projection(E_net,SST_net,PyrInconnector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))

input_to_E=pynn.Projection(expoisson,E_net,ext_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))

#PV Neurons

PV_to_PV=pynn.Projection(PV_net,PV_net,PVPVconnector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_PVPV,delay=p.delay_in))
PV_to_E=pynn.Projection(PV_net,E_net,PVPyrconnector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_PVPyr,delay=p.delay_in))
input_to_PV=pynn.Projection(pvpoisson,PV_net,ext_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))


#VIP Neurons

VIP_to_SST=pynn.Projection(VIP_net,SST_net,VIPSSTconnector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_VIPSST,delay=p.delay_in))
input_to_VIP=pynn.Projection(vippoisson,VIP_net,ext_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))


#SST Neurons
SST_to_PV=pynn.Projection(SST_net,PV_net,SSTPVconnector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_SSTPV,delay=p.delay_in))
SST_to_VIP=pynn.Projection(SST_net,VIP_net,SSTVIPconnector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_SSTVIP,delay=p.delay_in))
SST_to_E=pynn.Projection(SST_net,E_net,SSTPyrconnector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_SSTPyr,delay=p.delay_in))
input_to_SST=pynn.Projection(sstpoisson,SST_net,ext_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))



#Layer 4 Neurons

L4ex_to_E=pynn.Projection(L4exex,E_net,L4_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))
L4ex_to_PV=pynn.Projection(L4exinPV,PV_net,L4_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))
L4ex_to_VIP=pynn.Projection(L4exinVIP,VIP_net,L4_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))
L4ex_to_SST=pynn.Projection(L4exinSST,SST_net,L4_connector,receptor_type="excitatory",synapse_type=pynn.StaticSynapse(weight=p.J_ex,delay=p.delay_ex))
L4in_to_E=pynn.Projection(L4inex,E_net,L4_connector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_in,delay=p.delay_in))
L4in_to_PV=pynn.Projection(L4ininPV,PV_net,L4_connector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_in,delay=p.delay_in))
L4in_to_VIP=pynn.Projection(L4ininVIP,VIP_net,L4_connector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_in,delay=p.delay_in))
L4in_to_SST=pynn.Projection(L4ininSST,SST_net,L4_connector,receptor_type="inhibitory",synapse_type=pynn.StaticSynapse(weight=p.J_in,delay=p.delay_in))



pynn.run(p.simtime)

esp=E_net.get_data("spikes")

isp1=PV_net.get_data("spikes")

isp2=VIP_net.get_data("spikes")

isp3=SST_net.get_data("spikes")




Figure(Panel(esp.segments[0].spiketrains,yticks=True,xticks=True,markersize=01,xlim=(0,p.simtime)),Panel(isp1.segments[0].spiketrains,yticks=True,xticks=True,markersize=01,xlim=(0,p.simtime)),Panel(isp2.segments[0].spiketrains,yticks=True,xticks=True,markersize=01,xlim=(0,p.simtime)),Panel(isp3.segments[0].spiketrains,yticks=True,xticks=True,markersize=01,xlim=(0,p.simtime)),title="Spike trains",annotations="Simulated with {}".format(pynn.name()))


plt.show()


pynn.end()


