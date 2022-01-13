import spynnaker8 as sim
from spynnaker.pyNN.models.neuron.synapse_dynamics import (
    calculate_spike_pair_additive_stdp_weight)
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt


sim.setup(timestep=1.0)

runtime = 30
n_neurons = 1
start_w = 5.0

neuronParameters = {
        "LIFL": {"cm": 0.27, "i_offset": 0.0, "tau_m": 10.0, "tau_refrac": 1.0,
                 "tau_syn_E": 0.3, "tau_syn_I": 0.3,
                 "v_reset": -60.0, "v_rest": -60.0, "v_thresh": -55.0}
}
initNeuronParameters = {
    "LIFL": {"vInit": -60}
}

pre_spikes = [1, 6, 11, 16, 21]
spikeArray = {'spike_times': [pre_spikes]}

input_pop = sim.Population(n_neurons, sim.SpikeSourceArray(**spikeArray),
                           label='input')

pop1 = sim.Population(n_neurons, sim.IF_curr_exp(**neuronParameters["LIFL"]))
pop1.set(v=initNeuronParameters["LIFL"]["vInit"])
pop2 = sim.Population(n_neurons, sim.IF_curr_exp(**neuronParameters["LIFL"]))
pop2.set(v=initNeuronParameters["LIFL"]["vInit"])

input_proj = sim.Projection(input_pop, pop1, sim.OneToOneConnector(),
                            receptor_type="excitatory",
                            synapse_type=sim.StaticSynapse(weight=5.0, delay=1))

stdp_model = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=5.0, tau_minus=5.0, A_plus=0.1, A_minus=0.1),
    weight_dependence=sim.AdditiveWeightDependence(
        w_min=1.0, w_max=10.0), weight=start_w, delay=1)

stdp_proj = sim.Projection(pop1, pop2, sim.OneToOneConnector(),
                           receptor_type="excitatory",
                           synapse_type=stdp_model)

stdp_model2 = sim.STDPMechanism(
    timing_dependence=sim.SpikePairRule(
        tau_plus=5.0, tau_minus=5.0, A_plus=0.1, A_minus=0.1),
    weight_dependence=sim.AdditiveWeightDependence(
        w_min=1.0, w_max=10.0), weight=start_w, delay=1)

stdp_proj2 = sim.Projection(pop2, pop1, sim.OneToOneConnector(),
                            receptor_type="excitatory",
                            synapse_type=stdp_model2)

pop1.record("all")
pop2.record("all")

run_for = 5
weights1 = []
weights2 = []
for n in range(runtime//run_for):
    sim.run(run_for)
    weights1.append(stdp_proj.get(["weight"], "list"))
    weights2.append(stdp_proj2.get(["weight"], "list"))

pop1_data = pop1.get_data(['v', 'spikes', 'gsyn_exc'])
pop2_data = pop2.get_data(['v', 'spikes', 'gsyn_exc'])

v1 = pop1_data.segments[0].filter(name='v')[0]
v2 = pop2_data.segments[0].filter(name='v')[0]
ge1 = pop1_data.segments[0].filter(name='gsyn_exc')[0]
ge2 = pop2_data.segments[0].filter(name='gsyn_exc')[0]
spikes1 = pop1_data.segments[0].spiketrains
spikes2 = pop2_data.segments[0].spiketrains
print("1->2 weights", weights1)
print("2->1 weights", weights2)
print(v1, ge1, spikes1)
print(v2, ge2, spikes2)

Figure(
    Panel(v1, ylabel="pop1 membrane potential (mV)",
          data_labels=[pop1.label], yticks=True, xlim=(0, runtime)),
    Panel(ge1, ylabel="pop1 excitatory current (mV)",
          data_labels=[pop1.label], yticks=True, xlim=(0, runtime)),
    Panel(spikes1, ylabel="pop2 spikes", xlabel="Time (ms)",
          yticks=True, markersize=2, xlim=(0, runtime)),
    Panel(v2, ylabel="pop2 membrane potential (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    Panel(ge2, ylabel="pop2 excitatory current (mV)",
          data_labels=[pop2.label], yticks=True, xlim=(0, runtime)),
    Panel(spikes2, ylabel="pop2 spikes", xlabel="Time (ms)",
          yticks=True, markersize=2, xlim=(0, runtime)),
    title="Simple synfire chain example",
    annotations="Simulated with {}".format(sim.name())
)

plt.show()
sim.end()