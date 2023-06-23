# Copyright (c) 2017-2022 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Interference detection Network
"""
import pyNN.spiNNaker as p
from pyNN.space import Grid2D
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np
# from support_functions import myFunc
#from generator/ESA_interference_detection/interference_detection import *

def unpackConv2DMatrices(name):
    """
    """
    fileName = "./tc_intf/ed_params4/%s/parameters.npz" % name
    excWholeMatrix = list()
    inhWholeMatrix = list()
    data = np.load(fileName, "r")
    weights = data['weight']
    #print(weights)
    excChanMatrix = list()
    inhChanMatrix = list()
    #for chan in range(len(weights)):
    #    # print("x dim %d" % len(weights[chan][0]))
    #    excList = list()
    #    inhList = list()
    #    for element in weights[chan].flatten():
    #        if element >= 0.0:
    #            excList.append(element)
    #            inhList.append(0.0)
    #        else:
    #            inhList.append(-element)
    #            excList.append(0.0)
    #    excChanMatrix.append(excList)
    #    inhChanMatrix.append(inhList)
    for chan in range(len(weights)):
        excChanMatrix.append(weights[chan][0])
        inhChanMatrix.append(weights[chan][0])

    return excChanMatrix, inhChanMatrix

def unpackLinearMatrices(name):
    """
    """
    fileName = "./ed_params4/%s/parameters.npz" % name
    excWholeMatrix = list()
    inhWholeMatrix = list()
    data = np.load(fileName, "r")
    weights = data['weight']
    # print("x dim %d" % len(weights))
    for i in range(len(weights)):
        excList = list()
        inhList = list()
        # print("y dim %d" % len(weights[0]))
        for j in range(len(weights[0])):
            element = weights[i ,j]
            if element >= 0.0:
                excList.append(element)
                inhList.append(0.0)
            else:
                inhList.append(-element)
                excList.append(0.0)
        excWholeMatrix.append(excList)
        inhWholeMatrix.append(inhList)

    return excWholeMatrix, inhWholeMatrix

def padMatrixTo3x3(myMatrix):
    """
    """
    newMatrix = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])

    x, y =(len(myMatrix), len(myMatrix[0]))
    #print("x: %d" % x)
    #print("y: %d" % y)

    for i in range(x):
        for j in range(y):
            newMatrix[i+1][j+1] = myMatrix[i][j]

    return newMatrix

SUB_WIDTH = 2 # 8
SUB_HEIGHT = 32 # 8

runtime = 50
timestep = 1.0
p.setup(timestep=timestep, min_delay=timestep)
# p.set_number_of_neurons_per_core(p.IF_maxPool, (SUB_WIDTH, SUB_HEIGHT))
# p.set_number_of_neurons_per_core(p.IF_curr_chen, (SUB_WIDTH, SUB_HEIGHT))
p.set_number_of_neurons_per_core(p.IF_curr_exp, (SUB_WIDTH, SUB_HEIGHT))
p.set_number_of_neurons_per_core(p.SpikeSourceArray, (2, 256))

cell_params_maxPool = {
                   'x_range': 4,
                   'y_range': 4,
                   'x_fanIn': 2,
                   'y_fanIn': 2
                   }

cell_params_chen = {'v_reset' : 0.0,
                   'v_rest'   : 0.0,
                   'v_thresh' : 1.0
                   }

populations = list()
projections = list()

layers = dict()
layer_count = 0
connections = dict()
connection_count = 0

pop_inpExc  = 0
pop_inpInh  = 1
pop_negSrc  = 2
pop_negSSA  = 3
pop_maxPool = 4
oneRow = list()
spikeList = list()
for i in range(256):
    oneRow.append([0.2*i])
for j in range(2):
    spikeList.extend(oneRow)
spikeArray      = {'spike_times': spikeList}

#populations.append(p.Population(4, p.IF_curr_chen(**cell_params_chen), label='neg_source'))

#populations.append(p.Population(4, p.IF_maxPool(**cell_params_maxPool), label='pop_maxPool'))

##############################################
### Layer declarations

### Input Stimuli:
layer_label = "L0_Stim"
populations.append(p.Population(2*256, p.SpikeSourceArray(**spikeArray), label=layer_label,
                                structure=Grid2D(2/256)))
layers[layer_label] = layer_count
layer_count += 1

### Sequence 1-2:
### L2-4, Conv2d 2x256 -> 2x256, channels = 32
L2_4_channels = 32
for i in range(L2_4_channels):
    layer_label = "L2-4_conv2d_%d" % i
    populations.append(p.Population(2*256, p.IF_curr_exp(), label=layer_label,
                                    structure=Grid2D(2 / 256)))
    layers[layer_label] = layer_count
    layer_count += 1

### Convolutional connector from L0 to L2-4:
exc1, inh1 = unpackConv2DMatrices('encoder.0')
num_kernels = len(exc1)
print("Layer L2-4, channels = %d" % num_kernels)

for i in range(num_kernels):
    layer_label = "L2-4_conv2d_%d" % i
    connE = p.KernelConnector(weight_kernel = np.asarray(exc1[i]), shape_pre = [2, 256], shape_post = [2, 256],
                                                  shape_kernel = [2, 2],
                                                  pre_start_coords_in_post = [1, 1],
                                                  pre_sample_steps_in_post = [1, 1] )
    conn_label = "L0->L2-4E_%d" % i
    connections[conn_label] = connection_count
    connection_count += 1
    projections.append(p.Projection(populations[layers["L0_Stim"]], populations[layers[layer_label]], connE,
                                    synapse_type=p.StaticSynapse()))

    connI = p.KernelConnector(weight_kernel = np.asarray(inh1[i]), shape_pre = [2, 256], shape_post = [2, 256],
                                                  shape_kernel = [2, 2],
                                                  pre_start_coords_in_post = [1, 1],
                                                  pre_sample_steps_in_post = [1, 1] )
    conn_label = "L0->L2-4I_%d" % i
    connections[conn_label] = connection_count
    connection_count += 1
    projections.append(p.Projection(populations[layers["L0_Stim"]], populations[layers[layer_label]], connI,
                                    receptor_type = 'inhibitory', synapse_type=p.StaticSynapse()))

###############---
# L2-6, MaxPool2d 2x256 -> 2x128
L2_6_channels = 32
for i in range(L2_6_channels):
    layer_label = "L2-6_maxPool_%d" % i
    populations.append(p.Population(2*128, p.IF_curr_exp(), label=layer_label,
                                    structure=Grid2D(2/128)))
    layers[layer_label] = layer_count
    layer_count += 1

### Convolutional connector from L2-4 to L2-6:
#conn = p.KernelConnector(weight_kernel=np.asarray([[1.0, 1.0], [1.0, 1.0]]),
# Each of 32 input channels connects to one of the 32 output channels.
for i in range(L2_6_channels):
    conn = p.KernelConnector(weight_kernel=np.asarray([[1.0, 1.0]]),
                         shape_pre  = [2, 256],
                         shape_post = [2, 128],
                         shape_kernel = [1, 2], #, # was 2,2
                         post_start_coords_in_pre = [1, 1],
                         post_sample_steps_in_pre = [1, 2])

    conn_label = "L2-4E->L2-6_%d" % i
    connections[conn_label] = connection_count
    connection_count += 1
    from_label = "L2-4_conv2d_%d" % i
    projections.append(p.Projection(populations[layers[from_label]], populations[layers[layer_label]], conn, synapse_type=p.StaticSynapse()))

p.run(runtime)

print("Layers: %d" % layer_count)
print("Connections count: %d " % connection_count)

print(projections[-1].get(["weight"], "list"))

p.end()

# quit()
#
# ##################################################
# # Run simulation
#
# p.run(runtime)

