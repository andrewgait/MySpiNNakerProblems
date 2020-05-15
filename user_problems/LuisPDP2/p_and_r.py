import os

import spinnaker_graph_front_end as front_end

from p_and_r_vertex import P_and_R_Vertex

front_end.setup(
    n_chips_required = 1,
    model_binary_folder=os.path.dirname(__file__)
    )

# instantiate a p_and_r vertex
front_end.add_machine_vertex_instance(P_and_R_Vertex (gid = 16))

#front_end.run(10000)
front_end.run_until_complete()

# pause to allow debugging using ybug
input ('paused: press enter to exit')

front_end.stop()
