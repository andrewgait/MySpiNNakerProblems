import pyNN.spiNNaker as p
import numpy
numpy.set_printoptions(threshold=numpy.nan)

p.setup(0.2)

print p.get_time_step()

inp = p.Population(1, p.SpikeSourceArray([1.0, 11.0, 21.0]))
pop = p.Population(1, p.IF_curr_exp(tau_refrac=2.0))
pop.record("v")

p.Projection(inp, pop, p.OneToOneConnector(), p.StaticSynapse(weight=10.0))

p.run(10)

v = pop.spinnaker_get_data("v")

print v

v = pop.get_data("v").segments[0].filter(name="v")

print v

p.end()
