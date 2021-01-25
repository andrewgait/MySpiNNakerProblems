import logging

from pacman.model.constraints.key_allocator_constraints \
    import FixedKeyAndMaskConstraint
from pacman.model.decorators import overrides
from pacman.model.graphs.application import ApplicationSpiNNakerLinkVertex
from pacman.model.routing_info import BaseKeyAndMask
from spinn_front_end_common.abstract_models import \
    AbstractProvidesOutgoingPartitionConstraints
from spinn_front_end_common.abstract_models \
    import AbstractSendMeMulticastCommandsVertex
from spinn_front_end_common.abstract_models.impl import \
    ProvidesKeyToAtomMappingImpl
from spinn_front_end_common.utility_models import MultiCastCommand
from spynnaker.pyNN.exceptions import SpynnakerException

logger = logging.getLogger(__name__)

class ExternalCochleaDevice(
        ApplicationSpiNNakerLinkVertex, AbstractSendMeMulticastCommandsVertex,
        AbstractProvidesOutgoingPartitionConstraints,
        ProvidesKeyToAtomMappingImpl):

    #Number of channels of frequency
    CHANNELS_256 = "256"
    CHANNELS_128 = "128"
    CHANNELS_64 = "64"
    CHANNELS_32 = "32"
    CHANNELS_16 = "16"
    #Cochlea mode
    TYPE_MONO = "MONO"
    TYPE_STEREO = "STEREO"
    #Cochlea polarity
    POLARITY_UP = "UP"
    POLARITY_DOWN = "DOWN"
    POLARITY_MERGED = "MERGED"

    default_parameters = {
        'board_address': None, 'label': "ExternalCochleaDevice"}

    def __init__(
            self, cochlea_n_channels, cochlea_key, spinnaker_link_id, cochlea_type, cochlea_polarity,
            label=default_parameters['label'], n_neurons=None,
            board_address=default_parameters['board_address']):
        """
        :param cochlea_n_channels: The "number of frequency channels" of the cochlea
        :param cochlea_key: The value of the top 16-bits of the key
        :param spinnaker_link_id: The spinnaker link to which the cochlea is\
                connected
        :param cochlea_type: The cochlea "type". It can be either MONO (only one "ear")\
                or STEREO (two "ears")
        :param polarity: The "polarity" of the cochlea data (+spikes, -spikes, +-spikes)
        :param label:
        :param n_neurons: The number of neurons in the population
        :param board_address:
        """

        self._cochlea_type = cochlea_type
        logger.warn("The type selected for the FPGA cochlea is {}".format(self._cochlea_type))
        self._cochlea_polarity = cochlea_polarity
        logger.warn("The polarity selected for the FPGA cochlea is {}".format(self._cochlea_polarity))

        self._fixed_key = (cochlea_key & 0xFFFF) << 16
        self._fixed_mask = 0xFFFF8000
        if cochlea_type == ExternalCochleaDevice.TYPE_STEREO:
            self._fixed_key |= 0x4000

        logger.warn("The fixed_key selected for the FPGA cochlea is {}".format(self._fixed_key))
        fixed_n_neurons = self.get_n_neurons(cochlea_n_channels, cochlea_type, cochlea_polarity)
        self._fixed_mask = self._get_mask(cochlea_n_channels)
        logger.warn("The fixed_mask selected for the FPGA cochlea is {}".format(self._fixed_mask))

        if fixed_n_neurons != n_neurons and n_neurons is not None:
            logger.warn("The specified number of neurons for the FPGA cochlea"
                        " device has been ignored {} will be used instead"
                        .format(fixed_n_neurons))
        else:
            logger.warn("The number on neurons for the FPGA cochla is {} neurons".format(fixed_n_neurons))

        ApplicationSpiNNakerLinkVertex.__init__(
            self, n_atoms=fixed_n_neurons, spinnaker_link_id=spinnaker_link_id,
            label=label, max_atoms_per_core=fixed_n_neurons,
            board_address=board_address)
        AbstractProvidesOutgoingPartitionConstraints.__init__(self)
        ProvidesKeyToAtomMappingImpl.__init__(self)

    def _get_mask(self, cochlea_n_channels):
        if cochlea_n_channels == ExternalCochleaDevice.CHANNELS_128:
            return 0xFFFFC000
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_64:
            return 0xFFFFF000
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_32:
            return 0xFFFFFC00
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_16:
            return 0xFFFFFF00
        #elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_16:
            #return 0xFFFFFFC0
        else:
            raise SpynnakerException(
                "the FPGA cochlea does not recognise this number of channels")

    @staticmethod
    def get_n_neurons(cochlea_n_channels, cochlea_type, cochlea_polarity):
        
        device_n_neurons, device_n_channels, device_n_src, device_n_spikes = 1, 1, 1, 1

        if cochlea_type == ExternalCochleaDevice.TYPE_MONO:
            device_n_src = 1
        elif cochlea_type == ExternalCochleaDevice.TYPE_STEREO:
            device_n_src = 2
        else:
            raise SpynnakerException(
                "the FPGA cochlea does not recognise this type of cochlea")
        
        if cochlea_n_channels == ExternalCochleaDevice.CHANNELS_256:
            device_n_channels = 256
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_128:
            device_n_channels = 128
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_64:
            device_n_channels = 64
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_32:
            device_n_channels = 32
        elif cochlea_n_channels == ExternalCochleaDevice.CHANNELS_16:
            device_n_channels = 16
        else:
            raise SpynnakerException(
                "the FPGA cochlea does not recognise this number of channels")

        if cochlea_polarity == ExternalCochleaDevice.POLARITY_UP or cochlea_polarity == ExternalCochleaDevice.POLARITY_DOWN:
            device_n_spikes = 1
        elif cochlea_polarity == ExternalCochleaDevice.POLARITY_MERGED:
            device_n_spikes = 2
        else:
            raise SpynnakerException(
                "the FPGA cochlea does not reognise this type of polarity")
        
        device_n_neurons = (device_n_channels * device_n_src * device_n_spikes)
        
        return device_n_neurons

    @property
    @overrides(AbstractSendMeMulticastCommandsVertex.start_resume_commands)
    def start_resume_commands(self):
        return [MultiCastCommand(
            key=0x0000FFFF, payload=1, repeat=5,
            delay_between_repeats=100)]

    @property
    @overrides(AbstractSendMeMulticastCommandsVertex.pause_stop_commands)
    def pause_stop_commands(self):
        return [MultiCastCommand(
            key=0x0000FFFE, payload=0, repeat=5,
            delay_between_repeats=100)]

    @property
    @overrides(AbstractSendMeMulticastCommandsVertex.timed_commands)
    def timed_commands(self):
        return []

    def get_outgoing_partition_constraints(self, partition):
        return [FixedKeyAndMaskConstraint(
            [BaseKeyAndMask(self._fixed_key, self._fixed_mask)])]
