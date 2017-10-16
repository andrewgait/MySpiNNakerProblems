import numpy as np
import time
from matplotlib import cm
import spynnaker7.pyNN as sim
import pyNN
#import Population_Utils as PU
import matplotlib.pyplot as plt
#import spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot as push_bot
#import spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.push_bot_spinnaker_link as push_botSL
#import spynnaker_external_devices_plugin.pyNN.protocols as protocols
#from spynnaker_external_devices_plugin.pyNN import protocols
# import spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot.push_bot_spinnaker_link.push_bot_lif_spinnaker_link as pblif
import spynnaker_external_devices_plugin.pyNN.external_devices_models.abstract_multicast_controllable_device as amcd
import spynnaker_external_devices_plugin.pyNN.external_devices_models.munich_spinnaker_link_motor_device as munichSpinnLinkMotor
import spynnaker_external_devices_plugin.pyNN as q
from spynnaker_external_devices_plugin.pyNN.protocols.munich_io_spinnaker_link_protocol import MunichIoSpiNNakerLinkProtocol
from spynnaker_external_devices_plugin.pyNN.external_devices_models\
 .push_bot.push_bot_parameters.push_bot_motor import PushBotMotor
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot\
 .push_bot_spinnaker_link.push_bot_spinnaker_link_motor_device import PushBotSpiNNakerLinkMotorDevice
from spynnaker_external_devices_plugin.pyNN.external_devices_models.push_bot\
 .push_bot_control_modules.push_bot_lif_spinnaker_link import PushBotLifSpinnakerLink

timestart = time.time()

clockNeuron_parameters = {
    'cm': 0.2,
    'v_reset': -800,
    'v_rest': -70,
    'v_thresh': -73,
    'tau_m': 180.0,  # sim.RandomDistribution('uniform', (10.0, 15.0)),
    'tau_refrac': 0.10,
    'tau_syn_E': 1.5,  # np.linspace(0.1, 20, hiddenP_size),
    'tau_syn_I': 50.0,
    'i_offset': 0.0
}

readout_parameters = {
    'cm': 0.2,
    'v_reset': -75,
    'v_rest': -65,
    'v_thresh': 5000,
    'tau_m': 15.0,  # sim.RandomDistribution('uniform', (10.0, 15.0)),
    'tau_refrac': 0.1,
    'tau_syn_E': 5.5,  # np.linspace(0.1, 20, hiddenP_size),
    'tau_syn_I': 5.5,
    'i_offset': 0.0
}

#setup
timestep = 1.0
sim.setup(timestep=timestep, min_delay=1.0, max_delay=14.0)

#Populations
clock_populations = [sim.Population(1, sim.IF_curr_exp, clockNeuron_parameters)]
"""
        :param devices:\
            The AbstractMulticastControllableDevice instances to be controlled\
            by the population
"""
# motor_device = sim.Population(6, munichSpinnLinkMotor.MunichMotorDevice, {"spinnaker_link_id": 0}, "motor")
#protocol = protocols.munich_io_spinnaker_link_protocol.MunichIoSpiNNakerLinkProtocol(mode=protocols.munich_io_spinnaker_link_protocol.MunichIoSpiNNakerLinkProtocol.MODES["PUSH_BOT"])
protocol = MunichIoSpiNNakerLinkProtocol(mode=MunichIoSpiNNakerLinkProtocol.MODES.PUSH_BOT)

# 0 for PushBotMotor.MOTOR_0_PERMANENT
# 1 for PushBotMotor.MOTOR_0_LEAKY
# 2 for PushBotMotor.MOTOR_1_PERMANENT
# 3 for PushBotMotor.MOTOR_1_LEAKY
#pb_motor = push_bot.push_bot_motor.PushBotMotor(0) # 0 for PushBotMotor.MOTOR_0_PERMANENT
pb_motor = PushBotMotor(0) # 0 for PushBotMotor.MOTOR_0_PERMANENT
#motor_device = push_botSL.push_bot_spinnaker_link_motor_device.PushBotSpiNNakerLinkMotorDevice(motor=pb_motor, protocol=protocol, spinnaker_link_id=0)
motor_device = PushBotSpiNNakerLinkMotorDevice(motor=pb_motor, protocol=protocol, spinnaker_link_id=0)

#readout_populations = [sim.Population(1, push_botSL.push_bot_lif_spinnaker_link.PushBotLifSpinnakerLink,{'n_neurons':1, 'protocol':protocol, 'devices':[motor_device]})]
readout_populations = [sim.Population(1, PushBotLifSpinnakerLink, {'n_neurons':1, 'protocol':protocol, 'devices':[motor_device]})]

#Projections
connector = sim.OneToOneConnector(weights=100.0)  # weightMatCI2C
pro = sim.Projection(clock_populations[0], readout_populations[0], connector, target="excitatory")

# q.activate_live_output_to(readout_populations[0], push_bot_lif)
# q.activate_live_output_to(readout_populations[0],motor_device) # might not be needed as ExternalDeviceLifControl has parameter creates_edge = True

#set recording
for pop in clock_populations:
    pop.record()
    pop.record_v()
for pop in readout_populations:
    pop.record()
    pop.record_v()

#run
sim_duration = 2000
print "simulating " + str(sim_duration) + "ms network time"
start_time = time.time()
sim.run(sim_duration)
sim_time = time.time() - start_time
print "%f s for simulation" % (sim_time)

timeend = time.time()
print '%f s for setting up and simulating on SpiNNaker' % (timeend - timestart)

'''
#retrieve and plot data
clock_spikes = PU.get_population_spikes_spiNNaker(clock_populations)
readout_spikes = PU.get_population_spikes_spiNNaker(readout_populations)

clock_v = PU.retrieve_voltage_data_spiNNaker(clock_populations)
readout_v = PU.retrieve_voltage_data_spiNNaker(readout_populations)


fig = plt.figure()
ax1 = fig.add_subplot(411)

for idx in range(len(clock_spikes)):
    spikes = clock_spikes[idx]
    y = spikes[:, 0] + idx
    ax1.plot(spikes[:, 1], y, '|', color='blue', mew=2, markersize=1.5)
ax1.set_xlim(0,sim_duration)
ax1.set_title("clock spikes")

ax2 = fig.add_subplot(412, sharex=ax1)
for idx, v in enumerate(clock_v):
    ax2.plot(v[:, 2] + idx * 100)
ax2.set_title("clock neuron voltages")

ax3 = fig.add_subplot(413, sharex=ax1)
for idx in range(len(readout_spikes)):
    spikes = readout_spikes[idx]
    y = spikes[:, 0] + idx
    ax1.plot(spikes[:, 1], y, '|', color='orange', mew=2, markersize=1.5)
ax3.set_xlim(0,sim_duration)
ax3.set_title("readout spikes")

ax4 = fig.add_subplot(414, sharex=ax1)
for idx, v in enumerate(readout_v):
    ax4.plot(v[:, 2] + idx * 100)
ax4.set_title("readout neuron voltages")

ax1.set_xlim(0,sim_duration)
plt.show()
'''

sim.end()