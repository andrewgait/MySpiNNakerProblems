"""
****************************************************************************
********************************* Spikebot *********************************
****************************************************************************
****************** @Program by Thorben Schoepe *******************
****************************************************************************

Reset procedure:
Before every run the hardware has to be reset in the following order:
1. Unplug the mini USB power to the Munich IO board connected to spinnlink 1.
2. Press and hold the spinn-3 reset button
3. Press and hold the FPGA reset button
4. Release the FPGA reset button
5. Connect the mini USB power to the Munich IO board
6. Release the spinn-3 reset button





Motor PWM behaviour:
(channel red is second pin from LEDs on FPGA, channel yellow third pin)

note: The connection from neurons to the motors is very sensitive regarding
the set number of neurons per core. Better do not change the number of IF_curr_exp
neurons from the default.

moving straight output neuron ids: 80, 254 + 80 (328 = 1.285ms)
turn:							   60, 254 + 128 + 60 (1.23 red and 1.73 yellow ms)
turn2:							   128 + 60, 254 + 60 (1.73 red, 1.23 yellow ms)  right turn , turn is caused by 254 + 60





"""

#If the eDVS input doesn't work unplug the USB for the IO board and replug it.
#Afterwards reset the spinnaker board


# moving straight: red cable closer to leds than yellow cable
# neuron ids 86 and 334

#--- Importing  libraries ---#
import spynnaker8 as p
import pylab
import numpy as np
#import serial
import time
import matplotlib.pyplot as plt
import pyNN.utility.plotting as plot
from datetime import datetime

delay_oszi_lateral = 30 # was 40
turn_limit_neuron = 9

path_spikes = path_plots = '.' # /home/nbsroot/Documents/spinnaker_collision_avoidance/data/plots/'

def rasterplot(spiketimes,populations_size, simtime, x_labels, y_labels, path_save, plot_type, bin_size):


	frequency_scaling = 1000/bin_size

	number_subplots = len(spiketimes)
	ax = [[] for _ in range(number_subplots+1)]

	if number_subplots <= 6:
		fig = plt.figure(figsize =(6,number_subplots), dpi=300)
	else:
		fig = plt.figure(figsize =(12,number_subplots/1.5), dpi=300)

	plt.rc("font", size=5)

	for num in range(1, number_subplots+1):
		if number_subplots <= 6:
			ax[num] = fig.add_subplot(number_subplots+1,1, num)
		else:
			ax[num] = fig.add_subplot(number_subplots/2+1, 2, num)
		ax[num].set_ylabel(y_labels[num-1])
		ax[num].set_xlabel(x_labels)
		ax[num].set_xlim([0,simtime])
		if plot_type[num-1] == 'rasterplot':
			ax[num].set_ylim([0,populations_size[num-1]])
			for i in range(len(spiketimes[num-1].segments[0].spiketrains)):
				ax[num].scatter(spiketimes[num-1].segments[0].spiketrains[i], [i]* len(spiketimes[num-1].segments[0].spiketrains[i]), s=0.1, c = 'b')
		elif plot_type[num-1] == 'frequ':
			spikes = []
			for i in range(len(spiketimes[num-1].segments[0].spiketrains)):
				spikes = np.append(spikes, spiketimes[num-1].segments[0].spiketrains[i], np.uint32)
			print(spikes)
			ax[num].hist(spikes, bins = range(0, simtime, bin_size))

	fig.tight_layout()

	fig.savefig(path_save)



## Live Input
######################################################################################################################


def input_live():

	UART_ID=2 # The UART port on IO Board the retina is connected to
	spinnaker_link = 1 # SpiNNaker link ID (IO Board connected to)
	board_address = "192.168.240.253" # IP Address of the SpiNNaker board
	#retina_resolution = p.external_devices.PushBotRetinaResolution.NATIVE_128_X_128
	retina_resolution = p.external_devices.PushBotRetinaResolution.DOWNSAMPLE_64_X_64

  # Set up the PushBot devices
	spinnlink_protocol = p.external_devices.MunichIoSpiNNakerLinkProtocol(
		mode=p.external_devices.MunichIoSpiNNakerLinkProtocol.MODES.RESET_TO_DEFAULT,
		uart_id=UART_ID) #RESET_TO_DEFAULT ensures 4mbps baud rate for eDVS

	retina_device = p.external_devices.PushBotSpiNNakerLinkRetinaDevice(
		spinnaker_link_id=spinnaker_link,
		board_address=board_address,
		protocol=spinnlink_protocol,
		resolution=retina_resolution)

	return retina_device

input_dvs = 'live'


# define input

if input_dvs == 'live':
	retina_device = input_live()


#--- simulation setup ---#
p.setup(timestep=1.0, min_delay=1.0, max_delay=144., time_scale_factor=1)
p.set_number_of_neurons_per_core(p.extra_models.IF_curr_exp_sEMD, 128)  # was 100 for SpiNN3
p.set_number_of_neurons_per_core(p.IF_curr_exp, 256)  # was 100 SpiNN3
#p.set_number_of_neurons_per_core(p.SpikeSourceArray, 100)


############################# important parameters

#-- Config parameters --#
t               =   10000                 #time of simulation in ms


class Weights:
	sptc = 100# was 10
	semd = 5 # was 5

# id of turning and forward movement neuron
turn = 128
correction_factor = 0
correction_factor_2 = 0





class CellParams:
	#--- Neuron type parameters ---#
	lif = {'cm': 0.25,
					   'i_offset': 0.0,
					   'tau_m': 20.0,
					   'tau_refrac': 2.0,
					   'tau_syn_E': 5.0,
					   'tau_syn_I': 5.0,
					   'v_reset': -68.0,
					   'v_rest': -65.0,
					   'v_thresh': -50.0
					   }

	oszilator = {'cm': 0.25,
					   'i_offset': 0.0,
					   'tau_m': 20.0,
					   'tau_refrac': 2.0,
					   'tau_syn_E': 5.0,
					   'tau_syn_I': 5.0,
					   'v_reset': -68.0,
					   'v_rest': -65.0,
					   'v_thresh': -50.0
					   }

	wta = {'cm': 0.25,
					   'i_offset': 0.0,
					   'tau_m': 20.0,
					   'tau_refrac': 1.0,
					   'tau_syn_E': 5.0,
					   'tau_syn_I': 80.0, # was 50
					   'v_reset': -68.0,
					   'v_rest': -65.0,
					   'v_thresh': -50.0
					   }

	other = {'cm': 0.25,
					   'i_offset': 0.0,
					   'tau_m': 20.0,
					   'tau_refrac': 2.0,
					   'tau_syn_E': 5.0,
					   'tau_syn_I': 5.0,
					   'v_reset': -68.0,
					   'v_rest': -65.0,
					   'v_thresh': -50.0
					   }

	inhibition = {'cm': 0.25,
					   'i_offset': 0.0,
					   'tau_m': 20.0,
					   'tau_refrac': 2.0,
					   'tau_syn_E': 5.0,
					   'tau_syn_I': 10.0,
					   'v_reset': -68.0,
					   'v_rest': -65.0,
					   'v_thresh': -50.0
					   }

	global_inhib = {'cm': 0.25,
					   'i_offset': 0.0,
					   'tau_m': 30.0,
					   'tau_refrac': 2.0,
					   'tau_syn_E': 40.0, # was 25
					   'tau_syn_I': 5.0,
					   'v_reset': -68.0,
					   'v_rest': -65.0,
					   'v_thresh': -50.0
					   }

		 # spiking elementary motion detector
	sEMD =  {'cm'        : 0.25,
		   'i_offset'  : 0.0,
		   'tau_m'     : 30.0,     # was 50
		   'tau_syn_E' : 300,    # was 300
		   'tau_syn_I' : 50,    # was 100
		   'v_reset'   : -70.0,
		   'v_rest'    : -65.0,
		   'v_thresh'  : -40.0,
		   'tau_refrac' :  1
		   }

		 # spatiotemporal cuboid cells
	SPTC = {'cm'        : 0.25,
			 'i_offset'  : 0.0,
			 'tau_m'     : 35,
			 'tau_syn_E' : 10 , # was 0.2
			 'tau_syn_I' : 1 ,
			 'v_reset'   : -70.0,
			 'v_rest'    : -65.0,
			 'v_thresh'  : -40.0,
			 'tau_refrac' :  1
			 }


		  # integrator neurons

	integrator = {'cm'        : 0.25,
			 'i_offset'  : 0.0,
			 'tau_m'     : 20,
			 'tau_syn_E' : 5 ,
			 'tau_syn_I' : 5 ,
			 'v_reset'   : -70.0,
			 'v_rest'    : -65.0,
			 'v_thresh'  : -40.0,
			 'tau_refrac' :  1
			 }

def create_projections(n, w, d):
	projections = list()
	for i in range(n):
		singleConnection = ((i, i, w, d))
		projections.append(singleConnection)
	return projections


class Size:

    oszillator_pop = 96
    output = 512
    wta = 64
    #retina_edge = 128
    #retina = 128**2*2
    #retina_connections = 128*40
    retina_edge = 64
    retina = 64**2*2
    retina_connections = 64*20
    sptc_connections = 64**2
    sptc_real = 64*20
    semd = 64*20
    sptc_edge_horizontal = 64
    sptc_edge_vertical = 20
    semd_edge_vertical = 20
    semd_edge_horizontal = 64





scaling_wta_2_oszi = int(((Size.oszillator_pop-32)*2)/Size.wta)

class Populations:

    # motor oszillator
	fpga = p.Population(size=512, cellclass=p.external_devices.ExternalCochleaDevice(spinnaker_link_id=0, board_address=None, cochlea_key=0x200, cochlea_n_channels=p.external_devices.ExternalCochleaDevice.CHANNELS_128, cochlea_type=p.external_devices.ExternalCochleaDevice.TYPE_STEREO, cochlea_polarity=p.external_devices.ExternalCochleaDevice.POLARITY_MERGED), label="ExternalCochlea")



	output = p.Population(Size.output, p.IF_curr_exp, CellParams.lif, label='outputlayer')
	oszillator_1 = p.Population(Size.oszillator_pop, p.IF_curr_exp, CellParams.oszilator, label='oszillator_1')
	oszillator_2 = p.Population(Size.oszillator_pop, p.IF_curr_exp, CellParams.oszilator, label='oszillator_2')

	# vision
	# SPTC population
	retina = p.Population(Size.retina, retina_device, label='retina_pop')
	sptc = p.Population(Size.sptc_real,p.IF_curr_exp,CellParams.SPTC,label='SPTC')
	# sEMD populations
	semd_rl = p.Population(Size.semd,p.extra_models.IF_curr_exp_sEMD,CellParams.sEMD,label='sEMD_pop_right_left')
	semd_lr = p.Population(Size.semd,p.extra_models.IF_curr_exp_sEMD,CellParams.sEMD,label='sEMD_pop_left_right')
	# Integrator neurons
	integrator_lr = p.Population(Size.semd_edge_horizontal,p.IF_curr_exp,CellParams.integrator,label='int_left_right')
	integrator_rl = p.Population(Size.semd_edge_horizontal,p.IF_curr_exp,CellParams.integrator,label='int_right_left')
	poisson = p.Population(Size.wta, p.SpikeSourcePoisson, {'rate':100}, label = "poisson") # rate was 20
	poisson2 = p.Population(1, p.SpikeSourcePoisson, {'rate':100, 'start':10, 'duration':t - 10}, label = "poisson2")
	inhibition = p.Population(1, p.IF_curr_exp, CellParams.inhibition, label='inhibition')
	bias = p.Population(Size.wta, p.IF_curr_exp, CellParams.other, label='bias')
	wta = p.Population(Size.wta, p.IF_curr_exp, CellParams.wta, label='wta')
	global_inhib = p.Population(1,p.IF_curr_exp,CellParams.global_inhib,label='inhibitor_pop_horizontal')
	extreme_turn = p.Population(1, p.IF_curr_exp, CellParams.wta, label='extreme_turn')
	efference_copy = p.Population(1, p.IF_curr_exp, CellParams.wta, label='afferent')

scaling_factor = Size.retina_edge/Size.sptc_edge_horizontal
#SPTC_connection = np.arange(Size.sptc_connections, dtype=np.uint32)
#SPTC_connection.resize(Size.sptc_edge_horizontal,Size.sptc_edge_horizontal)
#SPTC_connection = np.kron(SPTC_connection, np.ones((int(scaling_factor), int(scaling_factor))))
#SPTC_connection.resize(int(Size.retina/2))

class Matrix:
	semd_y_lr = [[Size.semd_edge_horizontal-1 +1 - i % Size.semd_edge_horizontal] for i in range(Size.semd)]
	semd_y_rl = [[Size.semd_edge_horizontal-1 - i % Size.semd_edge_horizontal] for i in range(Size.semd)]

retina = range(Size.retina)
# connectors
class Connections:
	oszillator_lateral = [([i, i+1, 2, delay_oszi_lateral])for i in range(Size.oszillator_pop-1)]


	# turn connections
	#oszillator_to_output_1 = [[i, 254+turn, 10, 1] for i in range(0,Size.oszillator_pop,8)] #
	#oszillator_to_output_2 = [[i,128+turn,10,1] for i in range(0,Size.oszillator_pop,8)]
	#oszillator_to_output_3 =[[i,254+turn,10,1] for i in range(4,Size.oszillator_pop,8) ]
	#oszillator_to_output_4 =[[i,128+turn,10,1] for i in range(4,Size.oszillator_pop,8) ]

	#oszillator2_to_output_1 = [[i,turn, 10, 1] for i in range(0,Size.oszillator_pop,8)]
	#oszillator2_to_output_2 = [[i,254+128+turn,10,1] for i in range(0,Size.oszillator_pop,8)]
	#oszillator2_to_output_3 =[[i,turn,10,1] for i in range(4,Size.oszillator_pop,8) ]
	#oszillator2_to_output_4 =[[i,254+128+turn,10,1] for i in range(4,Size.oszillator_pop,8) ]

	oszillator_to_output_1 = [[i, 254+turn+correction_factor, 10, 1] for i in range(0,Size.oszillator_pop,8)] #
	oszillator_to_output_2 = [[i,turn+correction_factor_2,10,1] for i in range(0,Size.oszillator_pop,8)]
	oszillator_to_output_3 =[[i,254+turn+correction_factor,10,1] for i in range(4,Size.oszillator_pop,8) ]
	oszillator_to_output_4 =[[i,turn+correction_factor_2,10,1] for i in range(4,Size.oszillator_pop,8) ]

	oszillator2_to_output_1 = [[i,turn+correction_factor_2, 10, 1] for i in range(0,Size.oszillator_pop,8)]
	oszillator2_to_output_2 = [[i,254+turn+correction_factor,10,1] for i in range(0,Size.oszillator_pop,8)]
	oszillator2_to_output_3 =[[i,turn+correction_factor_2,10,1] for i in range(4,Size.oszillator_pop,8) ]
	oszillator2_to_output_4 =[[i,254+turn+correction_factor,10,1] for i in range(4,Size.oszillator_pop,8) ]

	oszillator_to_output_1 = oszillator_to_output_1 + oszillator_to_output_2 + oszillator_to_output_3 + oszillator_to_output_4
	oszillator2_to_output_1 = oszillator2_to_output_1 + oszillator2_to_output_2 + oszillator2_to_output_3 + oszillator2_to_output_4



	wta_2_oszi1 = [[i,i*scaling_wta_2_oszi+32,10,1] for i in range(turn_limit_neuron,int(Size.wta/2),1)]
	wta_2_oszi2 = [[Size.wta-i,i*scaling_wta_2_oszi+32,10,1] for i in range(turn_limit_neuron, int(Size.wta/2),1)]



	wta_2_oszi1_max = [[i,turn_limit_neuron*scaling_wta_2_oszi+32,10,1] for i in range(turn_limit_neuron)]
	wta_2_oszi2_max = [[Size.wta-i,turn_limit_neuron*scaling_wta_2_oszi+32,10,1] for i in range(turn_limit_neuron)]



	oszi_2_wta = [[Size.oszillator_pop-1,i,30,100] for i in range(Size.wta)] # delay was 100



	#sptc_on = [(int(retina[i]+44*128),int(SPTC_connection[i]),Weights.sptc,1) for i in range(Size.retina_connections)]


	  # SPTC to sEMD_pop connections

	semd_rl_trig  = [(i, i, Weights.semd, 1) for i in range(0,Size.semd)]
	semd_rl_fac  =[(i+1, i, Weights.semd, 1) for i in range(0,Size.semd)]
	semd_lr_trig = [(i+1,i, Weights.semd, 1) for i in range(0,Size.semd)]
	semd_lr_fac = [(i, i, Weights.semd, 1) for i in range(0,Size.semd)]

	# sEMD to Integrator connections

	integrator_rl = [(i,Matrix.semd_y_rl[i][0],1,1) for i in range(Size.semd)]
	integrator_lr = [(i,Matrix.semd_y_lr[i][0],1,1) for i in range(Size.semd)]

	# Integrator to WTA connections

	wta_lateral = [(i,i+1,0.75,1) for i in range(Size.semd_edge_horizontal-1)] + \
	[(i+1,i,0.75,1) for i in range(Size.semd_edge_horizontal-1)] # weights were 1.5
	wta_lateral_2 = [(i,i+2,0.5,1) for i in range(Size.semd_edge_horizontal-2)] + \
	[(i+2,i,0.5,1) for i in range(Size.semd_edge_horizontal-2)] # weights were 1
	wta_lateral_3 = [(i,i+3,0.3,1) for i in range(Size.semd_edge_horizontal-3)] + \
	[(i+3,i,0.3,1) for i in range(Size.semd_edge_horizontal-3)] # weights were 0.75
	wta = [(i,i,1,1) for i in range(Size.semd_edge_horizontal)] # weight was 2.5


# retina to sptc
#p.Projection(Populations.retina, Populations.sptc, p.FromListConnector(Connections.sptc_on),p.StaticSynapse(),receptor_type='excitatory')
#p.Projection(Populations.retina, Populations.sptc, p.OneToOneConnector(), p.StaticSynapse(weight=Weights.sptc,delay=1), receptor_type='excitatory')

# SPTC to sEMD
p.Projection(Populations.sptc, Populations.semd_rl, p.FromListConnector(Connections.semd_rl_fac),p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.sptc, Populations.semd_rl, p.FromListConnector(Connections.semd_rl_trig),p.StaticSynapse(), receptor_type='excitatory2') # was 2

p.Projection(Populations.sptc, Populations.semd_lr, p.FromListConnector(Connections.semd_lr_fac),p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.sptc, Populations.semd_lr, p.FromListConnector(Connections.semd_lr_trig),p.StaticSynapse(), receptor_type='excitatory2') # was 2


# sEMD to Integrator
p.Projection(Populations.semd_lr, Populations.integrator_lr , p.FromListConnector(Connections.integrator_lr),p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.semd_rl, Populations.integrator_rl , p.FromListConnector(Connections.integrator_rl),p.StaticSynapse(), receptor_type='excitatory')

# Integrator to WTA
p.Projection(Populations.integrator_lr,Populations.wta,p.FromListConnector(Connections.wta),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_rl,Populations.wta,p.FromListConnector(Connections.wta),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_lr,Populations.wta,p.FromListConnector(Connections.wta_lateral),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_rl,Populations.wta,p.FromListConnector(Connections.wta_lateral),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_lr,Populations.wta,p.FromListConnector(Connections.wta_lateral_2),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_rl,Populations.wta,p.FromListConnector(Connections.wta_lateral_2),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_lr,Populations.wta,p.FromListConnector(Connections.wta_lateral_3),p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.integrator_rl,Populations.wta,p.FromListConnector(Connections.wta_lateral_3),p.StaticSynapse(), receptor_type='inhibitory')

# wta to globale inhib
p.Projection(Populations.wta, Populations.global_inhib, p.AllToAllConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='excitatory')
p.Projection(Populations.global_inhib, Populations.wta, p.AllToAllConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='inhibitory')


# wta to oszillator
p.Projection(Populations.wta, Populations.oszillator_1, p.FromListConnector(Connections.wta_2_oszi1), p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.wta, Populations.oszillator_1, p.FromListConnector(Connections.wta_2_oszi1_max), p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.wta, Populations.oszillator_2, p.FromListConnector(Connections.wta_2_oszi2), p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.wta, Populations.oszillator_2, p.FromListConnector(Connections.wta_2_oszi2_max), p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.poisson, Populations.wta,  p.FromListConnector([[i,i,2,1] for i in range(3,Size.semd_edge_horizontal-3, 1)]), p.StaticSynapse(), receptor_type='excitatory')

# extreme turn
p.Projection(Populations.poisson, Populations.extreme_turn, p.OneToOneConnector(), p.StaticSynapse(weight=0.6,delay=1), receptor_type='excitatory')
p.Projection(Populations.extreme_turn, Populations.global_inhib, p.AllToAllConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='excitatory')
p.Projection(Populations.global_inhib, Populations.extreme_turn, p.AllToAllConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='inhibitory')
p.Projection(Populations.extreme_turn, Populations.oszillator_1, p.FromListConnector([[0,20,10,1]]), p.StaticSynapse(), receptor_type='excitatory')



# oszillator to wta
p.Projection(Populations.oszillator_1, Populations.wta, p.AllToAllConnector(), p.StaticSynapse(weight=30,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_2, Populations.wta, p.AllToAllConnector(), p.StaticSynapse(weight=30,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_1, Populations.extreme_turn, p.AllToAllConnector(), p.StaticSynapse(weight=30,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_2, Populations.extreme_turn, p.AllToAllConnector(), p.StaticSynapse(weight=30,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_2, Populations.wta, p.FromListConnector(Connections.oszi_2_wta), p.StaticSynapse(), receptor_type='inhibitory')
p.Projection(Populations.oszillator_1, Populations.wta, p.FromListConnector(Connections.oszi_2_wta), p.StaticSynapse(), receptor_type='inhibitory')


# oszillator to oszillator inhibiting each other
p.Projection(Populations.oszillator_1, Populations.oszillator_2, p.AllToAllConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_2, Populations.oszillator_1, p.AllToAllConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='inhibitory')

# oszillator lateral connections
p.Projection(Populations.oszillator_1, Populations.oszillator_1, p.FromListConnector(Connections.oszillator_lateral), p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.oszillator_1, Populations.oszillator_1, p.OneToOneConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_2, Populations.oszillator_2, p.FromListConnector(Connections.oszillator_lateral), p.StaticSynapse(), receptor_type='excitatory')
p.Projection(Populations.oszillator_2, Populations.oszillator_2, p.OneToOneConnector(), p.StaticSynapse(weight=10,delay=1), receptor_type='inhibitory')




#### oszillator to output
# turning
#p.Projection(Populations.oszillator_1, Populations.output, p.FromListConnector( Connections.oszillator_to_output_1), p.StaticSynapse(), receptor_type='excitatory')
#p.Projection(Populations.oszillator_2, Populations.output, p.FromListConnector( Connections.oszillator2_to_output_1), p.StaticSynapse(), receptor_type='excitatory')
# moving straight
p.Projection(Populations.oszillator_1, Populations.output, p.FromListConnector([[Size.oszillator_pop-1,254+turn+correction_factor,10,1], [Size.oszillator_pop-1,turn+correction_factor_2,10,1]]), p.StaticSynapse(), receptor_type='excitatory')# was +80 and 80
p.Projection(Populations.oszillator_2, Populations.output, p.FromListConnector([[Size.oszillator_pop-1,254+turn+correction_factor,10,1], [Size.oszillator_pop-1,turn+correction_factor_2,10,1]]), p.StaticSynapse(), receptor_type='excitatory')# was +80 and 80




# oszillator to sptc
p.Projection(Populations.oszillator_1, Populations.sptc, p.AllToAllConnector(), p.StaticSynapse(weight=30,delay=1), receptor_type='inhibitory')
p.Projection(Populations.oszillator_2, Populations.sptc, p.AllToAllConnector(), p.StaticSynapse(weight=30,delay=1), receptor_type='inhibitory')



# output from SpiNNaker to FPGA
p.external_devices.activate_live_output_to(Populations.output, Populations.fpga)




Populations.oszillator_1.record(["spikes"])
Populations.oszillator_2.record(["spikes"])
Populations.output.record(["spikes"])
Populations.wta.record(["spikes"])
Populations.inhibition.record(["spikes"])
Populations.bias.record(["spikes"])
Populations.integrator_lr.record(["spikes"])
Populations.integrator_rl.record(["spikes"])
Populations.sptc.record(["spikes"])





#---runing simulation ---#
p.run(t)

class Spikes:

	oszillator1=Populations.oszillator_1.get_data(variables=["spikes"]) # left
	oszillator2=Populations.oszillator_2.get_data(variables=["spikes"]) # right
	wta=Populations.wta.get_data(variables=["spikes"])
	output=Populations.output.get_data(variables=["spikes"])
	inhibition=Populations.inhibition.get_data(variables=["spikes"])
	bias=Populations.bias.get_data(variables=["spikes"])
	integrator_lr=Populations.integrator_lr.get_data(variables=["spikes"])
	integrator_rl=Populations.integrator_rl.get_data(variables=["spikes"])
	sptc=Populations.sptc.get_data(variables=["spikes"])


time_now = datetime.now().strftime('%Y-%m-%d-%H%M')


spikedata = [ Spikes.wta, Spikes.oszillator1, Spikes.oszillator2, Spikes.sptc, Spikes.integrator_lr, Spikes.integrator_rl, Spikes.output]
size_populations = [Size.wta, Size.oszillator_pop,  Size.oszillator_pop, Size.sptc_real, Size.semd_edge_horizontal, Size.semd_edge_horizontal, Size.output]
y_labels = ['wta, low:l, high:r', 'Oszi left', 'Oszi right','sptc lr', 'int lr', 'int rl', 'out']
plot_type = ['rasterplot','rasterplot', 'rasterplot','rasterplot', 'rasterplot', 'rasterplot', 'rasterplot']
path = path_spikes + time_now + 'experiment1_rasterplot.png'
rasterplot(spikedata,size_populations, t,'time (ms)', y_labels, path, plot_type, bin_size = 100)


np.save(path_spikes + time_now + 'experiment1_spikes.npy',Spikes.integrator_lr.segments[0].spiketrains + Spikes.integrator_rl.segments[0].spiketrains + \
Spikes.oszillator1.segments[0].spiketrains + Spikes.oszillator2.segments[0].spiketrains + Spikes.output.segments[0].spiketrains + \
Spikes.wta.segments[0].spiketrains)


#--- Finish simulation ---#
p.end()

# low number = left turn


