# Trying to reproduce from-list related cerebellum problems in a simpler format

# Population sizes for "loaded" cerebellum model:

# golgi           ->        219 neurons
# glomerulus      ->       7073 neurons (SSA)
# granule         ->      88158 neurons
# purkinje        ->         69 neurons
# basket          ->        603 neurons
# stellate        ->        603 neurons
# dcn             ->         12 neurons

# Problems appear to be related to golgi and purkinjie in that instance

# purkinjie connections come from aa (granule exc), bc (basket inh),
# pf (granule exc), sc (stellate inh)

import numpy as np
import pyNN.spiNNaker as sim
import argparse

from spynnaker.pyNN.extra_algorithms.splitter_components import (
    SplitterAbstractPopulationVertexNeuronsSynapses)

parser = argparse.ArgumentParser(description='parser')
parser.add_argument("-n", "--neurons_per_core", help="Number of neurons per core.",
    type=int, default=64)
args = parser.parse_args()
print("neurons per core is ", args.neurons_per_core)

sim.setup(timestep=1.0)

# Here we're just testing "granule->stellate" as it was causing problems,
# seeing what happens

stellate = sim.Population(600, sim.IF_cond_exp, label="stellate",
                          additional_parameters={
                              "splitter": SplitterAbstractPopulationVertexNeuronsSynapses(1, 64, False)})
spikeArray = {'spike_times': [1]}
granule = sim.Population(
    21000, sim.SpikeSourceArray(**spikeArray), label="granule")

global_n_neurons_per_core = args.neurons_per_core

stellate.set_max_atoms_per_core(global_n_neurons_per_core)
granule.set_max_atoms_per_core(20000)

# Load in projections from files
pf_sc = np.loadtxt("conn_pf_sc.txt")
print("check: pf_sc ", len(pf_sc), pf_sc[0])

pf_sc_proj = sim.Projection(granule, stellate,
                            # sim.FromListConnector(pf_sc),
                            sim.AllToAllConnector(),
                            receptor_type="excitatory",
                            label="pf_sc")

sim.run(1000)

sim.end()
