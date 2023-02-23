import numpy as np

import pyNN.spiNNaker as pynn
from pyNN.space import Grid2D


pynn.setup()

neuron_type = pynn.IF_curr_exp(
    tau_m=5.0,
    cm=5.0,
    v_rest=0.0,
    v_reset=0.0,
    v_thresh=0.5,
    tau_refrac=1.0,
    i_offset=0.0,
    v=0.0,
)

kernel = np.array(((2.0,),))

connector = pynn.ConvolutionConnector(kernel)

input_spikes = np.array((
    (), (), (),
    (), (0.0,), (),
    (), (), (),
), dtype=object)
# input_spikes = [0]

spike_source = pynn.SpikeSourceArray(spike_times=input_spikes)

input_shape = (3, 3)
input_height, input_width = input_shape
num_neurons = input_height * input_width

input_neurons = pynn.Population(
    num_neurons,
    spike_source,
    label='Input neurons') #,
    # structure=Grid2D(input_width / input_height))

output_height, output_width = connector.get_post_shape(input_shape)
num_output_neurons = output_width * output_height

print("num_neurons ", num_neurons)
print("num_output_neurons ", num_output_neurons)

# conv_neurons = pynn.Population(
#     num_output_neurons,
#     neuron_type,
#     label='Convolutional neurons',
#     structure=Grid2D(output_width / output_height))
#
# pynn.Projection(input_neurons, conv_neurons, connector, pynn.Convolution())

merge_neurons = pynn.Population(
    num_output_neurons,
    neuron_type,
    label='Merge neurons',
    structure=Grid2D(output_width / output_height))

pynn.Projection(
    # conv_neurons,
    input_neurons,
    merge_neurons,
    pynn.OneToOneConnector(),
    pynn.StaticSynapse(weight=2.0))

# conv_neurons.record("spikes")
merge_neurons.record("spikes")

duration = 10
pynn.run(duration)

# spikes_conv = conv_neurons.get_data("spikes")
spikes_out = merge_neurons.get_data("spikes")

# print("spikes_conv", spikes_conv.segments[0].spiketrains)
print("spikes_out", spikes_out.segments[0].spiketrains)

pynn.end()