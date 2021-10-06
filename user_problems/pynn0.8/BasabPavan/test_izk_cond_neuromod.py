import spynnaker8 as p

p.setup(timestep=1.0)

numCellsPerCol_STR = 10
numCellsPerCol_SNC = 10
phi_msn_dop = 2.0
runtime = 1000

strd1_pop1 = p.Population(
    numCellsPerCol_STR, p.extra_models.IZK_cond_exp_izhikevich_neuromodulation,
    label='strd1_pop1')
strd2_pop1 = p.Population(
    numCellsPerCol_STR, p.extra_models.IZK_cond_exp_izhikevich_neuromodulation,
    label='strd2_pop1')

reward_pop=p.Population(numCellsPerCol_SNC, p.extra_models.Izhikevich_cond,
                        label='reward_pop1')
synapse_dynamics_reward = p.STDPMechanism(
    timing_dependence=p.extra_models.TimingIzhikevichNeuromodulation(
        tau_plus=10, tau_minus=12, A_plus=1, A_minus=1, tau_c=1000, tau_d=50),
    weight_dependence=p.MultiplicativeWeightDependence(w_min=0, w_max=20),
    weight=1.5, neuromodulation=True)

# and projections are as follows

reward_projections_strd1_pop1 = p.Projection(
    reward_pop, strd1_pop1, p.AllToAllConnector(),
    synapse_type=p.StaticSynapse(weight=phi_msn_dop),
    receptor_type='reward', label='reward synapses')
reward_projections_strd2_pop1 = p.Projection(
    reward_pop, strd2_pop1, p.AllToAllConnector(),
    synapse_type=p.StaticSynapse(weight=phi_msn_dop),
    receptor_type='reward', label='reward synapses')

# '''Projectons from SNR TO REWARD POPULATION of channel1'''
# (think this was copied incorrectly...)
# snr_to_reward_pop1_projection = p.Projection(
#     snr_pop1, reward_pop, p.AllToAllConnector(),
#     synapse_type=p.StaticSynapse(weight=phi_msn_dop),###weight needs to be changed
#     receptor_type='excitatory', label='snrpop1 to rewardpop')

# nothing that uses the synapse_dynamics specified was given, so make something
inject_pop = p.Population(10, p.SpikeSourcePoisson(rate=10), label='inject')

inject_to_pop1_plastic_projection = p.Projection(
    inject_pop, strd1_pop1, p.AllToAllConnector(), synapse_type=synapse_dynamics_reward,
    receptor_type='excitatory', label='modulated')
# inject_to_pop2_plastic_projection = p.Projection(
#     inject_pop, strd2_pop1, p.AllToAllConnector(), synapse_type=synapse_dynamics_reward,
#     receptor_type='excitatory', label='modulated')

p.run(runtime)

p.end()