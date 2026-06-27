// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Primary model header
//
// This header should be included by all source files instantiating the design.
// The class here is then constructed to instantiate the design.
// See the Verilator manual for examples.

#ifndef VERILATED_VREPLAYCAPSULE_VERILATOR_TOP_H_
#define VERILATED_VREPLAYCAPSULE_VERILATOR_TOP_H_  // guard

#include "verilated.h"

class Vreplaycapsule_verilator_top__Syms;
class Vreplaycapsule_verilator_top___024root;

// This class is the main interface to the Verilated model
class alignas(VL_CACHE_LINE_BYTES) Vreplaycapsule_verilator_top VL_NOT_FINAL : public VerilatedModel {
  private:
    // Symbol table holding complete model state (owned by this class)
    Vreplaycapsule_verilator_top__Syms* const vlSymsp;

  public:

    // CONSTEXPR CAPABILITIES
    // Verilated with --trace?
    static constexpr bool traceCapable = false;

    // PORTS
    // The application code writes and reads these signals to
    // propagate new values into/out from the Verilated model.
    VL_IN8(&clk,0,0);
    VL_IN8(&rst_n,0,0);
    VL_IN8(&clear,0,0);
    VL_IN8(&capture_mode,3,0);
    VL_OUT8(&trap,0,0);
    VL_OUT8(&mem_valid,0,0);
    VL_OUT8(&mem_instr,0,0);
    VL_IN8(&mem_ready,0,0);
    VL_OUT8(&mem_wstrb,3,0);
    VL_IN8(&external_input_valid,0,0);
    VL_IN8(&capsule_read_addr,7,0);
    VL_OUT8(&capsule_word5,7,0);
    VL_OUT8(&capsule_frozen,0,0);
    VL_OUT8(&capsule_overflow,0,0);
    VL_OUT8(&property_fail_valid,0,0);
    VL_OUT8(&property_id,7,0);
    VL_OUT16(&capsule_event_count,8,0);
    VL_OUT(&mem_addr,31,0);
    VL_OUT(&mem_wdata,31,0);
    VL_IN(&mem_rdata,31,0);
    VL_IN(&irq,31,0);
    VL_OUT(&eoi,31,0);
    VL_IN(&external_input_value,31,0);
    VL_OUT(&capsule_word0,31,0);
    VL_OUT(&capsule_word1,31,0);
    VL_OUT(&capsule_word2,31,0);
    VL_OUT(&capsule_word3,31,0);
    VL_OUT(&capsule_word4,31,0);
    VL_OUT(&running_signature,31,0);
    VL_OUT(&property_signature,31,0);
    VL_OUT(&commit_count,31,0);

    // CELLS
    // Public to allow access to /* verilator public */ items.
    // Otherwise the application code can consider these internals.

    // Root instance pointer to allow access to model internals,
    // including inlined /* verilator public_flat_* */ items.
    Vreplaycapsule_verilator_top___024root* const rootp;

    // CONSTRUCTORS
    /// Construct the model; called by application code
    /// If contextp is null, then the model will use the default global context
    /// If name is "", then makes a wrapper with a
    /// single model invisible with respect to DPI scope names.
    explicit Vreplaycapsule_verilator_top(VerilatedContext* contextp, const char* name = "TOP");
    explicit Vreplaycapsule_verilator_top(const char* name = "TOP");
    /// Destroy the model; called (often implicitly) by application code
    virtual ~Vreplaycapsule_verilator_top();
  private:
    VL_UNCOPYABLE(Vreplaycapsule_verilator_top);  ///< Copying not allowed

  public:
    // API METHODS
    /// Evaluate the model.  Application must call when inputs change.
    void eval() { eval_step(); }
    /// Evaluate when calling multiple units/models per time step.
    void eval_step();
    /// Evaluate at end of a timestep for tracing, when using eval_step().
    /// Application must call after all eval() and before time changes.
    void eval_end_step() {}
    /// Simulation complete, run final blocks.  Application must call on completion.
    void final();
    /// Are there scheduled events to handle?
    bool eventsPending();
    /// Returns time at next time slot. Aborts if !eventsPending()
    uint64_t nextTimeSlot();
    /// Trace signals in the model; called by application code
    void trace(VerilatedTraceBaseC* tfp, int levels, int options = 0) { contextp()->trace(tfp, levels, options); }
    /// Retrieve name of this model instance (as passed to constructor).
    const char* name() const;

    // Abstract methods from VerilatedModel
    const char* hierName() const override final;
    const char* modelName() const override final;
    unsigned threads() const override final;
    /// Prepare for cloning the model at the process level (e.g. fork in Linux)
    /// Release necessary resources. Called before cloning.
    void prepareClone() const;
    /// Re-init after cloning the model at the process level (e.g. fork in Linux)
    /// Re-allocate necessary resources. Called after cloning.
    void atClone() const;
  private:
    // Internal functions - trace registration
    void traceBaseModel(VerilatedTraceBaseC* tfp, int levels, int options);
};

#endif  // guard
