import pyNN.spiNNaker as sim
import pyNN.utility.plotting as plot
from pyNN.random import NumpyRNG, RandomDistribution
import torch
import torchvision

from norse.torch.module import encode

# Setup the Simulator
sim.setup(timestep=1.0,time_scale_factor=10)
sim.set_number_of_neurons_per_core(sim.IF_curr_exp, 50)
# sim.set_number_of_neurons_per_core(sim.SpikeSourceArray, 50)

BATCH_SIZE = 500
input_size = 10000
transform = torchvision.transforms.Compose(
    [
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.1307,), (0.3081,)),
    ]
)

train_data = torchvision.datasets.MNIST(
    root=".",
    train=True,
    download=True,
    transform=transform,
)

test_loader = torch.utils.data.DataLoader(
    torchvision.datasets.MNIST(
        root=".",
        train=False,
        transform=transform,
    ),
    batch_size=BATCH_SIZE,
)

N_BATCH = len(train_data) / BATCH_SIZE

input_size = 10000

encoder = encode.SpikeLatencyLIFEncoder(20)
testset = [[0,0] for l in range(input_size)]
X = 0
for data,targets in test_loader:#train_loader:

    for x,t in zip(data,targets):
        testset[X][0] = encoder(x)
        testset[X][1] = t
        X+=1

class_selector = [0,1,2,3,4,5,6,7,8,9]
time_per_exp = 20 # Time in ms per input
input_per_class = []

i = 0
while len(input_per_class) < input_size:
    if (int(testset[i][1]) in class_selector):
        input_per_class.append(testset[i])
    i+=1

import datetime
labels=[]
i=0
while len(labels) < input_size:
#    if (int(testset[i][1]) in class_selector):
    labels.append(int(testset[i][1]))
    i+=1
#np.save(str(datetime.datetime.now())+'_labels.npy',labels)

a=[10 for _ in range(len(labels))]
labels=torch.tensor(labels)
a=torch.tensor(a)
(labels==a).sum()

spike_array = [[] for _ in range(28*28)]
num_examples_seen = {c:0 for c in class_selector}

for data in input_per_class[:-1]:
    frame = 0
    for sdata in data[0]:
        wave = torch.flatten(sdata[0])
        x = 0
        for w in wave:
            if w != 0:
                spike_array[x].append(frame+time_per_exp*sum(num_examples_seen.values()))
            x+=1

        frame+=1

    num_examples_seen[int(data[1])]+=1
#np.save('spike_array_by_SpiNNaker_MNIST.npy',spike_array)
#np.save('num_examples_seen_by_SpiNNaker_MNIST.npy',num_examples_seen)

num_events=0
for i in spike_array:
    num_events+=len(i)
print("Number of events is "+str(num_events))

# Important Variables
n_excitatory_neurons = 1600
excitatory_neuron_parameters = {
    'v_rest':     0.0,  # Resting membrane potential in mV. -65.0
    'cm':         1.0,  # Capacity of the membrane in nF 1.0
    'tau_m':     100.0,  # Membrane time constant in ms. 100.0
    'tau_refrac': 2.0,  # Duration of refractory period in ms. 5.0
    'tau_syn_E':  1.0,  # Decay time of the excitatory synaptic conductance in ms. 1.0
    'tau_syn_I':  2.0,  # Decay time of the inhibitory synaptic conductance in ms. 2.0
    #'e_rev_E':    0.0,  # Reversal potential for excitatory input in mV
    #'e_rev_I':  0.0,  # Reversal potential for inhibitory input in mV
    'v_thresh': 1.0,  # Spike threshold in mV. -52.0
    'v_reset':  0.0,  # Reset potential after a spike in mV. -65.0
    'i_offset':   0.0,  # Offset current in nA
}
n_inhibitory_neurons = n_excitatory_neurons
inhibitory_neuron_parameters = {
    'v_rest':   -60.0,  # Resting membrane potential in mV.
    'cm':         1.0,  # Capacity of the membrane in nF
    'tau_m':     10.0,  # Membrane time constant in ms.
    'tau_refrac': 2.0,  # Duration of refractory period in ms.
    'tau_syn_E':  0.3,  # Decay time of the excitatory synaptic conductance in ms. 1.0
    'tau_syn_I':  0.3,  # Decay time of the inhibitory synaptic conductance in ms. 2.0
    'e_rev_E':    0.0,  # Reversal potential for excitatory input in mV
    'e_rev_I':  -85.0,  # Reversal potential for inhibitory input in mV
    'v_thresh': -40.0,  # Spike threshold in mV.
    'v_reset':  -45.0,  # Reset potential after a spike in mV.
    'i_offset':   0.0,  # Offset current in nA
}

# input
inp = sim.Population(28*28,
                   sim.SpikeSourceArray(spike_array),
                   label="Input"
                  )
# excitatory
exc = sim.Population(n_excitatory_neurons,
                   sim.IF_curr_exp(**excitatory_neuron_parameters),#sim.IF_cond_exp(**excitatory_neuron_parameters),
                   initial_values={'v': excitatory_neuron_parameters["v_rest"]},
                   label="Excitatory"
                  )
# inhibitory
inh = sim.Population(n_inhibitory_neurons,
                   sim.IF_curr_exp(**excitatory_neuron_parameters),#sim.IF_cond_exp(**excitatory_neuron_parameters),
                   initial_values={'v': excitatory_neuron_parameters["v_rest"]},
                   label="Inhibitory"
                  )

# Record Spikes
inp.record("spikes") # Testing
exc.record(["spikes",'v']) # ,'gsyn_exc', 'gsyn_inh'
inh.record(["spikes",'v']) # ,'gsyn_exc', 'gsyn_inh'

min_weight = 0
max_weight = 1

# Input -> E

#c_con=sim.FromFileConnector('weights_28_28_0_1600_pruned.txt')

w = RandomDistribution('gamma', [1, 0.1])

proj_1=sim.Projection(inp,exc,
                    connector = sim.FixedProbabilityConnector(p_connect=0.7, rng=NumpyRNG(seed=98497627)),
                    synapse_type=sim.StaticSynapse(weight=w,delay=1)
                    )



# E -> I

sim.Projection(presynaptic_population = exc,
             postsynaptic_population = inh,
             connector = sim.OneToOneConnector(),
             synapse_type = sim.StaticSynapse(weight=1),
             receptor_type = 'excitatory'
            )

# I -> E (WTA)

i_e_connection_list = []
for i in range(n_excitatory_neurons):
    for j in range(n_inhibitory_neurons):
        if not i==j:
            i_e_connection_list.append((i,j))

sim.Projection(presynaptic_population = inh,
             postsynaptic_population = exc,
             connector = sim.FromListConnector(i_e_connection_list),
             synapse_type = sim.StaticSynapse(weight=10), # 0.0625 ,delay=1.0
             receptor_type = 'inhibitory'
            )

# Simulating
sim.run(sum(num_examples_seen.values())*time_per_exp)

# Getting Weights and spikes
weights = proj_1.get(["weight"],"list", with_address=False)
weights_address = proj_1.get(["weight"],"list")

inp_spikes = inp.get_data("spikes")
exc_spikes = exc.get_data("spikes")
inh_spikes = inh.get_data("spikes")

sim.end()
