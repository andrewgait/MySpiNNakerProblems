
import spynnaker8 as sim
import numpy as np
from spynnaker.pyNN.models.neuron.synapse_dynamics import (
    calculate_spike_pair_additive_stdp_weight)
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

# Parameters:
simulationParameters = {"simTime": 300, "timeStep": 1.0}
popNeurons = {"ILayer": 2, "LIFLayer": 2}
ILSpike = [[10, 60, 110, 160, 210],[]]
neuronParameters = {
        "LIFL": {"cm": 0.27, "i_offset": 0.0, "tau_m": 10.0, "tau_refrac": 1.0,
                 "tau_syn_E": 0.3, "tau_syn_I": 0.3,
                 "v_reset": -60.0, "v_rest": -60.0, "v_thresh": -55.0}
}
initNeuronParameters = {
    "LIFL": {"vInit": -60}
}
synParameters = {
    "LIFL-LIFL": {"tau_plus": 5.0, "tau_minus": 5.0, "A_plus": 1.0,
                  "A_minus": 1.0, "w_max": 10.0, "w_min": 1.0,
                  "initWeight": 5.0, "delay": 1.0, "receptor_type": "STDP"},
    "IL-LIFL": {"initWeight": 5.0, "delay": 1.0, "receptor_type": "excitatory"}
}


# Network and simulation
def main():

    ######################################
    # Setup
    ######################################
    sim.setup(timestep=simulationParameters["timeStep"])

    ######################################
    # Neuron pop
    ######################################
    # Input neurons
    ILayer = sim.Population(
        popNeurons["ILayer"], sim.SpikeSourceArray(spike_times=ILSpike),
        label="ILayer")
    # LIF neurons
    LIFLayer = sim.Population(
        popNeurons["LIFLayer"], sim.IF_curr_exp(**neuronParameters["LIFL"]),
        label="LIFLayer")
    LIFLayer.set(v=initNeuronParameters["LIFL"]["vInit"])

    ######################################
    # Synapses
    ######################################

    # ILayer-LIFLayer -> statics
    ILayer_LIFLayer_conn = sim.Projection(
        ILayer, LIFLayer, sim.OneToOneConnector(),
        synapse_type=sim.StaticSynapse(weight=synParameters["IL-LIFL"]["initWeight"],
                                       delay=synParameters["IL-LIFL"]["delay"]))

    # LIFLayer-ILayer -> STDP
    timing_rule = sim.SpikePairRule(tau_plus=synParameters["LIFL-LIFL"]["tau_plus"],
                                    tau_minus=synParameters["LIFL-LIFL"]["tau_minus"],
                                    A_plus=synParameters["LIFL-LIFL"]["A_plus"],
                                    A_minus=synParameters["LIFL-LIFL"]["A_minus"])
    weight_rule = sim.AdditiveWeightDependence(w_max=synParameters["LIFL-LIFL"]["w_max"],
                                               w_min=synParameters["LIFL-LIFL"]["w_min"])
    stdp_model = sim.STDPMechanism(timing_dependence=timing_rule, weight_dependence=weight_rule,
                                   weight=synParameters["LIFL-LIFL"]["initWeight"],
                                   delay=synParameters["LIFL-LIFL"]["delay"])
    LIFLayer_LIFLayer_conn = sim.Projection(
        LIFLayer, LIFLayer, sim.AllToAllConnector(allow_self_connections=False),
        synapse_type=stdp_model)

    ######################################
    # Record parameters
    ######################################
    LIFLayer.record(["spikes", "v"])
    weightRecorderLIF_LIF = weight_recorder(
        sampling_interval=simulationParameters["timeStep"], projection=LIFLayer_LIFLayer_conn)

    ######################################
    # Run simulation
    ######################################
    sim.run(simulationParameters["simTime"], callbacks=[weightRecorderLIF_LIF])
    # sim.run(simulationParameters["simTime"])

    ######################################
    # Recall data
    ######################################
    populationData = LIFLayer.get_data(variables=["spikes", "v"])
    LIFLSpikes = populationData.segments[0].spiketrains
    vLIFL = populationData.segments[0].filter(name='v')[0]
    w_LIFL_LIFL = weightRecorderLIF_LIF.get_weights()
    # w_LIFL_LIFL = LIFLayer_LIFLayer_conn.get(["weight"], "list")

    ######################################
    # End simulation
    ######################################
    sim.end()

    runtime = simulationParameters["simTime"]
    Figure(
        Panel(vLIFL,
              ylabel="membrane potential (mV)",
              data_labels=[LIFLayer.label], yticks=True, xlim=(0, runtime)),
        Panel(LIFLSpikes,
              ylabel="pop2 spikes",
              xlabel="Time (ms)",
              yticks=True, markersize=2, xlim=(0, runtime)),
        title="STDP 2-neuron example",
        annotations="Simulated with {}".format(sim.name())
    )

    plt.show()

    ######################################
    # Return parameters
    ######################################
    return ILSpike, LIFLSpikes, vLIFL, w_LIFL_LIFL


# http://neuralensemble.org/docs/PyNN/examples/simple_STDP.html
class weight_recorder(object):
    """
    Recording of weights is not yet built in to PyNN, so therefore we need
    to construct a callback object, which reads the current weights from
    the projection at regular intervals.
    """

    def __init__(self, sampling_interval, projection):
        self.interval = sampling_interval
        self.projection = projection
        self._weights = []

    def __call__(self, t):
        self._weights.append(
            self.projection.get('weight', format='list', with_address=True))
        return t + self.interval

    def get_weights(self):
        return self._weights


if __name__ == "__main__":
    ILSpike, LIFLSpikes, vLIFL, w_LIFL_LIFL = main()
    print(ILSpike)
    print(LIFLSpikes)
    print(vLIFL)
    print(w_LIFL_LIFL)

    neuron0_spikes = np.array(LIFLSpikes[0].magnitude)
    neuron1_spikes = np.array(LIFLSpikes[1].magnitude)

    print(neuron0_spikes)
    print(neuron1_spikes)

    initial_weight = synParameters["LIFL-LIFL"]["initWeight"]
    plastic_delay = synParameters["LIFL-LIFL"]["delay"]
    max_weight = synParameters["LIFL-LIFL"]["w_max"]
    a_plus = synParameters["LIFL-LIFL"]["A_plus"]
    a_minus = synParameters["LIFL-LIFL"]["A_minus"]
    tau_plus = synParameters["LIFL-LIFL"]["tau_plus"]
    tau_minus = synParameters["LIFL-LIFL"]["tau_minus"]

    new_weight_exact01 = calculate_spike_pair_additive_stdp_weight(
        neuron0_spikes, neuron1_spikes, initial_weight, plastic_delay,
        max_weight, a_plus, a_minus, tau_plus, tau_minus)
    new_weight_exact10 = calculate_spike_pair_additive_stdp_weight(
        neuron1_spikes, neuron0_spikes, initial_weight, plastic_delay,
        max_weight, a_plus, a_minus, tau_plus, tau_minus)

    print(new_weight_exact01)
    print(new_weight_exact10)