#import pyNN.spiNNaker as p
import spynnaker8 as p
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt

import csv
import sys
import numpy
import datetime
from setuptools import run_2to3_on_doctests

# parameters
datum = datetime.datetime.now()

step = 0.1
p.setup(timestep = step)
n_neurons = 1
run_time = 150
cm = 0.25
i_offset = 0.0
tau_m = 20.0
tau_refrac = 1.0
current_decay = tau_syn_E = tau_syn_I = 30
v_reset = -85.0
v_rest = -65.0
v_thresh = -50.0

weight= 1
delay1 = 0.1
delay2 = 2.0
																								# default parameters
cell_params_lif = {'cm'        : cm, 															# 1.0
                   'i_offset'  : i_offset,														# 0
                   'tau_m'     : tau_m,															# 20.0
                   'tau_refrac': tau_refrac,													# 0.1
                   'tau_syn_E' : current_decay , # speed of synaptic current decay excitatory	# 5.0
                   'tau_syn_I' : current_decay , # speed of synaptic current decay inhibitory	# 5.0
                   'v_reset'   : v_reset,														# -65.0
                   'v_rest'    : v_rest,														# -65.0
                   'v_thresh'  : v_thresh														# -50.0
                   }

# neuron populations
# cellparams let's you change parameters of the neuron
sEMD = p.Population(1, p.IF_curr_exp_sEMD(**cell_params_lif), label = "sEMD")

spikeArray = {'spike_times': [[0]]}
input_first = p.Population(1, p.SpikeSourceArray(**spikeArray),
						label = "input_first")
input_second = p.Population(1, p.SpikeSourceArray(**spikeArray),
						label = "input_second")

p.Projection(input_first,sEMD, p.OneToOneConnector(),
			receptor_type='excitatory',
			synapse_type=p.StaticSynapse(weight=weight,delay=delay1))
p.Projection(input_second,sEMD, p.OneToOneConnector(),
			receptor_type = 'inhibitory',
			synapse_type=p.StaticSynapse(weight=weight, delay=delay2))

# record
sEMD.record(['v','gsyn_exc','gsyn_inh','spikes'])

# run
p.run(run_time)

# get data
spikes = sEMD.get_data('spikes') # read spikes
v = sEMD.get_data('v') # read membrane voltage
exc_current = sEMD.get_data('gsyn_exc')
inh_current = sEMD.get_data('gsyn_inh')

print datum

# plots
# Note that the plot of inh_current is the negative of that in the pynn0.7
# version of this script
Figure(
	# membrane potential of the sEMD neuron
	Panel(v.segments[0].filter(name='v')[0],
		  ylabel="Membrane potential (mV)",
		  data_labels=[sEMD.label], yticks=True, xlim=(0, run_time)),
    # raster plot of the sEMD neuron spike times
    Panel(spikes.segments[0].spiketrains,
          yticks=True, markersize=5, xlim=(0, run_time)),
    Panel(exc_current.segments[0].filter(name='gsyn_exc')[0],
          ylabel="exc current",
          data_labels=[sEMD.label], yticks=True, xlim=(0, run_time)),
	Panel(inh_current.segments[0].filter(name='gsyn_inh')[0],
          xlabel="Time (ms)", xticks=True,
          ylabel="inh current",
          data_labels=[sEMD.label], yticks=True, xlim=(0, run_time)),
    title="sEMD example, PyNN0.8",
    annotations="Simulated with {}".format(p.name()+
										", with tau_syn: "+str(current_decay)+
										", weights: "+str(weight)+
										", delay1: "+str(delay1)+
										", delay2: "+str(delay2))
)
plt.show()

# export to csv files
output_values = [v.segments[0].filter(name='v')[0],
				exc_current.segments[0].filter(name='gsyn_exc')[0],
				inh_current.segments[0].filter(name='gsyn_inh')[0],
				spikes.segments[0].spiketrains]
testvalue = [cm, i_offset, tau_m, tau_refrac,
			current_decay, v_reset, v_rest, v_thresh]

csvfile = "output.csv"
csvfile_parameter = "output_parameter.csv"

with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in output_values:
        writer.writerow(val)

with open(csvfile_parameter, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in testvalue:
        writer.writerow([val])

# end
p.end()
