import spynnaker8 as sim


sim.setup(timestep=1.0)
runtime = 50
populations = []

pop_src1 = sim.Population(2, sim.SpikeSourceArray,
                        {'spike_times': [5, 15, 20, 30]}, label="src1")

populations.append(sim.Population(2, sim.Izhikevich(),  label="test"))

# populations[0].set(tau_syn_E=2)
# populations[0].set(tau_syn_I=4)
start_w = 2.5

stdp_model = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=16.7, tau_minus=33.7, A_plus=0.005, A_minus=0.005),
    weight_dependence=sim.AdditiveWeightDependence(
        w_min=0.0, w_max=1.0), weight=start_w)

# define the projections
proj = sim.Projection(
    pop_src1, populations[0], sim.OneToOneConnector(),
    receptor_type="excitatory", synapse_type=stdp_model)

populations[0].record("all")
sim.run(runtime)

print(proj.get(["weight", "delay"], "list"))

sim.end()
