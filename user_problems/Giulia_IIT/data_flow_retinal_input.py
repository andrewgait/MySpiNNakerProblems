import socket
import spynnaker8 as sim
import numpy as np
#import logging
import matplotlib.pyplot as plt

from pacman.model.constraints.key_allocator_constraints import FixedKeyAndMaskConstraint
from pacman.model.graphs.application import ApplicationSpiNNakerLinkVertex
from pacman.model.routing_info import BaseKeyAndMask
#from spinn_front_end_common.abstract_models.abstract_provides_n_keys_for_partition import AbstractProvidesNKeysForPartition
from spinn_front_end_common.abstract_models.abstract_provides_outgoing_partition_constraints import AbstractProvidesOutgoingPartitionConstraints
from spinn_utilities.overrides import overrides
from spinn_front_end_common.abstract_models.abstract_provides_incoming_partition_constraints import AbstractProvidesIncomingPartitionConstraints
from pacman.executor.injection_decorator import inject_items
from pacman.operations.routing_info_allocator_algorithms.malloc_based_routing_allocator.utils import get_possible_masks
from spinn_front_end_common.utility_models.command_sender_machine_vertex import CommandSenderMachineVertex

from spinn_front_end_common.abstract_models \
    import AbstractSendMeMulticastCommandsVertex
from spinn_front_end_common.utility_models.multi_cast_command \
    import MultiCastCommand


from pyNN.utility import Timer
from pyNN.utility.plotting import Figure, Panel
from pyNN.random import RandomDistribution, NumpyRNG

# from spynnaker.pyNN.models.neuron.plasticity.stdp.common import plasticity_helpers

NUM_NEUR_IN = 2**20 #2**20bits -> 0xFFFE0000 #1024 -> 0xFFFFFC00 # 2x240x304 mask -> 0xFFFE0000
MASK_IN = 0xFFFE0000
NUM_NEUR_OUT = 304*240 #1024
#MASK_OUT =0xFFFFFC00

class ICUBInputVertex(
        ApplicationSpiNNakerLinkVertex,
        AbstractProvidesOutgoingPartitionConstraints,
        AbstractProvidesIncomingPartitionConstraints,
        AbstractSendMeMulticastCommandsVertex):

    def __init__(self, spinnaker_link_id, board_address=None,
                 constraints=None, label=None):

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=NUM_NEUR_IN, spinnaker_link_id=spinnaker_link_id,
            board_address=board_address, label=label)

        #AbstractProvidesNKeysForPartition.__init__(self)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)
        AbstractSendMeMulticastCommandsVertex.__init__(self)

    @overrides(AbstractProvidesOutgoingPartitionConstraints.
               get_outgoing_partition_constraints)
    def get_outgoing_partition_constraints(self, partition):
        return [FixedKeyAndMaskConstraint(
            keys_and_masks=[BaseKeyAndMask(
                base_key=0, #upper part of the key,
                mask=MASK_IN)])]
                #keys, i.e. neuron addresses of the input population that sits in the ICUB vertex,

    # @inject_items({"graph_mapper": "MemoryGraphMapper"})
    @overrides(AbstractProvidesIncomingPartitionConstraints.
               get_incoming_partition_constraints)
               # additional_arguments=["graph_mapper"])
    def get_incoming_partition_constraints(self, partition):#, graph_mapper):
        if isinstance(partition.pre_vertex, CommandSenderMachineVertex):
            return []
        # index = graph_mapper.get_machine_vertex_index(partition.pre_vertex)
        # vertex_slice = graph_mapper.get_slice(partition.pre_vertex)
        index = partition.pre_vertex.index
        vertex_slice = partition.pre_vertex.vertex_slice
        mask = get_possible_masks(vertex_slice.n_atoms)[0]
        key = (0x1000 + index) << 16
        return [FixedKeyAndMaskConstraint(
            keys_and_masks=[BaseKeyAndMask(key, mask)])]

    @property
    @overrides(AbstractSendMeMulticastCommandsVertex.start_resume_commands)
    def start_resume_commands(self):
        return [MultiCastCommand(
            key=0x80000000, payload=0, repeat=5, delay_between_repeats=100)]

    @property
    @overrides(AbstractSendMeMulticastCommandsVertex.pause_stop_commands)
    def pause_stop_commands(self):
        return [MultiCastCommand(
            key=0x40000000, payload=0, repeat=5, delay_between_repeats=100)]

    @property
    @overrides(AbstractSendMeMulticastCommandsVertex.timed_commands)
    def timed_commands(self):
        return []

def convert_pixel_to_id(x, y):
    return (int(y) << 12) + (int(x) << 1) + 0  # +0 = 0 polarity, +1 = on

def create_connections(weight=20):
    connections = []
    for x in range(304):
        for y in range(240):
            icub_pixel = convert_pixel_to_id(x, y)
            neuron_id = (y*304) + x
            connections.append([icub_pixel, neuron_id, weight, 1])  # off polarity
            connections.append([icub_pixel+1, neuron_id, weight, 1])  # on polarity
    return connections

sim.setup(timestep=1.0, max_delay=16, min_delay=1)
# sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 128)

# set up populations,
pop = sim.Population(None, ICUBInputVertex(spinnaker_link_id=0), label='pop_in')

#neural population    ,
neuron_pop = sim.Population(NUM_NEUR_OUT, sim.IF_curr_exp(), label='neuron_pop')

# sim.Projection(pop, neuron_pop, sim.OneToOneConnector(), sim.StaticSynapse(weight=20.0))
connections = create_connections()
sim.Projection(pop, neuron_pop, sim.FromListConnector(connections))

#pop_out = sim.Population(None, ICUBOutputVertex(spinnaker_link_id=0), label='pop_out')

sim.external_devices.activate_live_output_to(neuron_pop,pop)

#recordings and simulations,
neuron_pop.record("spikes")
# neuron_pop.record("all")


simtime = 30000 #ms,
sim.run(simtime)

# continuous run until key press
# remember: do NOT record when running in this mode
# sim.external_devices.run_forever()
# raw_input('Press enter to stop')

exc_spikes = neuron_pop.get_data("spikes")

# neuron_data = neuron_pop.get_data("all")

Figure(
#     raster plot of the neuron_pop
    Panel(exc_spikes.segments[0].spiketrains, xlabel="Time/ms", xticks=True,
          yticks=True, markersize=0.2, xlim=(0, simtime)),

    # Panel(neuron_data.segments[0].filter(name='v')[0], ylabel='Membrane potential (mV)', yticks=True, xticks=True,
    #       xlim=(0, simtime)),
    #
    # Panel(neuron_data.segments[0].filter(name='gsyn_exc')[0], ylabel='gsyn_exc', yticks=True, xticks=True,
    #       xlim=(0, simtime)),
    #
    # Panel(neuron_data.segments[0].filter(name='gsyn_inh')[0], ylabel='gsyn_inh', yticks=True, xticks=True,
    #       xlim=(0, simtime)),
    #
    # title = "neuron_pop: spikes"

)


plt.show()

sim.end()

print("finished")
