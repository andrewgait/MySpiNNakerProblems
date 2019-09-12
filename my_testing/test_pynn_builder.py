
# coding: utf-8
#!python

import numpy
import pyNN.spiNNaker as sim

sim.setup()

pop_6 = sim.Population(100, sim.SpikeSourcePoisson(rate=100, start=0, duration=10000000000))
pop_6.record('spikes')
pop_7 = sim.Population(100, sim.IF_curr_exp(v_rest=-65, cm=1, tau_m=20, tau_refrac=0, tau_syn_E=5, tau_syn_I=5, i_offset=0, v_reset=-65, v_thresh=-50 ), label='IFCurrExp')
pop_7.initialize(v=-65)
pop_7.record('spikes')
pop_7.record('v')
prj_8 = sim.Projection(pop_7, pop_7, sim.OneToOneConnector(),sim.StaticSynapse(weight=5, delay=3), receptor_type='excitatory')
prj_9 = sim.Projection(pop_6, pop_7, sim.OneToOneConnector(),sim.StaticSynapse(weight=5, delay=3), receptor_type='excitatory')


sim.run(1000)

pop_6.write_data("testing_pop_6.pkl")
pop_7.write_data("testing_pop_7.pkl")


sim.end()
