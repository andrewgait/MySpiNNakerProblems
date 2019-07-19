import spynnaker8 as sim

NUM_EXCITATORY = 2000

sim.setup(timestep=1.0, min_delay=1.0, max_delay=10.0)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 10)

ex_pop = sim.Population(NUM_EXCITATORY, sim.IF_curr_exp)
in_pop = sim.Population(NUM_EXCITATORY / 4, sim.IF_curr_exp)

sim.Projection(ex_pop, in_pop, sim.FixedProbabilityConnector(0.02),
               receptor_type='excitatory',
               synapse_type=sim.StaticSynapse(weight=0.03))
sim.Projection(ex_pop, ex_pop, sim.FixedProbabilityConnector(0.02),
               receptor_type='excitatory',
               synapse_type=sim.StaticSynapse(weight=0.03))

sim.Projection(in_pop, in_pop, sim.FixedProbabilityConnector(0.02),
               receptor_type='inhibitory',
               synapse_type=sim.StaticSynapse(weight=-0.3))

ie_projection = sim.Projection(
    in_pop, ex_pop, sim.FixedProbabilityConnector(0.02),
    receptor_type='inhibitory', synapse_type=sim.StaticSynapse(weight=-0.3))

ex_pop.record(['spikes'])

sim.run(1200000)
sim.end()