#ifndef _MY_THRESHOLD_TYPE_H_
#define _MY_THRESHOLD_TYPE_H_

#include <neuron/threshold_types/threshold_type.h>
#include <random.h>
#include <limits.h>
#include <debug.h>

typedef struct threshold_type_t {

    // TODO: Add any additional parameters here

    REAL threshold_value;

//    REAL my_param;

    // probability of firing
    uint32_t prob_fire;

    // seed random number generator
    uint32_t seed[4];

} threshold_type_t;

static inline bool threshold_type_is_above_threshold(state_t value,
                        threshold_type_pointer_t threshold_type) {

    // TODO: Perform the appropriate operations

	// Set the test_value to max so that false is returned when
	// value is not over threshold_value
	uint32_t test_value = UINT_MAX;

	// If value is over threshold_value, use the random function
	// mars_kiss64_seed to get a random uint32_t for test_value
	if (REAL_COMPARE(value,>=,threshold_type->threshold_value))
	{
		test_value = mars_kiss64_seed(threshold_type->seed);
	}

	// Debug checking
//	log_info("test_value is %08x", test_value);
//	log_info("prob_fire is %08x", threshold_type->prob_fire);

    // TODO: Update to return true if the test_value is less than
	// the input probability / otherwise return false
    return (test_value < threshold_type->prob_fire);
}

#endif // _MY_THRESHOLD_TYPE_H_
