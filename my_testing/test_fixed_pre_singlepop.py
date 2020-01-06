import spynnaker8 as sim

n_neurons = 5
weights = 0.5
delays = 7

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)

p1 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')

connector_pre = sim.FixedNumberPreConnector(n_neurons+2,
                                            with_replacement=True)

proj_pre = sim.Projection(p1, p2, connector_pre,
                          synapse_type=sim.StaticSynapse(
                              weight=weights, delay=delays))

sim.run(10)

weights_delays_pre = proj_pre.get(["weight", "delay"], "list")
print('fixedpre: ', sorted(weights_delays_pre, key = lambda x: x[1]))

sim.end()
