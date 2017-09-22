# main interface to use the spynnaker related tools.
# ALL MODELS MUST INHERIT FROM THIS
from spynnaker.pyNN.models.neuron import AbstractPopulationVertex
from spynnaker8.utilities import DataHolder
from python_models8.neuron.builds.my_model_cond_exp import MyModelCondExpBase


class MyModelCondExpDataHolder(DataHolder):
    def __init__(
            self, spikes_per_second=(
                AbstractPopulationVertex.none_pynn_default_parameters[
                    'spikes_per_second']),
            ring_buffer_sigma=(
                AbstractPopulationVertex.none_pynn_default_parameters[
                    'ring_buffer_sigma']),
            incoming_spike_buffer_size=(
                AbstractPopulationVertex.none_pynn_default_parameters[
                    'incoming_spike_buffer_size']),
            constraints=AbstractPopulationVertex.none_pynn_default_parameters[
                'constraints'],
            label=AbstractPopulationVertex.none_pynn_default_parameters[
                'label'],
            v_init=MyModelCondExpBase.none_pynn_default_parameters['v_init'],
            v_thresh=MyModelCondExpBase.default_parameters['v_thresh'],
            tau_syn_E=MyModelCondExpBase.default_parameters['tau_syn_E'],
            tau_syn_I=MyModelCondExpBase.default_parameters['tau_syn_I'],
            isyn_exc=MyModelCondExpBase.default_parameters['isyn_exc'],
            isyn_inh=MyModelCondExpBase.default_parameters['isyn_inh'],
            e_rev_E=MyModelCondExpBase.default_parameters['e_rev_E'],
            e_rev_I=MyModelCondExpBase.default_parameters['e_rev_I'],
            my_parameter=MyModelCondExpBase.default_parameters['my_parameter'],
            i_offset=MyModelCondExpBase.default_parameters['i_offset']):
        DataHolder.__init__(
            self, {
                'spikes_per_second': spikes_per_second,
                'ring_buffer_sigma': ring_buffer_sigma,
                'incoming_spike_buffer_size': incoming_spike_buffer_size,
                'constraints': constraints,
                'label': label,
                'v_thresh': v_thresh,
                'tau_syn_E': tau_syn_E, 'tau_syn_I': tau_syn_I,
                'isyn_exc': isyn_exc, 'isyn_inh': isyn_inh,
                'e_rev_E': e_rev_E, 'e_rev_I': e_rev_I,
                'i_offset': i_offset,
                'my_parameter': my_parameter, 'v_init': v_init})

    @staticmethod
    def build_model():
        return MyModelCondExpBase
