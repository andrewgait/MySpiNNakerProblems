from spynnaker.pyNN.utilities import utility_calls
from spynnaker.pyNN.models.neural_properties import NeuronParameter
from data_specification.enums import DataType
from spynnaker.pyNN.models.neuron.threshold_types import AbstractThresholdType

from enum import Enum
import random
from pyNN.random import NumpyRNG

class _MY_THRESHOLD_TYPES(Enum):

    THRESHOLD_VALUE = (1, DataType.S1615)
    PROB_FIRE = (2, DataType.UINT32)
    SEED = (3, DataType.UINT32)

    def __new__(cls, value, data_type):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._data_type = data_type
        return obj

    @property
    def data_type(self):
        return self._data_type


class MyThresholdType(AbstractThresholdType):
    """ A threshold that is a static value
    """
    def __init__(
            self, n_neurons,

            # TODO: update parameters
            threshold_value, prob_fire, seed, rng=None):
        AbstractThresholdType.__init__(self)
        self._n_neurons = n_neurons

        # TODO: Store any parameters
        self._threshold_value = utility_calls.convert_param_to_numpy(
            threshold_value, n_neurons)

        # Convert prob_fire to uint32 from [0,1]
        self._prob_fire = int(utility_calls.convert_param_to_numpy(
            prob_fire, n_neurons) * 0xFFFFFFFF)

        print prob_fire
        print self._prob_fire

        # Get rng (if it hasn't been defined yet) using NumpyRNG
        if rng is None:
            rng = NumpyRNG(seed=seed)

        # now get seed from rng
        seed = [rng.randint(0xFFFFFFFF) for _ in range(4)]
        print seed

        # Validate the random seed here
        utility_calls.validate_mars_kiss_64_seed(seed)

        self._seed = utility_calls.convert_param_to_numpy(
            seed, n_neurons*4)

    # TODO: Add getters and setters for the parameters

    @property
    def threshold_value(self):
        return self._threshold_value

    @threshold_value.setter
    def threshold_value(self, threshold_value):
        self._threshold_value = utility_calls.convert_param_to_numpy(
            threshold_value, self._n_neurons)

    @property
    def prob_fire(self):
        return self._prob_fire

    @prob_fire.setter
    def prob_fire(self, prob_fire):
        self._prob_fire = utility_calls.convert_param_to_numpy(
            prob_fire, self._n_neurons) * 0x7FFFFFFF

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, seed):
        self._seed = utility_calls.convert_param_to_numpy(
            seed, self._n_neurons)

    def get_n_threshold_parameters(self):

        # TODO: update to return the number of parameters
        # Note: This must match the number of values in the threshold_type_t
        # data structure in the C code
        return 3

    def get_threshold_parameters(self):

        # TODO: update to return the parameters
        # Note: The order of the parameters must match the order in the
        # threshold_type_t data structure in the C code
        return [
            NeuronParameter(self._threshold_value,
                            _MY_THRESHOLD_TYPES.THRESHOLD_VALUE.data_type),
            NeuronParameter(self._prob_fire,
                            _MY_THRESHOLD_TYPES.PROB_FIRE.data_type),
            NeuronParameter(self._seed,
                            _MY_THRESHOLD_TYPES.SEED.data_type)
        ]

    def get_threshold_parameter_types(self):

        # TODO: update to return the parameter types
        return [item.data_type for item in _MY_THRESHOLD_TYPES]

    def get_n_cpu_cycles_per_neuron(self):

        # TODO: update to the number of cycles used by\
        # threshold_type_is_above_threshold
        # Note: This can be guessed
        return 100
