import struct

from data_specification.enums.data_type import DataType

from pacman.model.graphs.machine.machine_vertex import MachineVertex
from pacman.model.resources.resource_container \
    import ResourceContainer, ConstantSDRAM

from spinn_front_end_common.abstract_models.abstract_provides_n_keys_for_partition \
    import AbstractProvidesNKeysForPartition
from spinn_front_end_common.abstract_models.impl \
    import MachineDataSpecableVertex

from spinn_front_end_common.utilities.constants \
    import SYSTEM_BYTES_REQUIREMENT
from spinnaker_graph_front_end.utilities import SimulatorVertex
from spinnaker_graph_front_end.utilities.data_utils \
    import generate_system_data_region

from spinn_utilities.overrides import overrides

# from spinn_pdp2.mlp_types import MLPRegions, MLPConstants


class P_and_R_Vertex(
        SimulatorVertex,
        MachineDataSpecableVertex
        ):

    """ A vertex to implement a simple vertex
        to test simulation pause and resume options
    """

    def __init__(self,
                 gid
                 ):

        self._id = gid

        super(P_and_R_Vertex, self).__init__(
            label = f"p&r{gid}",
            binary_name = "p_and_r.aplx",
            constraints = None
            )

    @property
    def id (self):
        return self._id

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
        # Generate the system data region for simulation .c requirements
        generate_system_data_region(spec, 0,
                                    self, machine_time_step, time_scale_factor)

        spec.end_specification()

