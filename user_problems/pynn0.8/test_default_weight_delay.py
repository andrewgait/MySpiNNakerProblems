import spynnaker8 as sim

sim.setup(timestep=1.0)

neuron_size = 1

input = sim.Population(neuron_size, sim.SpikeSourceArray([[1]]),
                       label='source')
receiver = sim.Population(neuron_size, sim.IF_curr_exp())

proj = sim.Projection(input, receiver, sim.OneToOneConnector(),
                      receptor_type='excitatory')

sim.run(100)

print("weights_delays: ", proj.get(["weight", "delay"], "list"))

sim.end()