
import spynnaker8 as sim


# Parameters:
simulationParameters = {"simTime": 30, "timeStep": 1.0}
popNeurons = {"ILayer": 2, "LIFLayer": 2}
ILSpike = [[1, 6, 11, 16, 21],[]]
neuronParameters = {
        "LIFL": {"cm": 0.27, "i_offset": 0.0, "tau_m": 10.0, "tau_refrac": 2.0, "tau_syn_E": 0.3, "tau_syn_I": 0.3,
                "v_reset": -60.0, "v_rest": -60.0, "v_thresh": -55.0}
}
initNeuronParameters = {
    "LIFL": {"vInit": -60}
}
synParameters = {
    "LIFL-LIFL": {"tau_plus": 5.0, "tau_minus": 5.0, "A_plus": 0.1, "A_minus": 0.1, "w_max": 10.0, "w_min": 1.0,
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
    ILayer = sim.Population(popNeurons["ILayer"], sim.SpikeSourceArray(spike_times=ILSpike), label="ILayer")
    # LIF neurons
    LIFLayer = sim.Population(popNeurons["LIFLayer"], sim.IF_curr_exp(**neuronParameters["LIFL"]), label="LIFLayer")
    LIFLayer.set(v=initNeuronParameters["LIFL"]["vInit"])

    ######################################
    # Synapses
    ######################################

    # ILayer-LIFLayer -> statics
    ILayer_LIFLayer_conn = sim.Projection(ILayer, LIFLayer, sim.OneToOneConnector(),
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
    LIFLayer_LIFLayer_conn = sim.Projection(LIFLayer, LIFLayer, sim.AllToAllConnector(allow_self_connections=False),
                                           synapse_type=stdp_model)
    # conn_list = [[0,1], [1,0]]
    # LIFLayer_LIFLayer_conn = sim.Projection(LIFLayer, LIFLayer, sim.FromListConnector(conn_list),
    #                                        synapse_type=stdp_model)

    ######################################
    # Record parameters
    ######################################
    LIFLayer.record(["spikes", "v"])
    weightRecorderLIF_LIF = weight_recorder(sampling_interval=simulationParameters["timeStep"], projection=LIFLayer_LIFLayer_conn)

    ######################################
    # Run simulation
    ######################################
    w_LIFL_LIFL = []
    # sim.run(simulationParameters["simTime"], callbacks=[weightRecorderLIF_LIF])
    for n in range(simulationParameters["simTime"]):
        sim.run(1)
        w_LIFL_LIFL.append(LIFLayer_LIFLayer_conn.get(["weight"], "list"))

    ######################################
    # Recall data
    ######################################
    populationData = LIFLayer.get_data(variables=["spikes", "v"])
    LIFLSpikes = populationData.segments[0].spiketrains
    vLIFL = populationData.segments[0].filter(name='v')[0]
    # w_LIFL_LIFL = weightRecorderLIF_LIF.get_weights()

    ######################################
    # End simulation
    ######################################
    sim.end()

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
        self._weights.append(self.projection.get(['weight','delay'], format='list', with_address=True))
        return t + self.interval

    def get_weights(self):
        return self._weights


if __name__ == "__main__":
    ILSpike, LIFLSpikes, vLIFL, w_LIFL_LIFL = main()
    print(ILSpike)
    print(LIFLSpikes)
    print(vLIFL)
    print(w_LIFL_LIFL)