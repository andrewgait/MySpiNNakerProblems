import spynnaker8 as sim
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import random
import pickle
from pyNN.standardmodels import electrodes
from pyNN.utility.plotting import Figure,Panel
from pyNN.random import NumpyRNG,RandomDistribution
from pyNN.utility import get_simulator,init_logging,normalized_filename


np.random.seed(seed=1)


'''
# Sweep Signal

fs=5000.0
ts=1./fs


total_time=10.0

samples=np.linspace(0,total_time,int(fs*total_time),endpoint=False)

f_start=1.0/total_time
f_stop=50.0/total_time

f_sweep=np.linspace(f_start,f_stop,num=len(samples))

sinus_f_sweep=np.sin(2*np.pi*f_sweep*samples)

t_sweep=np.arange(0,(len(samples)*ts),ts)

'''


def dvs(signal):
    on_spikes_p=[]
    off_spikes_p=[]
    for i in range(0,100):
        on_spikes=[]
        off_spikes=[]
        th=0.25+np.random.uniform(0.0,0.5,size=1)
        a=signal[0]
        for j in range(1,len(signal)):
            if signal[j]>=a+th:
               on_spikes.append(j)
               a=signal[j]
            if signal[j]<=a-th:
               off_spikes.append(j)
               a=signal[j]
        on_spikes_p.append(on_spikes)
        off_spikes_p.append(off_spikes)
    return on_spikes_p,off_spikes_p


def plot_spiketrains(segment):
    for spiketrain in segment.spiketrains:
        y = np.ones_like(spiketrain) * spiketrain.annotations['source_id']
        plt.plot(spiketrain, y, '.', ms=0.1, c='k')



# Sine wave of different frequencies
t=10.0
SNR=2.0
fs=5000.0
ts=1./fs

samples=np.linspace(0,t,int(fs*t),endpoint=False)


f=1.0


wave=np.sin(2*np.pi*f*samples)

'''
#noise=[]

#for i in range(0,len(wave)):
 #   random.seed(i)
#    noise.append(random.gauss(0,1))
'''

noise=np.random.randn(len(wave))

sig_v=np.var(wave)

n_v=np.var(noise)

k=sig_v/(n_v*10**(SNR/10))

new_n=np.sqrt(k)*noise




#new_n=[]

#for i in range(0,len(noise)):
#    new_n.append(np.sqrt(k)*noise[i])



noisy_wave=wave+new_n


t_wave=np.arange(0,(len(wave)*ts),ts)

'''

plt.figure()

plt.plot(t_wave,noisy_wave)

plt.xlabel('Time (s)')

plt.ylabel('Amplitude (V)')

plt.show()


'''

# Apply DVS


on_s,off_s=dvs(noisy_wave)



fs=5000.0
ts=1./fs


on_s_t=[]
off_s_t=[]




for i in range(0,len(on_s)):
    on_s_t.append(np.array(on_s[i])*ts*1000.0)                # ON spike times

for i in range(0,len(off_s)):
    off_s_t.append(np.array(off_s[i])*ts*1000.0)              # OFF spike times


on_s_t_ex=on_s_t[0:50]
on_s_t_in=on_s_t[50:100]

off_s_t_ex=off_s_t[0:50]
off_s_t_in=off_s_t[50:100]



simtime=10000.0

izk=sim.Izhikevich



# Sim setup

dt=0.2
delay_ex=1.0
delay_in=2.0
extra={}



# sim.setup(timestep=dt,min_delay=delay_ex,max_delay=delay_in,**extra)
sim.setup(timestep=dt)
sim.set_number_of_neurons_per_core(izk,20)
sim.set_number_of_neurons_per_core(sim.SpikeSourceArray,20)
rng=NumpyRNG(seed=1,parallel_safe=True)

#c_source=electrodes.ACSource(start=0.0,stop=10000.0,amplitude=1.0,offset=0.0,frequency=4,phase=0.0)
# Neuron parameters for different types of dynamics (Izhikevich (2003))
neuron_params_RS={'a':0.1,'b':0.2,'c':-65.0,'d':1.0,'i_offset':5.0}            # Regular Spiking
neuron_params_IB={'a':0.02,'b':0.2,'c':-55.0,'d':4.0,'i_offset':0.0}            # Intrinsically Bursting
neuron_params_CH={'a':0.02,'b':0.2,'c':-50.0,'d':2.0,'i_offset':0.0}            # Chattering
neuron_params_FS={'a':0.1,'b':0.2,'c':-65.0,'d':2.0,'i_offset':5.0}             # Fast spiking
neuron_params_LTS={'a':0.02,'b':0.25,'c':-65.0,'d':2.0,'i_offset':0.0}          # Low threshold spiking
neuron_params_TC={'a':0.02,'b':0.25,'c':-65.0,'d':0.05,'i_offset':0.0}          # Thalamocortical
neuron_params_RZ={'a':0.1,'b':0.26,'c':-65.0,'d':2.0,'i_offset':0.0}  # Resonator


print('on ex: ', len(on_s_t_ex), on_s_t_ex)
print('on in: ', len(on_s_t_in), on_s_t_in)
print('off ex: ', len(off_s_t_ex), off_s_t_ex)
print('off in: ', len(off_s_t_in), off_s_t_in)

on_input_ex=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in on_s_t_ex]))

on_input_in=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in on_s_t_in]))

off_input_ex=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in off_s_t_ex]))

off_input_in=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in off_s_t_in]))



neuron_ex=sim.Population(80,izk(**neuron_params_RS))

neuron_in=sim.Population(20,izk(**neuron_params_FS))

#expoisson=sim.Population(1,sim.SpikeSourcePoisson(rate=2500.0))
#inpoisson=sim.Population(1,sim.SpikeSourcePoisson(rate=2500.0))

# Building Network


n_exex=sim.Projection(neuron_ex,neuron_ex,sim.FixedProbabilityConnector(0.1,rng=rng),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')
n_exin=sim.Projection(neuron_ex,neuron_in,sim.FixedProbabilityConnector(0.1,rng=rng),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')


n_inex=sim.Projection(neuron_in,neuron_ex,sim.FixedProbabilityConnector(0.1,rng=rng),synapse_type=sim.StaticSynapse(weight=-(5*0.15),delay=delay_in),receptor_type='inhibitory')
n_inin=sim.Projection(neuron_in,neuron_in,sim.FixedProbabilityConnector(0.1,rng=rng),synapse_type=sim.StaticSynapse(weight=-(5*0.15),delay=delay_in),receptor_type='inhibitory')



# Connecting inputs

on_path_exex=sim.Projection(on_input_ex,neuron_ex,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')
on_path_inex=sim.Projection(on_input_in,neuron_ex,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=-(5*0.15),delay=delay_in),receptor_type='inhibitory')

off_path_exex=sim.Projection(off_input_ex,neuron_ex,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')
off_path_inex=sim.Projection(off_input_in,neuron_ex,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=-(5*0.15),delay=delay_in),receptor_type='inhibitory')



on_path_exin=sim.Projection(on_input_ex,neuron_in,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')
on_path_inin=sim.Projection(on_input_in,neuron_in,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=-(5*0.15),delay=delay_in),receptor_type='inhibitory')


off_path_exin=sim.Projection(off_input_ex,neuron_in,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')
off_path_inin=sim.Projection(off_input_in,neuron_in,sim.FixedProbabilityConnector(0.5,rng=rng),synapse_type=sim.StaticSynapse(weight=-(5*0.15),delay=delay_in),receptor_type='inhibitory')



#p_ex=sim.Projection(expoisson,neuron_ex,sim.FixedProbabilityConnector(1.0),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')

#p_in=sim.Projection(inpoisson,neuron_in,sim.FixedProbabilityConnector(1.0),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay_ex),receptor_type='excitatory')


#electrodes.ACSource(start=0.0,stop=10000.0,amplitude=1.0,offset=0.0,frequency=4,phase=0.0).inject_into(neuron_ex)




neuron_ex.record(['spikes','v'])

neuron_in.record(['spikes','v'])

sim.run(simtime)



out_spikes_ex=neuron_ex.get_data('spikes')
mem_v_ex=neuron_ex.get_data('v').segments[0]
v_ex=mem_v_ex.filter(name='v')[0]
np.save('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/mp_exE_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2',v_ex)


plt.figure()

plot_spiketrains(out_spikes_ex.segments[0])
plt.xlabel('Time (ms)')
plt.ylabel('Neuronid')
plt.savefig('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/spikes_ex_E_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2.png')



Figure(Panel(v_ex,ylabel='Membrane Potential (mV)',xticks=True,xlabel='Time (ms)',yticks=True), settings={'savefig.dpi':300}).save('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/v_ex_E_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2.png')




out_spikes_in=neuron_in.get_data('spikes')
mem_v_in=neuron_in.get_data('v').segments[0]
v_in=mem_v_in.filter(name='v')[0]
np.save('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/mp_inE_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2',v_in)


plt.figure()

plot_spiketrains(out_spikes_in.segments[0])
plt.xlabel('Time (ms)')
plt.ylabel('Neuronid')

plt.savefig('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/spikes_in_E_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2.png')



Figure(Panel(v_in,ylabel='Membrane Potential (mV)',xticks=True,xlabel='Time (ms)',yticks=True), settings={'savefig.dpi':300}).save('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/v_in_E_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2.png')

results_ex=dict(spikes=dict(),signals=dict())



# Extract the raw data to store it

rec_spikes_ex=out_spikes_ex.segments[0]
tr_ex=rec_spikes_ex.spiketrains
results_ex['spikes']=[t.times for t in tr_ex]

rec_signals_ex=mem_v_ex
array_ex=rec_signals_ex.analogsignals

if array_ex:
   results_ex['signals']=np.array(array_ex)
with open('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/results_ex_E_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2.pickle','wb') as f:
     pickle.dump(results_ex,f)



results_in=dict(spikes=dict(),signals=dict())



# Extract the raw data to store it

rec_spikes_in=out_spikes_in.segments[0]
tr_in=rec_spikes_in.spiketrains
results_in['spikes']=[t.times for t in tr_in]

rec_signals_in=mem_v_in
array_in=rec_signals_in.analogsignals

if array_in:
   results_in['signals']=np.array(array_in)


with open('spin3_results/noisy_wave_E_RS_I_FS_population5050_inpr05_i5_snr2/results_in_E_RS_I_FS_noisywavef1_population5050_prexex01_prexin01_prinex01_prinin01_ioffsetex5in5_wexex015_wexin015_g5_inpr05_s2.pickle','wb') as f1:
     pickle.dump(results_in,f1)


sim.end()










