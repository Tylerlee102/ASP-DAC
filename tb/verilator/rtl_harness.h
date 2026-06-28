#pragma once

#include "capsule_io.h"

#include <cstdint>
#include <map>
#include <string>
#include <vector>

struct HarnessOptions {
  std::string mode = "record";
  std::string benchmark;
  std::string variant;
  std::string firmware;
  std::string capsule_path;
  std::string signature_path;
  std::string debug_dir = "results/debug/pass4";
  std::string arch = "v1";
  std::string recorder_config = "core";
  int seed = 1;
  uint64_t max_cycles = 100000;
  uint32_t capture_mode = 3;
  bool debug_events = false;
  bool dump_mmio = false;
  bool dump_property = false;
  bool dump_pc = false;
  bool dump_disasm_context = false;
};

struct HarnessResult {
  bool ok = false;
  std::string error_code;
  std::string notes;
  Capsule capsule;
  uint64_t cycles_to_failure = 0;
  uint64_t commits_to_failure = 0;
};

HarnessResult run_harness(const HarnessOptions& options);
