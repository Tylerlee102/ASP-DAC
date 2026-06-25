# Motivation

Consider firmware that polls a sensor, enters a critical MMIO update, and services a timer interrupt. A failure may depend on the exact sensor value returned by an MMIO read and the commit-index at which the interrupt is delivered. A final snapshot can show the bad state, but it does not explain or replay the nondeterministic schedule that produced it. A branch trace can show control flow, but not the sensor value. A monitor can flag the violation, but not replay it.

ReplayCapsule-RV records the nondeterministic boundary events needed to replay this failure and attaches the property-failure signature that defines success.

