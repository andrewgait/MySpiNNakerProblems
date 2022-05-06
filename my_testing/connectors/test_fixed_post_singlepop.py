import pyNN.spiNNaker as sim

n_neurons = 10
weights = 0.5
delays = 7

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 5)

# p1 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1')
p1 = sim.Population(n_neurons, sim.SpikeSourceArray([0]), label='input1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')

# p1view = p1[2:6]
# p2view = p2[3:8]

n_post = 2
# n_post = sim.RandomDistribution('uniform', [2, 5])

connector_post = sim.FixedNumberPostConnector(n_post) #,
#                                               with_replacement=True)

# proj_post = sim.Projection(p1view, p2view, connector_post,
proj_post = sim.Projection(p1, p2, connector_post,
                           synapse_type=sim.StaticSynapse(
                               weight=weights, delay=delays))
sim.run(10)

weights_delays_post = proj_post.get(["weight", "delay"], "list")
print('fixedpost: ', weights_delays_post)

sim.end()
