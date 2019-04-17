import spynnaker8 as sim

sim.setup(timestep=1.0, min_delay=1, max_delay=144)

n_pop = 2
runtime = 1

input_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="input")
out_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="out_pop")

list1 = [(0, 0, 0.5, 16.1),
         (1, 1, 0.5, 17)]
fromlist_in2out = sim.FromListConnector(list1)

proj_in2out = sim.Projection(input_pop, out_pop, fromlist_in2out, # sim.OneToOneConnector(),
                             receptor_type='excitatory',
                             synapse_type=sim.StaticSynapse(weight=(0.5, 0.5),
                                                            delay=(16.1, 17)))

sim.run(runtime)

sim.end()