from data_specification.enums import DataType

datatype = DataType.S1615

def find_closest_representable_value(value):
    """ Returns the closest value to the given value that can be
        represented by this type
    :param value:
    :type value: float or in
    :rtype: float
    """
    return decode_from_int(datatype.encode_as_int(value))


def decode_from_int(value):
        """ Decode a single value represented as an int according to this type.
        :param int array:
        :rtype: float or int
        """
        return value / float(datatype.scale)


print("4.9: ", find_closest_representable_value(4.9))
print("5.0: ", find_closest_representable_value(5.0))
print("0.1: ", find_closest_representable_value(0.1))