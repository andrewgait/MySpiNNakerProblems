import os

import spinnaker_graph_front_end as front_end

from timed_vertex import Timed_Vertex

front_end.setup(
    n_chips_required = 1,
    model_binary_folder=os.path.dirname(__file__)
    )

# instantiate a vertex
front_end.add_machine_vertex_instance(Timed_Vertex())

front_end.run(10000)

front_end.stop()
