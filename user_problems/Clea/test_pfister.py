import pyNN.spiNNaker as sim

source_pop_obj = sim.extra_models.SpikeSourcePoissonVariable(
    rates=rate, starts=start_time, durations=duration)

post_spliter = SplitterAbstractPopulationVertexNeuronsSynapses(1)

source_pop = sim.Population(25, source_pop_obj)

excit_pop = sim.Population(9, IFCondExpBase(**excit_param), label='excitatory',
                           additional_parameters={'splitter': post_spliter})
excit_pop.initialize(v=-105)

inhit_pop = sim.Population(9, sim.IF_cond_exp(**inhit_param), label='inhibitory')
inhit_pop.initialize(v=-100)

timing_stdp = sim.extra_models.PfisterSpikeTriplet(
    tau_plus=20, tau_minus=20, tau_x=40, tau_y=40, A_plus=0, A_minus=0.0001)
weight_stdp = sim.extra_models.WeightDependenceAdditiveTriplet(
    w_min=0, w_max=1.0, A3_plus=0.01, A3_minus=0)

numpy_RNG = NumpyRNG(seed=42)

## STDP on the input projection
stdp_model_triplet = sim.STDPMechanism(
    timing_dependence=timing_stdp, weight_dependence=weight_stdp,
    weight=RandomDistribution('normal', mu=0.1, sigma=0.1, rng=numpy_RNG),
    delay=RandomDistribution('uniform', (1, 5), rng=numpy_RNG))
input_projec = sim.Projection(
    source_pop, excit_pop, sim.AllToAllConnector(),
    synapse_type=stdp_model_triplet, receptor_type="excitatory")

## below is the lateral inhibition mechanism
E2I_projec = sim.Projection(excit_pop, inhit_pop, sim.OneToOneConnector(),
                            synapse_type=sim.StaticSynapse(weight=10.4))
I2E_projec = sim.Projection(inhit_pop, excit_pop, sim.ArrayConnector(ie_conn),
                            receptor_type='inhibitory',
                            synapse_type=sim.StaticSynapse(weight=17))

excit_pop.record(["spikes", "v"])

tstop = 20000
sim.run(tstop)

stdp_weights = input_projec.get(["weights"], "array")

print(stdp_weights)

exc_spikes = excit_pop.get_data("spikes")
exc_v = excit_pop.get_data("v")

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(exc_spikes.segments[0].spiketrains, xlabel="Time/ms", xticks=True,
          yticks=True, markersize=0.2, xlim=(0, tstop)),
    title="pfister: spikes",
    annotations="Simulated with {}".format(sim.name())
)
plt.show()
