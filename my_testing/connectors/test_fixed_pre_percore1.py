import pyNN.spiNNaker as sim
# from pyNN.random import NumpyRNG, RandomDistribution

n_neurons = 100
weights = 0.5
delays = 7

# rngseed = 3423652
# rng = NumpyRNG(seed=rngseed, parallel_safe=True)
# delays = RandomDistribution('uniform', [11, 20], rng=rng)

sim.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 50)

p1 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop1')
p2 = sim.Population(n_neurons, sim.IF_curr_exp, {}, label='pop2')
# rng = NumpyRNG(seed=None, parallel_safe=True)
connector_pre = sim.FixedNumberPreConnector(2)
connector_post = sim.FixedNumberPostConnector(2)
# connector = sim.FixedProbabilityConnector(0.2)
proj_pre = sim.Projection(p1, p2, connector_pre,
                          synapse_type=sim.StaticSynapse(
                              weight=weights, delay=delays))
proj_post = sim.Projection(p1, p2, connector_post,
                           synapse_type=sim.StaticSynapse(
                               weight=weights, delay=delays))
sim.run(10)

weights_delays_pre = proj_pre.get(["weight", "delay"], "list")
weights_delays_post = proj_post.get(["weight", "delay"], "list")
print('fixedpre: ', weights_delays_pre)
print('fixedpost: ', weights_delays_post)

sim.end()
