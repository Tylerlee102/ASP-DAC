# Introduction

Debug traces are often either too large to keep continuously or too incomplete to reproduce failures caused by asynchronous peripherals. Runtime monitors can detect a violation, but detection alone does not provide the input schedule needed to replay the same bug.

ReplayCapsule-RV targets a narrower question: for a single-core embedded RV32I system with deterministic core execution, interrupts, and memory-mapped I/O, which hardware-visible events are sufficient to replay a safety failure?

The project deliberately avoids claiming novelty for tracing, monitoring, snapshots, or deterministic replay in general. Its proposed contribution is a model and implementation of event sufficiency at the interrupt/MMIO boundary.

