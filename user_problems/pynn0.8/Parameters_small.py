simtime=1000.7
dt=0.1
delay_ex=1.5
delay_in=0.7


# Population Size

N_pyr=2069
N_PV=146
N_VIP=291
N_SST=146

# Scaling factor for inhibitory connection probabilities

ep_pr=0.2


# Connection Probabilities

ep_PVPV=1.0*ep_pr
ep_PVPyr=1.0*ep_pr
ep_VIPSST=0.625*ep_pr
ep_SSTPV=0.857*ep_pr
ep_SSTVIP=1.0*ep_pr
ep_SSTPyr=1.0*ep_pr
ep_PyrIn=0.135
ep_PyrPyr=0.101


# Relative Inhibitory strength

g=0.3 # 3.0

# Indegrees for L4-L2/3 connection
N_L4exex=98
N_L4exin=70
N_L4inex=47
N_L4inin=29

# Synaptic Strength (in mV)
J_ex=0.15
J_in=-(g*J_ex)


# Synaptic Strength for different inhibitory populations (in mV)
J_PVPV=-11.3
J_PVPyr=-11.2
J_VIPSST=-2.688
J_SSTPV=-4.312
J_SSTVIP=-8.624
J_SSTPyr=-6.048


# Background input rates

p_bgexrate=10000.0
p_bgpvrate=10000.0
p_bgviprate=7000.0
p_bgsstrate=7000.0



# Neuron Parameters

C_m=0.25            # (in  microfarads)
V_th=-50.0          # (in mV)
V_reset=-65.0       # (in mV)
tau_m=10.0          # (in ms)
tau_r=2.0           # (in ms)

neuron_params={'cm':C_m,'tau_m':tau_m,'v_rest':V_reset,'v_reset':V_reset,'v_thresh':V_th}

# Layer 4 inputs to Layer 2/3 neurons (modelled by poisson inputs)

p_rate=4.0
ex_rateL4exex=N_L4exex*p_rate
ex_rateL4exin=N_L4exin*p_rate
ex_rateL4inex=N_L4inex*p_rate
ex_rateL4inin=N_L4inin*p_rate






