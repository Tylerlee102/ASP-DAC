#ifdef RC_RUNTIME_BASELINE
#include "Vpicorv32_baseline_top.h"
using RuntimeTop = Vpicorv32_baseline_top;
constexpr bool kHasRecorder = false;
#else
#include "Vreplaycapsule_verilator_top.h"
using RuntimeTop = Vreplaycapsule_verilator_top;
constexpr bool kHasRecorder = true;
#endif

#include "verilated.h"

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>

double sc_time_stamp() { return 0.0; }

namespace {

constexpr uint32_t RESET_PC = 0x00000080u;
constexpr uint32_t SENSOR_ADDR = 0x40000000u;
constexpr uint32_t ACTUATOR_ADDR = 0x40000004u;
constexpr uint32_t CONFIG_ADDR = 0x40000008u;
constexpr uint32_t COMMAND_ADDR = 0x4000000cu;
constexpr uint32_t CONFIG_SAFE_MAGIC = 0x0000cafeu;
constexpr uint32_t WATCHDOG_HEARTBEAT = 0x0000feedu;
constexpr uint32_t CAPTURE_REPLAYCAPSULE_RV = 3u;
constexpr uint32_t CAPTURE_DISABLED = 4u;

struct Options {
  std::string config;
  std::string benchmark;
  std::string variant;
  std::string firmware;
  int seed = 1;
  uint64_t max_cycles = 100000;
  uint32_t capture_mode = CAPTURE_REPLAYCAPSULE_RV;
  uint32_t arch_select = 1u;
  uint32_t recorder_config_select = 0u;
};

struct Stimulus {
  uint32_t sensor = 850;
  uint32_t command = 0;
  bool irq_after_command = false;
  uint32_t irq_pulse_cycles = 24;
  uint32_t expected_property = 0;
};

struct PropertyModel {
  uint8_t deadline_count = 0;
  uint8_t watchdog_count = 0;
  bool sensor_deadline_active = false;
  bool watchdog_active = false;
  bool safe_config_seen = false;
  bool critical_section_active = false;
  bool failed = false;
  uint32_t property_id = 0;

  void mmio_read(uint32_t addr, uint32_t data) {
    if (addr == SENSOR_ADDR && data > 700u) {
      sensor_deadline_active = true;
      deadline_count = 16u;
      watchdog_active = true;
      watchdog_count = 12u;
    }
  }

  void write(uint32_t addr, uint32_t data, uint32_t commit) {
    if (addr == COMMAND_ADDR && (data & 1u) && data != WATCHDOG_HEARTBEAT) {
      critical_section_active = true;
    } else if (addr == CONFIG_ADDR) {
      critical_section_active = false;
    }
    if (addr == CONFIG_ADDR && data == CONFIG_SAFE_MAGIC) {
      safe_config_seen = true;
    }
    if (addr == ACTUATOR_ADDR && data > 100u) {
      fail(1u);
    } else if (addr == ACTUATOR_ADDR && data != 0u && !safe_config_seen) {
      fail(5u);
    } else if (addr == ACTUATOR_ADDR && data <= 100u) {
      sensor_deadline_active = false;
      deadline_count = 0u;
    }
    if (addr == COMMAND_ADDR && data == WATCHDOG_HEARTBEAT) {
      watchdog_active = false;
      watchdog_count = 0u;
    }
    if (addr >= 0x00001000u && addr < 0x00001400u) {
      fail(4u);
    }
    (void)commit;
  }

  void interrupt_enter() {
    if (critical_section_active) {
      fail(2u);
    }
  }

  void commit(uint32_t watchdog_enabled) {
    if (watchdog_enabled && watchdog_active) {
      if (watchdog_count == 0u) {
        fail(6u);
      } else {
        --watchdog_count;
      }
    }
    if (sensor_deadline_active) {
      if (deadline_count == 0u) {
        fail(3u);
      } else {
        --deadline_count;
      }
    }
  }

  void fail(uint32_t id) {
    if (!failed) {
      failed = true;
      property_id = id;
    }
  }
};

bool require_value(int* index, int argc, char** argv, std::string* value) {
  if (*index + 1 >= argc) return false;
  *value = argv[++(*index)];
  return true;
}

bool parse_args(int argc, char** argv, Options* options) {
  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    std::string value;
    if (arg == "--config" && require_value(&i, argc, argv, &value)) {
      options->config = value;
    } else if (arg == "--benchmark" && require_value(&i, argc, argv, &value)) {
      options->benchmark = value;
    } else if (arg == "--variant" && require_value(&i, argc, argv, &value)) {
      options->variant = value;
    } else if (arg == "--firmware" && require_value(&i, argc, argv, &value)) {
      options->firmware = value;
    } else if (arg == "--seed" && require_value(&i, argc, argv, &value)) {
      options->seed = std::stoi(value);
    } else if (arg == "--max-cycles" && require_value(&i, argc, argv, &value)) {
      options->max_cycles = std::stoull(value);
    } else if (arg == "--capture-mode" && require_value(&i, argc, argv, &value)) {
      options->capture_mode = static_cast<uint32_t>(std::stoul(value, nullptr, 0));
    } else {
      std::cerr << "unknown or incomplete argument: " << arg << "\n";
      return false;
    }
  }
  return !options->config.empty() && !options->benchmark.empty() &&
         !options->variant.empty() && !options->firmware.empty();
}

Stimulus stimulus_for(const std::string& benchmark, const std::string& variant) {
  Stimulus s;
  const bool edge = variant == "no_failure_edge";
  const bool fixed = variant == "fixed";
  if (benchmark == "sensor_threshold_bug") {
    s.sensor = edge ? 300 : 850;
    s.expected_property = (fixed || edge) ? 0 : 3;
  } else if (benchmark == "interrupt_race_bug") {
    s.irq_after_command = !fixed;
    s.expected_property = fixed ? 0 : 2;
  } else if (benchmark == "mmio_ordering_bug") {
    s.expected_property = fixed ? 0 : 5;
  } else if (benchmark == "stack_corruption_bug") {
    s.expected_property = fixed ? 0 : 4;
  } else if (benchmark == "uart_command_bug") {
    s.command = (fixed || edge) ? 0 : 0x55;
    s.expected_property = (fixed || edge) ? 0 : 1;
  } else if (benchmark == "watchdog_timeout_bug") {
    s.sensor = (fixed || edge) ? 300 : 850;
    s.expected_property = (fixed || edge) ? 0 : 6;
  }
  return s;
}

bool load_hex(const std::string& path, std::map<uint32_t, uint32_t>* memory, std::string* error) {
  std::ifstream in(path);
  if (!in) {
    *error = "firmware hex not found: " + path;
    return false;
  }
  uint32_t addr = RESET_PC;
  std::string token;
  while (in >> token) {
    if (token.empty()) continue;
    if (token[0] == '@') {
      addr = static_cast<uint32_t>(std::stoul(token.substr(1), nullptr, 16));
      continue;
    }
    uint32_t word = static_cast<uint32_t>(std::stoul(token, nullptr, 16));
    memory->insert_or_assign(addr, word);
    addr += 4;
  }
  return true;
}

uint32_t read_word(const std::map<uint32_t, uint32_t>& memory, uint32_t addr) {
  auto it = memory.find(addr);
  if (it == memory.end()) return 0x00000013u;
  return it->second;
}

void write_word(std::map<uint32_t, uint32_t>* memory, uint32_t addr, uint32_t data, uint8_t wstrb) {
  uint32_t current = read_word(*memory, addr);
  for (int i = 0; i < 4; ++i) {
    if (wstrb & (1u << i)) {
      current &= ~(0xffu << (8 * i));
      current |= ((data >> (8 * i)) & 0xffu) << (8 * i);
    }
  }
  (*memory)[addr] = current;
}

uint32_t capsule_count(const RuntimeTop& top) {
#ifdef RC_RUNTIME_BASELINE
  (void)top;
  return 0u;
#else
  return top.capsule_event_count;
#endif
}

void configure_recorder(RuntimeTop* top, const Options& options) {
#ifdef RC_RUNTIME_BASELINE
  (void)top;
  (void)options;
#else
  top->clear = 0;
  top->capture_mode = options.capture_mode;
  top->arch_select = options.arch_select;
  top->recorder_config_select = options.recorder_config_select;
  top->watchdog_enable = options.benchmark == "watchdog_timeout_bug" ? 1 : 0;
  top->external_input_valid = 0;
  top->external_input_value = 0;
  top->capsule_read_addr = 0;
#endif
}

uint32_t top_commit_count(const RuntimeTop& top) {
  return top.commit_count;
}

uint32_t capsule_bytes(uint32_t events, const Options& options) {
  return events * (options.arch_select == 2u ? 8u : 21u);
}

void usage(const char* argv0) {
  std::cerr << "usage: " << argv0
            << " --config NAME --benchmark NAME --variant NAME --firmware PATH"
            << " [--seed N] [--max-cycles N] [--capture-mode N]\n";
}

}  // namespace

int main(int argc, char** argv) {
  Options options;
  if (!parse_args(argc, argv, &options)) {
    usage(argv[0]);
    return 2;
  }
  if (options.config == "recorder_present_disabled") {
    options.capture_mode = CAPTURE_DISABLED;
  } else if (options.config == "recorder_enabled") {
    options.capture_mode = CAPTURE_REPLAYCAPSULE_RV;
  } else if (options.config == "v2_recorder_present_disabled") {
    options.arch_select = 2u;
    options.recorder_config_select = 0u;
    options.capture_mode = CAPTURE_DISABLED;
  } else if (options.config == "v2_recorder_enabled_core") {
    options.arch_select = 2u;
    options.recorder_config_select = 0u;
    options.capture_mode = CAPTURE_REPLAYCAPSULE_RV;
  } else if (options.config == "v2_recorder_enabled_hashed") {
    options.arch_select = 2u;
    options.recorder_config_select = 1u;
    options.capture_mode = CAPTURE_REPLAYCAPSULE_RV;
  } else if (options.config == "v2_recorder_enabled_full") {
    options.arch_select = 2u;
    options.recorder_config_select = 2u;
    options.capture_mode = CAPTURE_REPLAYCAPSULE_RV;
  }

  std::map<uint32_t, uint32_t> memory;
  std::string error;
  if (!load_hex(options.firmware, &memory, &error)) {
    std::cerr << "error_code=FIRMWARE_LOAD\n" << error << "\n";
    return 1;
  }

  VerilatedContext context;
  RuntimeTop top{&context};
  Stimulus stimulus = stimulus_for(options.benchmark, options.variant);
  PropertyModel property;
  uint32_t irq_pulse_remaining = 0;
  uint32_t last_eoi = 0;
  uint32_t last_commit = 0;
  uint64_t cycles = 0;

  top.clk = 0;
  top.rst_n = 0;
  top.mem_ready = 0;
  top.mem_rdata = 0;
  top.irq = 0;
  configure_recorder(&top, options);

  for (int i = 0; i < 5; ++i) {
    top.clk = 0; top.eval();
    top.clk = 1; top.eval();
    context.timeInc(1);
  }
  top.rst_n = 1;

  for (; cycles < options.max_cycles && !property.failed; ++cycles) {
    top.clk = 0;
    top.eval();

    top.mem_ready = top.mem_valid ? 1 : 0;
    top.mem_rdata = 0x00000013u;
    if (top.mem_valid) {
      const uint32_t addr = top.mem_addr;
      if (top.mem_instr) {
        top.mem_rdata = read_word(memory, addr);
      } else if (top.mem_wstrb == 0) {
        if (addr == SENSOR_ADDR) {
          top.mem_rdata = stimulus.sensor;
        } else if (addr == COMMAND_ADDR) {
          top.mem_rdata = stimulus.command;
        } else {
          top.mem_rdata = read_word(memory, addr);
        }
        if (addr >= 0x40000000u) {
          property.mmio_read(addr, top.mem_rdata);
        }
      } else {
        if (addr < 0x40000000u) {
          write_word(&memory, addr, top.mem_wdata, top.mem_wstrb);
        }
        property.write(addr, top.mem_wdata, top_commit_count(top));
        if (stimulus.irq_after_command && addr == COMMAND_ADDR && (top.mem_wdata & 1u)) {
          irq_pulse_remaining = stimulus.irq_pulse_cycles;
        }
      }
    }

    if (irq_pulse_remaining > 0) {
      top.irq = 1;
      --irq_pulse_remaining;
    } else {
      top.irq = 0;
    }

    top.eval();
    top.clk = 1;
    top.eval();
    context.timeInc(1);

    if (top.eoi != 0u && last_eoi == 0u) {
      property.interrupt_enter();
    }
    last_eoi = top.eoi;

    const uint32_t current_commit = top_commit_count(top);
    while (last_commit < current_commit && !property.failed) {
      property.commit(options.benchmark == "watchdog_timeout_bug" ? 1u : 0u);
      ++last_commit;
    }
  }

  const bool expected_failure = stimulus.expected_property != 0u;
  bool ok = true;
  std::string notes = "measured";
  if (expected_failure && !property.failed) {
    ok = false;
    notes = "expected property failure did not occur";
  } else if (expected_failure && property.property_id != stimulus.expected_property) {
    ok = false;
    notes = "wrong property ID";
  } else if (!expected_failure && property.failed) {
    ok = false;
    notes = "unexpected property failure";
  }

  const uint32_t events = capsule_count(top);
  const uint32_t bytes = capsule_bytes(events, options);
  std::cout << (ok ? "PASS" : "FAIL")
            << " runtime config=" << options.config
            << " benchmark=" << options.benchmark
            << " variant=" << options.variant
            << " seed=" << options.seed
            << " property=" << property.property_id
            << " events=" << events
            << " capsule_bytes=" << bytes
            << " cycles=" << cycles
            << " commits=" << top_commit_count(top)
            << " notes=\"" << notes << "\"\n";
  if (!ok) {
    std::cerr << "error_code=RUNTIME_PROPERTY\n";
  }
  return ok ? 0 : 1;
}
