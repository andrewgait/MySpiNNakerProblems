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
    if (b < 0.001):
        return a
    else:
        return (float_gcd(b, a - math.floor(a / b) * b))


print("gcd of 2.5 and 3.5: ", float_gcd(2.5, 3.5))
print("gcd of 0.5 and 2.25: ", float_gcd(0.5, 2.25))
print("gcd of 0.003125 and 0.5: ", float_gcd(0.0003125, 0.5))
print("gcd of 5.125 and 3.15625: ", float_gcd(5.125, 3.15625))
print("gcd of 0.005 and 0.0035", float_gcd(0.005, 0.0035))
print("gcd of 0.00023 and 0.0000013", float_gcd(0.00023, 0.0000013))
print("gcd of 0.303847577293368 and 1.0", float_gcd(0.303847577293368, 1.0))
print("gcd of 0.100006103515625 and 0.0999755859375",
      float_gcd(0.100006103515625, 0.0999755859375))
print("gcd of 2.5 and 0.00669921875", float_gcd(2.5, 0.00669921875))