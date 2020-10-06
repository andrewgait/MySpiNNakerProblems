import math

def float_gcd(a, b):
    """ Floating point gcd of two values
    """
    # Using absolute values for cases where a user has supplied a negative
    # weight appears necessary for Python 2.7
    a = abs(a)
    b = abs(b)

    if (a < b):
        return float_gcd(b, a)

    # base case
    if (abs(b) < 0.00001):
        return a
    else:
        return (float_gcd(b, a - math.floor(a / b) * b))


print("gcd of 2.5 and 3.5: ", float_gcd(2.5, 3.5))
print("gcd of 0.5 and 2.25: ", float_gcd(0.5, 2.25))
print("gcd of 0.003125 and 0.5: ", float_gcd(0.0003125, 0.5))