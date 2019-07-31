import spynnaker8 as sp
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin, exp
import pyNN.space as space
source_connection0 = []
source_connection1 = []
vertical_connection = []
horizontal_connection = []
left_connection = []
right_connection = []
#connection = []
spike_time = []
neuron_size = 128*128
for i in range(128*128):
    spike_time.append([])
time_window = 1000

w = 0.8  # Spatial frequency
gamma = 2  # Aspect ratio
sigma = 20  # Decay ratio
lgn_delay = 1.0  # 0.1
g_exc = (4.0 / 1) * 0.00098  # microsiemens
g_exc = (4.0 / 1) * 0.0021   # microsiemens
n_pick = 3  # Number of times to sample
phase = 90
ori_ver = 0
ori_hor = 90
ori_right = 135
ori_left = 45
"""parameter of gabor function"""
Ncell_lgn = 128 * 128
Ncell_exc = 128 ** 2
Ncell_inh = 128 ** 2
"""number of neurons"""
count = 0
## Assign inhibitory phases and orientations
def gabor_probability(x, y, sigma, gamma, phi, w, theta, xc=0, yc=0):

    """
    calculate the gabor function of x and y
    Returns value of the 2D Gabor function at x, y
    sigma: Controls the decay of the exponential term
    gamma: x:y proportionality factor, elongates the pattern
    phi: Phase of the overall pattern
    w: Frequency of the pattern
    theta: Rotates the whole pattern by the angle theta
    xc, yc : Linear translation
    """
    #print("I am in gabor probability")
    transforms_to_radians = np.pi / 180
    theta *= transforms_to_radians
    phi *= transforms_to_radians  # Transforms to radians

    # Translate
    x = x - xc
    y = y - yc

    # Rotate
    aux1 = cos(theta) * x + sin(theta) * y
    y = -sin(theta) * x + cos(theta) * y

    x = aux1

    # Function
    r = x**2 + (gamma * y) ** 2
    exp_part = exp(- r / (2 * sigma**2))
    cos_part = cos(2 * np.pi * w * x + phi)


    return exp_part * cos_part
def gabor_connection(connections, n_pick, g, delay, polarity, posibility,neuron_id):
    """
    Creates connections from the LGN to the cortex with a Gabor profile.
    This function adds all the connections from the LGN to the cortical cell with index = cortical_neuron_index. It
    requires as parameters the cortical_neruon_index, the current list of connections, the lgn population and also
    the parameters of the Gabor function.
    Parameters
    ----
    cortical_neuron_index : the neuron in the cortex -target- that we are going to connect to
    connections: the list with the connections to which we will append the new connnections
    lgn_neurons: the source population
    n_pick: How many times we will sample per neuron
    g: how strong is the connection per neuron
    delay: the time it takes for the action potential to arrive to the target neuron from the source neuron
    polarity: Whether we are connection from on cells (polarity = 1) or off cells (polarity = -1)
    sigma: Controls the decay of the exponential term
    gamma: x:y proportionality factor, elongates the pattern
    phi: Phase of the overall pattern
    w: Frequency of the pattern
    theta: Rotates the whole pattern by the angle theta
    x_cortical, y_cortical : The spatial coordinate of the cortical neuron
    """

            # Calculate the gabor probability
    probability = polarity * posibility
    #print("Before samples",probability," posibiliti is ",posibility)
    probability = np.sum(np.random.rand(n_pick) < probability)  # Samples
    #print("After samples ", probability)
    synaptic_weight = (g / n_pick) * probability
    #print("synaptic weight is ",synaptic_weight)
            # The format of the connector list should be pre_neuron, post_neuron, w, tau_delay
    if synaptic_weight > 0:
        if (neuron_id, neuron_id, synaptic_weight, delay) not in connections:
            connections.append((neuron_id, neuron_id, synaptic_weight, delay))
   #print("in gabor connection, the list is",connections)

def normalize_connection_list(connection_list):
    """
    This function takes a list of tuples represnting the connections from one neuron population to another and returns
    the same list with the connection weights (the third element of the list's tuples) normalized/averaged
    """
   # print("I am in normalize")
    weights = [x[2] for x in connection_list] # Make a list with the weights
    average = sum(weights) / len(weights)  # Calculate the average of the weights

    return [(x[0], x[1], average, x[3]) for x in connection_list]

with open("box_mix_pushbot_whitepaper.txt", "r") as f:
    for data_in_row in f:
        num = data_in_row.index("[")
        time = int(data_in_row[0:num])
        if time > time_window:
            break
        value_str = data_in_row[num:]
        bits = value_str[2:].split("[")
        value = {}
        for element in bits:
            more_bits = element.split(",")
            p_and_count = more_bits[2].split(":")
            count = int(p_and_count[1].split("]")[0])
            x = int(more_bits[0])
            y = int(more_bits[1])
            p = int(p_and_count[0])
            neuron_id = (x * 128) + y
            verposibility = gabor_probability(x,y,sigma,gamma,phase,w,ori_ver)
            gabor_connection(vertical_connection, n_pick,g_exc,lgn_delay,1,verposibility,neuron_id)
            horposibility = gabor_probability(x,y,sigma,gamma,phase,w,ori_hor)
            gabor_connection(horizontal_connection, n_pick, g_exc, lgn_delay, 1, verposibility, neuron_id)
            leftposibility = gabor_probability(x,y,sigma,gamma,phase,w,ori_left)
            gabor_connection(left_connection, n_pick, g_exc, lgn_delay, 1, verposibility, neuron_id)
            rightposibility = gabor_probability(x,y,sigma,gamma,phase,w,ori_right)
            gabor_connection(right_connection, n_pick, g_exc, lgn_delay, 1, verposibility, neuron_id)
            spike_time[neuron_id].append(time)
"""convert data to SpikeSourceArray"""
f.close()
sp.setup(timestep=1.0, min_delay=1.0, max_delay=144.0)  #, time_scale_factor=10)
sp.set_number_of_neurons_per_core(sp.IF_cond_exp, 128)
sp.set_number_of_neurons_per_core(sp.SpikeSourceArray, 128)

cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -55.0,
                   'v_thresh': -50.0
                   }
cell_params_is = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }
cell_params_shape = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }
vertical_connection = normalize_connection_list(vertical_connection)
horizontal_connection = normalize_connection_list(horizontal_connection)
left_connection = normalize_connection_list(left_connection)
right_connection = normalize_connection_list(right_connection)
print('spike_time: ', spike_time)
Input = sp.Population(neuron_size, sp.SpikeSourceArray(spike_times=spike_time))
vertical = sp.Population(neuron_size, sp.IF_cond_exp(**cell_params_lif), label='vertical')
horizontal = sp.Population(neuron_size, sp.IF_cond_exp(**cell_params_lif), label='horizontal')
angel_left = sp.Population(neuron_size, sp.IF_cond_exp(**cell_params_lif), label='angel_left')
angel_right = sp.Population(neuron_size, sp.IF_cond_exp(**cell_params_lif), label='angel_right')
is_vertical = sp.Population(1,sp.IF_cond_exp(**cell_params_is), label='isvertical')
is_horizontal = sp.Population(1,sp.IF_cond_exp(**cell_params_is), label='ishorizontal')
is_angel_left= sp.Population(1,sp.IF_cond_exp(**cell_params_is),label='isangel_left')
is_angel_right = sp.Population(1,sp.IF_cond_exp(**cell_params_is), label='isangel_right')
square = sp.Population(1,sp.IF_cond_exp(**cell_params_shape),label = 'square')
circle = sp.Population(1,sp.IF_cond_exp(**cell_params_shape),label = 'circle')
doll = sp.Population(1,sp.IF_cond_exp(**cell_params_shape),label='doll')
"""Create neurons that we need"""
"""print("I am creating vertical connection")
vertical_connection = create_lgn_to_cortical(Input,vertical,1,n_pick,g_exc,lgn_delay,sigma,gamma,
                                             phases=phase,w=w,orientations=ori_ver)
print("I am creating horizontal connection")
horizontal_connection = create_lgn_to_cortical(Input,horizontal,1,n_pick,g_exc,lgn_delay,sigma,gamma,
                                             phases=phase,w=w,orientations=ori_hor)
print("I am creating left angel connection")
left_connection = create_lgn_to_cortical(Input,angel_left,1,n_pick,g_exc,lgn_delay,sigma,gamma,
                                             phases=phase,w=w,orientations=ori_left)
print("I am creating righ angel connection")
right_connection = create_lgn_to_cortical(Input,angel_left,1,n_pick,g_exc,lgn_delay,sigma,gamma,
                                             phases=phase,w=w,orientations=ori_right)"""
v_proj = sp.Projection(Input,vertical,sp.FromListConnector(vertical_connection))
h_proj = sp.Projection(Input,horizontal,sp.FromListConnector(horizontal_connection))
l_proj = sp.Projection(Input,angel_left,sp.FromListConnector(left_connection))
r_proj = sp.Projection(Input,angel_right,sp.FromListConnector(right_connection))
"""Gabor filter"""

sp.Projection(vertical,is_vertical,sp.AllToAllConnector(),
              sp.StaticSynapse(weight=0.0075,delay=1.0))
sp.Projection(horizontal,is_horizontal,sp.AllToAllConnector(),
              sp.StaticSynapse(weight=0.0075, delay=1.0))
sp.Projection(angel_right,is_angel_right,sp.AllToAllConnector(),
              sp.StaticSynapse(weight=0.0075, delay=1.0))
sp.Projection(angel_left,is_angel_left,sp.AllToAllConnector(),
              sp.StaticSynapse(weight=0.0075, delay=1.0))

"""Edge detection"""
sp.Projection(is_vertical,square,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_vertical,doll,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_horizontal,square,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_horizontal,doll,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_angel_right,doll,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_angel_left,doll,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_angel_left,circle,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
sp.Projection(is_angel_right,circle,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=2.0, delay=1.0))
"""Check shape"""
sp.Projection(square,circle,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=7.5, delay=1.0),
              receptor_type="inhibitory")
sp.Projection(square,doll,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=7.5, delay=1.0),
              receptor_type="inhibitory")
sp.Projection(circle,square,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=7.5, delay=1.0),
              receptor_type="inhibitory")
sp.Projection(circle,doll,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=7.5, delay=1.0),
              receptor_type="inhibitory")
sp.Projection(doll,circle,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=7.5, delay=1.0),
              receptor_type="inhibitory")
sp.Projection(doll,square,sp.OneToOneConnector(),
              sp.StaticSynapse(weight=7.5, delay=1.0),
              receptor_type="inhibitory")

is_vertical.record(['v', 'spikes'])
is_horizontal.record(['v'])
is_angel_left.record(['v'])
square.record(['v'])
circle.record(['v'])
doll.record(['v'])

runtime = 20000

sp.run(runtime)

#v = on.get_data('v')
vd = doll.get_data('v')
vc = circle.get_data('v')
vs = square.get_data('v')
vver = is_vertical.get_data('v')
vhor = is_horizontal.get_data('v')
vlft = is_angel_left.get_data('v')

print('v_proj: ', v_proj.get(["weight", "delay"], "list"))
print('h_proj: ', h_proj.get(["weight", "delay"], "list"))
print('l_proj: ', l_proj.get(["weight", "delay"], "list"))
print('r_proj: ', r_proj.get(["weight", "delay"], "list"))

Figure(
    Panel(vd.segments[0].filter(name='v')[0],
          ylabel="doll Membrane potential (mV)",
          data_labels=[doll.label], yticks=True, xlim=(0, runtime)),
    Panel(vc.segments[0].filter(name='v')[0],
          ylabel="circle Membrane potential (mV)",
          data_labels=[circle.label], yticks=True, xlim=(0, runtime)),
    Panel(vs.segments[0].filter(name='v')[0],
          ylabel="square Membrane potential (mV)",
          data_labels=[square.label], yticks=True, xlim=(0, runtime)),
    Panel(vhor.segments[0].filter(name='v')[0],
          ylabel="is horizontal Membrane potential (mV)",
          data_labels=[is_horizontal.label], yticks=True, xlim=(0, runtime)),
    Panel(vver.segments[0].filter(name='v')[0],
          ylabel="is vertical Membrane potential (mV)",
          data_labels=[is_vertical.label], yticks=True, xlim=(0, runtime)),
    Panel(vlft.segments[0].filter(name='v')[0],
          ylabel="is angel left Membrane potential (mV)",
          data_labels=[is_angel_left.label], yticks=True, xlim=(0, runtime))
)

plt.show()
sp.end()