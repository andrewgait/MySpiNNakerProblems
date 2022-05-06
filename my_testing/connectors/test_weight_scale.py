import pyNN.spiNNaker as sim
import numpy
import csv

sim.setup(timestep=1.0)

input_pop = sim.Population(100, sim.SpikeSourcePoisson(rate=2.0), label='input')

output_pop = sim.Population(100, sim.IF_curr_exp(), label='output')

rng = sim.NumpyRNG(100)

w_mean = 0.0878

w_rand = sim.RandomDistribution(
    "normal_clipped", mu=w_mean, sigma=0.2, low=0, high=numpy.inf, rng=rng)
w_rand_inh = sim.RandomDistribution(
    "normal_clipped", mu=-4*w_mean, sigma=0.2, low=-numpy.inf, high=0, rng=rng)
d_rand = sim.RandomDistribution("uniform", low=1, high=10)

proj = sim.Projection(input_pop, output_pop, sim.OneToOneConnector(),
                      sim.StaticSynapse(weight=w_rand,delay=d_rand))

proj_inh = sim.Projection(input_pop, output_pop,
                          sim.FixedProbabilityConnector(0.5),
                          sim.StaticSynapse(weight=w_rand_inh, delay=d_rand),
                          receptor_type='inhibitory')

sim.run(1000)

weights_delays = proj.get(["weight", "delay"], "list")
weights_delays_inh = proj_inh.get(["weight", "delay"], "list")

print(weights_delays)
print(" ")
print(weights_delays_inh)

sim.end()

f = open("test_ws_weights_delays.csv", "w")
write = csv.writer(f)
for weight_delay in weights_delays:
    weight_delay_list = list(weight_delay)
    write.writerow(weight_delay_list)

for weight_delay_inh in weights_delays_inh:
    weight_delay_inh_list = list(weight_delay_inh)
    write.writerow(weight_delay_inh_list)

f.close()