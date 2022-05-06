import pyNN.spiNNaker as sim
import matplotlib
matplotlib.use('SVG')
import numpy as np
import matplotlib.pyplot as plt
import pickle
from pyNN.utility.plotting import Figure,Panel
from pyNN.random import NumpyRNG,RandomDistribution
from pyNN.utility import get_simulator,init_logging,normalized_filename


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
SNR=18.0
fs=5000.0
ts=1./fs

samples=np.linspace(0,t,int(fs*t),endpoint=False)

f=6.0

wave=np.sin(2*np.pi*f*samples)
noise=np.random.randn(len(wave))

sig_v=np.var(wave)

n_v=np.var(noise)

k=sig_v/(n_v*10**(SNR/10))

new_n=np.sqrt(k)*noise

noisy_wave=wave+new_n


t_wave=np.arange(0,(len(wave)*ts),ts)


# Apply DVS


on_s,off_s=dvs(wave)

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
   
dt=0.5
delay=1
extra={}



sim.setup(timestep=dt,min_delay=delay,max_delay=delay,**extra)
sim.set_number_of_neurons_per_core(izk,1)
rng=NumpyRNG(seed=1,parallel_safe=True)

#[0.07746952, 0.2171109 , 0.25375802, 0.27679948, 0.0742837 , 0.12948881, 0.24188027, 0.18678166, 0.05058233, 0.01550525]


# Neuron parameters for different types of dynamics (Izhikevich (2003))
neuron_params_RS={'a':0.02,'b':0.2,'c':-65.0,'d':8.0,'i_offset':0.0}            # Regular Spiking
neuron_params_IB={'a':0.02,'b':0.2,'c':-55.0,'d':4.0,'i_offset':0.0}            # Intrinsically Bursting
neuron_params_CH={'a':0.02,'b':0.2,'c':-50.0,'d':2.0,'i_offset':0.0}            # Chattering
neuron_params_FS={'a':0.1,'b':0.2,'c':-65.0,'d':2.0,'i_offset':0.0}             # Fast spiking
neuron_params_LTS={'a':0.02,'b':0.25,'c':-65.0,'d':2.0,'i_offset':0.0}          # Low threshold spiking
neuron_params_TC={'a':0.02,'b':0.25,'c':-65.0,'d':0.05,'i_offset':-10.0}          # Thalamocortical
neuron_params_RZ={'a':0.1,'b':0.26,'c':-65.0,'d':2.0,'i_offset':0.0}  # Resonator






on_input_ex=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in on_s_t_ex]))

on_input_in=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in on_s_t_in]))

off_input_ex=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in off_s_t_ex]))

off_input_in=sim.Population(50,sim.SpikeSourceArray(spike_times=[t for t in off_s_t_in]))






#p_g=sim.Population(1,sim.SpikeSourcePoisson(rate=2.0),label='poisson_source')

neuron=sim.Population(1,izk(**neuron_params_RZ))



#p_path=sim.Projection(p_g,neuron,sim.AllToAllConnector(),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay),receptor_type='excitatory')

on_path_ex=sim.Projection(on_input_ex,neuron,sim.AllToAllConnector(),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay),receptor_type='excitatory')
on_path_in=sim.Projection(on_input_in,neuron,sim.AllToAllConnector(),synapse_type=sim.StaticSynapse(weight=-0.15,delay=delay),receptor_type='inhibitory')

off_path_ex=sim.Projection(off_input_ex,neuron,sim.AllToAllConnector(),synapse_type=sim.StaticSynapse(weight=0.15,delay=delay),receptor_type='excitatory')
off_path_in=sim.Projection(off_input_in,neuron,sim.AllToAllConnector(),synapse_type=sim.StaticSynapse(weight=-0.15,delay=delay),receptor_type='inhibitory')


#on_input.record('spikes')
neuron.record(['spikes','v'])

sim.run(simtime)


out_spikes=neuron.get_data('spikes')
mem_v=neuron.get_data('v').segments[0]
v=mem_v.filter(name='v')[0]
np.save('/home/shavika/Documents/spin3_results/pure_wave_rz_population5050_3/mp_rz_pop_purewavef6',v)




plt.figure()

plot_spiketrains(out_spikes.segments[0])
plt.xlabel('Time (ms)')
plt.ylabel('Neuronid')


    

plt.savefig('/home/shavika/Documents/spin3_results/pure_wave_rz_population5050_3/izk_rz_pop_spikes_purewavef6.png')

    

Figure(Panel(v,ylabel='Membrane Potential (mV)',xticks=True,xlabel='Time (ms)',yticks=True), settings={'savefig.dpi':300}).save('/home/shavika/Documents/spin3_results/pure_wave_rz_population5050_3/v_rz_pop_purewavef6.png')


    

results=dict(spikes=dict(),signals=dict())
   
    

# Extract the raw data to store it

    

rec_spikes=out_spikes.segments[0]
tr=rec_spikes.spiketrains
results['spikes']=[t.times for t in tr]

rec_signals=mem_v
array=rec_signals.analogsignals

if array:
   results['signals']=np.array(array)

with open('/home/shavika/Documents/spin3_results/pure_wave_rz_population5050_3/results_rz_pop_purewavef6.pickle','w') as f:
     pickle.dump(results,f)



sim.end()


