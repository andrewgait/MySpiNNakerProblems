import spynnaker8 as sim

sim.setup(timestep=1.0, min_delay=1, max_delay=144)

n_pop = 2
runtime = 1

input_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="input")
out_pop = sim.Population(n_pop, sim.IF_curr_exp(), label="out_pop")

list1 = [(0, 0, 2.1),
         (0, 1, 2.6),
         (1, 1, 3.2)]

fromlist_in2out = sim.FromListConnector(list1, column_names=["weight"])

nrng = sim.NumpyRNG(seed=1)

proj_in2out = sim.Projection(
    input_pop, out_pop, fromlist_in2out, receptor_type='excitatory',
    synapse_type=sim.StaticSynapse(
        weight=0.5,
        delay=sim.RandomDistribution('uniform', [1, 10], rng=nrng)))

sim.run(runtime)

print(proj_in2out.get(["weight", "delay"], "list"))

sim.end()