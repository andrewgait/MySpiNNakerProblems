import spynnaker8 as sim

n_neurons = 10
weights = 0.5
delays = 7

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 3)

p1 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')

p1view = p1[2:6]
p2view = p2[3:9]

connector_prob = sim.FixedProbabilityConnector(0.5)

# proj_prob = sim.Projection(p1view, p2view, connector_prob,
proj_prob = sim.Projection(p1, p2, connector_prob,
                           synapse_type=sim.StaticSynapse(
                               weight=weights, delay=delays))
sim.run(10)

weights_delays_prob = proj_prob.get(["weight", "delay"], "list")
print('fixed_prob: ', weights_delays_prob)

sim.end()
