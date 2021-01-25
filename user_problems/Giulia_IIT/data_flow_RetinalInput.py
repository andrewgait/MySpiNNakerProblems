import spynnaker8 as sim
import matplotlib.pyplot as plt
from pacman.model.constraints.key_allocator_constraints import FixedKeyAndMaskConstraint
from pacman.model.graphs.application import ApplicationSpiNNakerLinkVertex
from pacman.model.routing_info import BaseKeyAndMask
from spinn_front_end_common.abstract_models import AbstractProvidesOutgoingPartitionConstraints
from spinn_utilities.overrides import overrides

from spinn_front_end_common.abstract_models \
    import AbstractSendMeMulticastCommandsVertex
from spinn_front_end_common.utility_models.multi_cast_command \
    import MultiCastCommand


from pyNN.utility.plotting import Figure, Panel

# from spynnaker.pyNN.models.neuron.plasticity.stdp.common import plasticity_helpers

simulationFLAG = False

image_w = 304
image_h = 240

NUM_NEUR_IN = 1024
MASK_IN = 0xFFFFFC00
NUM_NEUR_OUT = image_w*image_h


class ICUBInputVertex(
        ApplicationSpiNNakerLinkVertex,
        AbstractProvidesOutgoingPartitionConstraints):

    def __init__(self, spinnaker_link_id, row, board_address=None,
                 constraints=None, label=None):

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=NUM_NEUR_IN, spinnaker_link_id=spinnaker_link_id,
            board_address=board_address, label=label)
        self.__row = row
        self.__key = BaseKeyAndMask(
                base_key=self.__row << 12,  # y part of the key,
                mask=MASK_IN)

    @overrides(AbstractProvidesOutgoingPartitionConstraints.
               get_outgoing_partition_constraints)
    def get_outgoing_partition_constraints(self, partition):
        return [FixedKeyAndMaskConstraint(
            keys_and_masks=[self.__key])]
            # keys, i.e. neuron addresses of the input population that sits in the ICUB vertex,


class ICUBOutputVertex(ApplicationSpiNNakerLinkVertex,
                       AbstractSendMeMulticastCommandsVertex):
    def __init__(self, spinnaker_link_id, board_address=None,
                 constraints=None, label=None):
        ApplicationSpiNNakerLinkVertex.__init__(
            self, NUM_NEUR_OUT, spinnaker_link_id, board_address=board_address,
            label=label)

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
    for y in range(image_h):
        row_connections = []
        for x in range(image_w):
            icub_pixel = int(x) << 1
            neuron_id = (y*image_w) + x
            row_connections.append([icub_pixel, neuron_id, weight, 1])  # off polarity
            row_connections.append([icub_pixel+1, neuron_id, weight, 1])  # on polarity
        connections.append(row_connections)
    return connections


### spinnaker
sim.setup(timestep=1.0, max_delay=16, min_delay=1)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 128)

# set up populations,
input_pops = [
    sim.Population(None, ICUBInputVertex(spinnaker_link_id=0, row=i),
                   label="pop_in_{}".format(i))
    for i in range(240)
]
output = sim.Population(None, ICUBOutputVertex(spinnaker_link_id=0),
                        label="pop_out")

# neural population
neuron_pop = sim.Population(NUM_NEUR_OUT, sim.IF_curr_exp(), label='neuron_pop')
# sim.Projection(pop, neuron_pop, sim.OneToOneConnector(), sim.StaticSynapse(weight=20.0))

connections = create_connections()
for pop, conns in zip(input_pops, connections):
    sim.Projection(pop, neuron_pop, sim.FromListConnector(conns))

sim.external_devices.activate_live_output_to(neuron_pop, output)

if simulationFLAG:
    neuron_pop.record("spikes")
    # neuron_pop.record("all")

    # recordings and simulations
    simtime = 30000  # ms,
    sim.run(simtime)

    exc_spikes = neuron_pop.get_data("spikes")
    # neuron_data = neuron_pop.get_data("all")

    Figure(
        # raster plot of the neuron_pop
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
else:
    # continuous run until key press
    # remember: do NOT record when running in this mode
    # raw_input('Press enter to stop')
    sim.external_devices.run_forever()




sim.end()

print("finished")
