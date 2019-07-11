import spynnaker8 as sim
import numpy as np

sim.setup(timestep=1.0)
runtime = 1050
populations = []

n_pop = 500
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 200)

spikeat = []
for n in range(runtime):
    if n % 100:
        spikeat.append(n)

pop_src1 = sim.Population(n_pop, sim.SpikeSourceArray,
                        {'spike_times': spikeat}, label="src1")

populations.append(sim.Population(n_pop, sim.IF_curr_exp(),  label="test"))

# populations[0].set(tau_syn_E=2)
# populations[0].set(tau_syn_I=4)
start_w = 0.5

stdp_model = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=10.0, tau_minus=20.0, A_plus=0.05, A_minus=0.05),
    weight_dependence=sim.AdditiveWeightDependence(
        w_min=0.1, w_max=5.0))  #, weight=start_w)

# define the projections
# connector = sim.OneToOneConnector
connector = sim.FixedProbabilityConnector(0.1)
proj = sim.Projection(
    pop_src1, populations[0], connector,
    receptor_type="excitatory", synapse_type=stdp_model)

populations[0].record("all")
sim.run(runtime)

np.set_printoptions(threshold=np.inf)
print(proj.get(["weight", "delay"], "list"))

sim.end()
