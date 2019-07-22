import spynnaker8 as sp
from pyNN.utility.plotting import Figure, Panel
import matplotlib.pyplot as plt
source_connection0 = []
source_connection1 = []
connection = []
spike_time = [[], []]
time_window = 1000
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
            neuron_id = (x-1)*128+y-1
            if (neuron_id,neuron_id) not in connection:
                connection.append((neuron_id, neuron_id))
            if p == 1:
                spike_time[1].append(time)
                if (1, neuron_id) not in source_connection1:
                    source_connection1.append((0, neuron_id))
            if p == 0:
                spike_time[0].append(time)
                if (0,neuron_id) not in source_connection0:
                    source_connection0.append((0, neuron_id))

f.close()

neuron_size = 128*128
sp.setup(timestep=1.0)
cell_params_lif = {'cm': 0.25,
                   'i_offset': 0.0,
                   'tau_m': 20.0,
                   'tau_refrac': 2.0,
                   'tau_syn_E': 5.0,
                   'tau_syn_I': 5.0,
                   'v_reset': -70.0,
                   'v_rest': -65.0,
                   'v_thresh': -50.0
                   }
Input0 = sp.Population(1, sp.SpikeSourceArray(spike_times=spike_time[0]))
Input1 = sp.Population(1, sp.SpikeSourceArray(spike_times=spike_time[1]))
off = sp.Population(neuron_size, sp.IF_curr_exp(**cell_params_lif), label='B_off')
on = sp.Population(neuron_size, sp.IF_curr_exp(**cell_params_lif), label='B_on')
Output = sp.Population(neuron_size, sp.IF_curr_exp(**cell_params_lif), label='output')
Input0_to_Output = sp.Projection(Input0, Output, sp.FromListConnector(source_connection0))
Input1_to_Output = sp.Projection(Input1, Output, sp.FromListConnector(source_connection1))
Input0_to_off = sp.Projection(Input0, off, sp.FromListConnector(source_connection0))
Input0_to_on = sp.Projection(Input0, on, sp.FromListConnector(source_connection1),
                             receptor_type="inhibitory")
Input1_to_off = sp.Projection(Input1, off, sp.FromListConnector(source_connection0),
                              receptor_type="inhibitory")
Input1_to_on = sp.Projection(Input1, on, sp.FromListConnector(source_connection1))
on_to_Output = sp.Projection(on, Output, sp.FromListConnector(connection),
                             receptor_type="inhibitory")
off_to_Output = sp.Projection(off, Output, sp.FromListConnector(connection),
                              receptor_type="inhibitory")
sp.run(time_window)
on.record(['v', 'spikes'])
v = on.get_data('v')
spike = on.get_data('spikes')
Figure(
    Panel(spike.segments[0].spiketrains,
          yticks=True, markersize=0.2, xlim=(0, time_window)),
    Panel(v.segments[0].filter(name='v')[0],
          ylabel="Membrane potential (mV)",
          )
)
plt.show()
sp.end()