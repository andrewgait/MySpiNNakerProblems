#include "spin1_api.h"
#include "common-typedefs.h"
#include <data_specification.h>
#include <simulation.h>
#include <debug.h>

// ------------------------------------------------------------------------
// simulation control variables
// ------------------------------------------------------------------------
static uint32_t simulation_ticks;
static uint32_t infinite_run;
static uint32_t timer_period;
static uint32_t time = 0;
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// initialise simulation parameters and setup control
// ------------------------------------------------------------------------
static uint sim_init() {
    // get the data specification address in SDRAM
    data_specification_metadata_t * data =
            data_specification_get_data_address();

    // check that the header is correct
    if (!data_specification_read_header(data)) {
        return 1;
    }

    // set up the simulation interface (system region)
    if (!simulation_initialise(
            data_specification_get_region(0, data),
            APPLICATION_NAME_HASH, &timer_period, &simulation_ticks,
            &infinite_run, &time, 0, 0)) {
        return 1;
    }

    return 0;
}
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// timer callback: print message to iobuf
// ------------------------------------------------------------------------
void do_tick(uint tick, uint null) {
    use(null);

    time++;

    // show progress every once in a while
    if ((tick % 10) == 0) {
      log_info("timed tick: %u %u\n", tick, time);
    }

    // check if time to finish
    if (tick >= simulation_ticks) {
        // stop timer ticks,
        simulation_exit();

        // and let host know that we're ready
        simulation_ready_to_read();
    }
}
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// do something at the start of the simulation
// ------------------------------------------------------------------------
void get_started(void) {
    for (uint i = 0; i <= 10; i++) {
      log_info("untimed step: %u\n", i);
    }
}
// ------------------------------------------------------------------------

// ------------------------------------------------------------------------
// main: initialise simulation, register callbacks and run simulation
// ------------------------------------------------------------------------
void c_main() {
    // initialise the simulation,
    if (sim_init()) {
        rt_error(RTE_SWERR);
    }

    time = UINT32_MAX;

    for (uint i = 0; i <= 10; i++) {
      log_info("c_main step: %u\n", i);
    }

    // set up timer,
    spin1_set_timer_tick(timer_period);
    spin1_callback_on(TIMER_TICK, do_tick, 0);

    // setup simulation,
    simulation_set_start_function(get_started);

    // and run simulation
    simulation_run();
}
// ------------------------------------------------------------------------
