import pyNN.spiNNaker as sim
from pyNN.random import RandomDistribution, NumpyRNG

sim.setup(timestep=0.1, time_scale_factor=1)
# sim.setup(timestep=1.0)
sim.set_number_of_neurons_per_core(sim.extra_models.Izhikevich_cond, 16)
sim.set_number_of_neurons_per_core(sim.extra_models.Izhikevich_cond_dual, 16)

numCellsPerCol_STR = 125
numCellsPerCol_GPe = 20
numCellsPerCol_SNC = 10
numPoissonInput_str = 60

strd1_pop1 = sim.Population(numCellsPerCol_STR, sim.extra_models.Izhikevich_cond_dual,
                          label='strd1_pop1')
gpe_pop1 = sim.Population(numCellsPerCol_GPe, sim.extra_models.Izhikevich_cond,
                        label='gpe_pop1')

Rate_Poisson_Inp_base = 3
start_Poisson_Inp_base = 100
Duration_Poisson_Inp_base = 9900

spike_source_Poisson_base1_strd1 = sim.Population(
    numPoissonInput_str, sim.SpikeSourcePoisson,
    {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,
     'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base1')
spike_source_Poisson_base2_strd1 = sim.Population(
    numPoissonInput_str, sim.SpikeSourcePoisson,
    {'rate': Rate_Poisson_Inp_base, 'duration': Duration_Poisson_Inp_base,
     'start': start_Poisson_Inp_base}, label='spike_source_Poisson_base2')

distr_strd1 = sim.RandomDistribution('uniform', (9,12), rng=NumpyRNG(seed=85520))

sim.Projection(spike_source_Poisson_base1_strd1, strd1_pop1,
               sim.FixedProbabilityConnector(p_connect=0.1),
               sim.StaticSynapse(weight=0.125, delay=distr_strd1),
               receptor_type='excitatory')

stdp_cort2strd1_NMDA = sim.STDPMechanism(
        timing_dependence=sim.SpikePairRule(
            tau_plus=2, tau_minus=1,
            A_plus=2, A_minus=1),
        weight_dependence=sim.AdditiveWeightDependence(
            w_min=0, w_max=0.0096), weight=0.00001)

sim.Projection(spike_source_Poisson_base2_strd1, strd1_pop1,
               sim.FixedProbabilityConnector(p_connect=0.1),
               synapse_type=stdp_cort2strd1_NMDA,
               receptor_type ='excitatory2')

distr_strd22gpe = sim.RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))

sim.Projection(strd1_pop1, gpe_pop1,
               sim.FixedProbabilityConnector(p_connect=0.15),
               sim.StaticSynapse(weight=0.2, delay=distr_strd22gpe),
               receptor_type='inhibitory')

distr_str2str = RandomDistribution('uniform', (5,7), rng=NumpyRNG(seed=85520))

sim.Projection(strd1_pop1, strd1_pop1,
               sim.FixedProbabilityConnector(p_connect=0.1),
               sim.StaticSynapse(weight=0.12, delay=distr_str2str),
               receptor_type='inhibitory')

snc_pop1 = sim.Population(
    numCellsPerCol_SNC, sim.extra_models.Izhikevich_cond, label='reward_pop1')
DA_concentration_reward = 0.05
max_w=0.0096
sim.Projection(
        snc_pop1, strd1_pop1, sim.AllToAllConnector(),
        synapse_type=sim.extra_models.Neuromodulation(
            weight=DA_concentration_reward, tau_c=100.0, tau_d=5.0, w_max=max_w),
        receptor_type='reward', label='reward synapses')

sim.run(10000)

sim.end()
