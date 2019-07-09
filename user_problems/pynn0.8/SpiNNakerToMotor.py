#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed 3 Jul 2019
"""

import pyNN.spiNNaker as p
from spynnaker8.utilities import DataHolder
from pacman.model.graphs.application import ApplicationSpiNNakerLinkVertex
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt


class MyMotor(ApplicationSpiNNakerLinkVertex):
    def __init__(n_neurons, spinnaker_link_id, board_address=None, label=None):
        ApplicationSpiNNakerLinkVertex(
            n_neurons,spinnaker_link_id=spinnaker_link_id,
            board_address=board_address, label=label)

class MyMotorDataHolder(DataHolder):
    def __init__(
            self, spinnaker_link_id,
            board_address=None,
            label=None):

        DataHolder.__init__(
            self, {
                'spinnaker_link_id': spinnaker_link_id,
                'board_address': board_address, 'label': label})
    
    @staticmethod
    def build_model():
        return MyMotor
    
# set up the tools
tstop = 1000
p.setup(timestep=1.0, min_delay=1.0, max_delay=32.0)


input_population = p.Population(1, p.SpikeSourceArray(spike_times=[20]))
control_population = p.Population(1, p.IF_curr_exp())

motor_device = p.Population(1, MyMotor(spinnaker_link_id=1))

p.Projection(
    input_population, control_population, p.OneToOneConnector(),
    synapse_type=p.StaticSynapse(weight=5, delay=2))

p.external_devices.activate_live_output_to(control_population, motor_device)


# === Setup recording ===
input_population.record("spikes")
control_population.record("spikes")


p.run(tstop)


# === Print results to file ===
input_spikes = input_population.get_data("spikes")
control_spikes = control_population.get_data("spikes")

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(input_spikes.segments[0].spiketrains, xlabel="Time/ms", xticks=True,
          yticks=True, markersize=2, xlim=(0, tstop)),
    title="INPUT: spikes",
    annotations="Simulated with {}".format(p.name())
)
plt.show()

Figure(
    # raster plot of the presynaptic neuron spike times
    Panel(control_spikes.segments[0].spiketrains, xlabel="Time/ms", xticks=True,
          yticks=True, markersize=2, xlim=(0, tstop)),
    title="CONTROL: spikes",
    annotations="Simulated with {}".format(p.name())
)
    
plt.show()
p.end()