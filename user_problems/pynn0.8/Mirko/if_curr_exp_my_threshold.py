# A PyNN Model for standard neurons built from components
from spynnaker.pyNN.models.neuron import AbstractPyNNNeuronModelStandard
# Components from main tools
from spynnaker.pyNN.models.neuron.input_types import InputTypeCurrent
from spynnaker.pyNN.models.neuron.synapse_types import SynapseTypeExponential
from spynnaker.pyNN.models.defaults import default_initial_values
from spynnaker.pyNN.models.neuron.neuron_models import NeuronModelLeakyIntegrateAndFire
from python_models8.neuron.threshold_types.my_threshold_type import (
    MyThresholdType)


class IFCurrExpMyThreshold(AbstractPyNNNeuronModelStandard):

    @default_initial_values({"v", "isyn_exc", "isyn_inh","my_inh_input_previous"})
  
    def __init__(
            self,
            tau_m=20.0, cm=1.0, v_rest=-65.0, v_reset=-65.0,
            threshold_value=-52.0, tau_syn_E=5.0, tau_syn_I=5.0, tau_refrac=0.1,
            i_offset=0.0, v=-65.0, isyn_exc=0.0, isyn_inh=0.0,
            my_multiplicator=0.0, my_inh_input_previous=0.0, tau_th= (10 ** 5)*5,
            e_rev_E=0, e_rev_I= -100, my_threshold_parameter=0.5, my_neuron_parameter= -70):

        # create neuron model class
        neuron_model = NeuronModelLeakyIntegrateAndFire(v, my_neuron_parameter, v_rest, tau_m, cm, i_offset, v_reset, tau_refrac)

        # create synapse type model
        synapse_type = SynapseTypeExponential(
            tau_syn_E, tau_syn_I, isyn_exc, isyn_inh)

        # create input type model
        input_type = InputTypeCurrent(my_multiplicator, my_inh_input_previous)

        # create threshold type model
        threshold_type = MyThresholdType(
            threshold_value,tau_th, my_threshold_parameter)

        # Create the model using the superclass
        super().__init__(

            # the model a name (shown in reports)
            model_name="IFCurrExpMyThreshold",

            # the matching binary name
            binary="if_curr_exp_my_threshold.aplx",

            # the various model types
            neuron_model=neuron_model, input_type=input_type,
            synapse_type=synapse_type, threshold_type=threshold_type)
