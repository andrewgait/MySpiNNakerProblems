import pyNN.spiNNaker as sim
import numpy as np

sim.setup(timestep=1.0)
runtime = 5000
populations = []

n_pop = 3000
n_input = 100
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 100)
# sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 50)

spikeat = []
for n in range(runtime):
    if n % 500:
        spikeat.append(n)

pop_src1 = sim.Population(n_input, sim.SpikeSourceArray,
                        {'spike_times': spikeat}, label="src1")

populations.append(sim.Population(n_pop, sim.IF_curr_exp(),  label="test"))

# populations[0].set(tau_syn_E=2)
# populations[0].set(tau_syn_I=4)
start_w = 0.5

stdp_model = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=10.0, tau_minus=10.0, A_plus=0.5, A_minus=0.5),
    weight_dependence=sim.AdditiveWeightDependence(
        w_min=0.01, w_max=4.0), weight=start_w,
    delay=sim.RandomDistribution('uniform', (2.0, 15.0)))

# define the projections
# connector = sim.OneToOneConnector
connector = sim.FixedProbabilityConnector(0.01)
proj = sim.Projection(
    pop_src1, populations[0], connector,
    receptor_type="excitatory", synapse_type=stdp_model)
# proj = sim.Projection(
#     pop_src1, populations[0], connector,
#     receptor_type="excitatory",
#     synapse_type=sim.StaticSynapse(
#         weight=4.0, delay=sim.RandomDistribution('uniform', (2.0, 15.0))))

populations[0].record("all")
sim.run(runtime)

np.set_printoptions(threshold=np.inf)
weights_delays = proj.get(["weight", "delay"], "list")
print(weights_delays)
print(len(weights_delays))

sim.end()
