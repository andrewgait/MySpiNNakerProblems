import spynnaker8 as p

# Testing the bandit network without the bandit pop, to see if there's some
# weirdness going on

p.setup(timestep=1.0)

# There is some weirdness going on, but only at these pop sizes... ?

input_size = 6
output_size = 2
input_pop = p.Population(input_size, p.IF_curr_exp(), label='inp')

output_pop1 = p.Population(output_size, p.IF_curr_exp(), label='out1')
output_pop2 = p.Population(output_size, p.IF_curr_exp(), label='out2')

i2o1 = p.Projection(input_pop, output_pop1, p.AllToAllConnector(),
                    p.StaticSynapse(weight=2.0, delay=1))
i2o2 = p.Projection(input_pop, output_pop2, p.OneToOneConnector(),
                    p.StaticSynapse(weight=2.0, delay=1))

runtime = 1
p.run(runtime)

p.end()
