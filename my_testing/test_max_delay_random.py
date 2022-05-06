import pyNN.spiNNaker as sim

sim.setup(0.1)

pop_a = sim.Population(100, sim.IF_curr_exp(i_offset=5.0))
pop_b = sim.Population(100, sim.IF_curr_exp())

exc_delays = sim.RandomDistribution("normal_clipped", mu=1.5*15,
                                    sigma=0.75*15, low=0.1*15, high=14.4*15)
proj = sim.Projection(pop_a, pop_b, sim.AllToAllConnector(),
                      sim.StaticSynapse(delay=exc_delays))

sim.run(1000)

sim.end()