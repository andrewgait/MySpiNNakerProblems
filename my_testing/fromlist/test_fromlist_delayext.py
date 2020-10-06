import spynnaker8 as sim

sim.setup(timestep=1.0, min_delay=1, max_delay=144)
# sim.setup(timestep=0.1, min_delay=0.1, max_delay=14.4)

n_pop = 2
runtime = 1

input_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="input")
out_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="out_pop")

list1 = [(0, 0, 2.0, 10),
         (0, 1, 2.6, 1),
         (1, 1, 3.2, 17)]
# list1 = [(0, 0, 0.5, 1.61),
#          (1, 1, 0.5, 1.7)]
fromlist_in2out = sim.FromListConnector(list1)

# fromlist_in2out = sim.FromListConnector([(0, 0, 2.5, 2), (1, 0, 4.76, 20)])

# proj_in2out = sim.Projection(input_pop, out_pop, sim.OneToOneConnector(),
proj_in2out = sim.Projection(input_pop, out_pop, fromlist_in2out,
                             receptor_type='excitatory',
                             synapse_type=sim.StaticSynapse(weight=0.5, #(0.5, 0.5),
                                                            delay=1.68)) # (1.63, 1.7)))
#                              synapse_type=sim.StaticSynapse())

sim.run(runtime)

print(proj_in2out.get(["weight", "delay"], "list"))

sim.end()