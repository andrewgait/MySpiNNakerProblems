from __future__ import print_function
import sys
from spinnman.transceiver import create_transceiver_from_hostname
from spinn_utilities.make_tools.replacer import Replacer
from builtins import input
import traceback
import logging
import six
import os
from spinn_utilities.executable_finder import ExecutableFinder
from spynnaker.pyNN import model_binaries
from spinn_front_end_common import common_model_binaries


def read_iobuf(txrx, executable_finder, binary, x, y, p):
    real_binary = executable_finder.get_executable_path(binary)
    if real_binary is None:
        real_binary = executable_finder.get_executable_path(binary + ".aplx")
    if real_binary is None:
        real_binary = binary
    if not os.path.exists(real_binary):
        print("Unknown file:", real_binary)
        return
    replacer = Replacer(real_binary)
    iobuf = txrx.get_iobuf_from_core(x, y, p)
    txrx.close()
    for line in iobuf.iobuf.split("\n"):
        print(replacer.replace(line))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executable_finder = ExecutableFinder([])
    executable_finder.add_path(os.path.dirname(model_binaries.__file__))
    executable_finder.add_path(os.path.dirname(common_model_binaries.__file__))
    print(executable_finder.binary_paths)
    if len(sys.argv) == 6:
        (machine, binary, x, y, p) = sys.argv[1:]
        txrx = create_transceiver_from_hostname(machine, 3)
        read_iobuf(txrx, binary, int(x), int(y), int(p))
    elif len(sys.argv) == 2:
        machine = sys.argv[1]
        txrx = create_transceiver_from_hostname(machine, 3)
        try:
            while True:
                try:
                    inputs = input("<binary> <x> <y> <p>: ").split(" ")
                    if len(inputs) != 4:
                        print("Unrecognized input")
                    else:
                        (binary, x, y, p) = inputs
                        read_iobuf(txrx, executable_finder, binary,
                                   int(x), int(y), int(p))
                except Exception as e:
                    if isinstance(e, KeyboardInterrupt):
                        six.reraise(*sys.exc_info())
                    traceback.print_exc()
        except KeyboardInterrupt:
            txrx.close()
    else:
        print(
            "python -m spinn_front_end_common.iobuf"
            " <machine> [<binary> <x> <y> <p>]")
