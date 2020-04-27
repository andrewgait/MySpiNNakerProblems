import spynnaker8 as sim

n_neurons = 10
weights = 1.0
delays = 1.0

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 3)

p1 = sim.Population(n_neurons, sim.SpikeSourceArray(spike_times=[1.0]),
                    label='SSA')
# p1 = sim.Population(n_neurons, sim.IF_cond_exp, {}, label='pop1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')

p1view = p1[2:6]
p2view = p2[3:9]

# connector_total = sim.FixedTotalNumberConnector(20,
#                                                 with_replacement=False)
# connector_total2 = sim.FixedTotalNumberConnector(50,
#                                                  with_replacement=True)
connector_total3 = sim.FixedTotalNumberConnector(10,
                                                 with_replacement=False)

# proj_total = sim.Projection(p1view, p2view, connector_total,
# proj_total = sim.Projection(p1, p2, connector_total,
#                             synapse_type=sim.StaticSynapse(
#                                 weight=weights, delay=delays))
# proj_total2 = sim.Projection(p1, p2, connector_total2,
#                              synapse_type=sim.StaticSynapse(
#                                  weight=weights, delay=delays))
proj_total2_stdp = sim.Projection(p1view, p2view, connector_total3,
                                  synapse_type=sim.STDPMechanism(
                                      sim.SpikePairRule(),
                                      sim.AdditiveWeightDependence(),
                                      weight=weights, delay=delays))

sim.run(10)

# weights_delays_total = proj_total.get(["weight", "delay"], "list")
# weights_delays_total2 = proj_total2.get(["weight", "delay"], "list")
weights_delays_total2_stdp = proj_total2_stdp.get(["weight", "delay"], "list")
# print('fixed_total: ', weights_delays_total)
# print('fixed_total2: ', weights_delays_total2)
print('fixed_total2_stdp: ', weights_delays_total2_stdp)

sim.end()
