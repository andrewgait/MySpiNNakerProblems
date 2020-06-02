from enum import Enum

from pacman.model.graphs.machine.machine_vertex import MachineVertex
from pacman.model.resources.resource_container \
    import ResourceContainer, ConstantSDRAM

from spinn_front_end_common.abstract_models.impl \
    import MachineDataSpecableVertex
from spinn_front_end_common.utilities.constants \
    import SYSTEM_BYTES_REQUIREMENT

from spinnaker_graph_front_end.utilities import SimulatorVertex
from spinnaker_graph_front_end.utilities.data_utils \
    import generate_system_data_region

from spinn_utilities.overrides import overrides


class Timed_Vertex(
        SimulatorVertex,
        MachineDataSpecableVertex
        ):

    """ A vertex to test timed simulations with start function
    """

    SDRAM_REGIONS = Enum(
        value="SDRAM_REGIONS",
        names=[('SYSTEM', 0)
               ]
        )


    def __init__(self):
        super(Timed_Vertex, self).__init__(
            label = "timed",
            binary_name = "timed.aplx",
            constraints = None
            )


    @property
    @overrides (MachineVertex.resources_required)
    def resources_required (self):
        resources = ResourceContainer (
            sdram = ConstantSDRAM(SYSTEM_BYTES_REQUIREMENT)
            )
        return resources


    @overrides(MachineDataSpecableVertex.generate_machine_data_specification)
    def generate_machine_data_specification(
            self, spec, placement, machine_graph, routing_info, iptags,
            reverse_iptags, machine_time_step, time_scale_factor):

        # Generate the system data region for simulation.c requirements
        generate_system_data_region(spec, self.SDRAM_REGIONS.SYSTEM.value,
                                    self, machine_time_step, time_scale_factor)

        spec.end_specification()
