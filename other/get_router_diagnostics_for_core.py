from spinnman.transceiver import create_transceiver_from_hostname
from board_test_configuration import BoardTestConfiguration
from spinn_machine import CoreSubsets, CoreSubset
from spinnman.model.enums import CPUState

board_config = BoardTestConfiguration()
board_config.set_up_remote_board()

# n_cores = 20
core_subsets = CoreSubsets(core_subsets=[])

down_cores = CoreSubsets()
down_chips = CoreSubsets(core_subsets=[])

chip_x = 41
chip_y = 68

transceiver = create_transceiver_from_hostname(
    board_config.remotehost, board_config.board_version,
    ignore_cores=down_cores, ignore_chips=down_chips,
    bmp_connection_data=board_config.bmp_names,
    auto_detect_bmp=board_config.auto_detect_bmp)
try:
    # get the router diagnostics for specified core
    router_diagnostics = transceiver.get_router_diagnostics(chip_x, chip_y)

    # print out error status
    print('diag.error_status: ', chip_x, chip_y, router_diagnostics.error_status)

finally:
    transceiver.close()
