#include "rtl_harness.h"

#include "Vreplaycapsule_verilator_top.h"
#include "verilated.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>

namespace {

constexpr uint32_t RESET_PC = 0x00000080u;
constexpr uint32_t SENSOR_ADDR = 0x40000000u;
constexpr uint32_t ACTUATOR_ADDR = 0x40000004u;
constexpr uint32_t CONFIG_ADDR = 0x40000008u;
constexpr uint32_t COMMAND_ADDR = 0x4000000cu;

struct Stimulus {
  uint32_t sensor = 850;
  uint32_t command = 0;
  bool irq_after_command = false;
  uint32_t irq_pulse_cycles = 24;
  uint32_t expected_property = 0;
};

std::string rel(const std::string& path) {
  return std::filesystem::path(path).generic_string();
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
    *error = "firmware hex not found: " + rel(path);
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
    (*memory)[addr] = word;
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

std::vector<CapsuleEvent> events_of_type(const Capsule& capsule, uint32_t type) {
  std::vector<CapsuleEvent> out;
  for (const auto& event : capsule.events) {
    if (event.event_type == type) out.push_back(event);
  }
  return out;
}

bool compare_events(const Capsule& expected, const Capsule& observed, std::string* notes) {
  if (expected.property_id != observed.property_id) {
    *notes = "property ID mismatch";
    return false;
  }
  if (expected.property_signature != observed.property_signature) {
    *notes = "property signature mismatch";
    return false;
  }
  if (expected.events.size() != observed.events.size()) {
    *notes = "event count mismatch";
    return false;
  }
  for (size_t i = 0; i < expected.events.size(); ++i) {
    if (expected.events[i].packet_hex != observed.events[i].packet_hex) {
      std::ostringstream out;
      out << "event packet mismatch at index " << i;
      *notes = out.str();
      return false;
    }
  }
  *notes = "record/replay capsule packets match";
  return true;
}

uint32_t replay_mmio_value(const Capsule& capsule, size_t* mmio_read_index, uint32_t addr, bool* ok, std::string* notes) {
  std::vector<CapsuleEvent> reads = events_of_type(capsule, 5);
  if (*mmio_read_index >= reads.size()) {
    *ok = false;
    *notes = "replay MMIO read missing from capsule";
    return 0;
  }
  const auto& event = reads[*mmio_read_index];
  ++(*mmio_read_index);
  if (event.addr != addr) {
    *ok = false;
    std::ostringstream out;
    out << "replay MMIO address mismatch: expected 0x" << std::hex << event.addr << " got 0x" << addr;
    *notes = out.str();
    return 0;
  }
  return event.data;
}

uint32_t irq_from_capsule(const Capsule& capsule, uint32_t commit_count) {
  bool active = false;
  const uint32_t replay_window_commit = commit_count + 1u;
  for (const auto& event : capsule.events) {
    if (event.commit > replay_window_commit) continue;
    if (event.event_type == 7) active = true;
    if (event.event_type == 8) active = false;
  }
  return active ? 1u : 0u;
}

Capsule read_capsule_from_dut(Vreplaycapsule_verilator_top* top, const HarnessOptions& options) {
  Capsule capsule;
  capsule.benchmark = options.benchmark;
  capsule.variant = options.variant;
  capsule.seed = options.seed;
  capsule.mode = options.mode;
  capsule.property_id = top->property_id;
  capsule.property_signature = top->property_signature;
  capsule.overflow = top->capsule_overflow;
  const uint32_t count = top->capsule_event_count;
  for (uint32_t i = 0; i < count; ++i) {
    top->capsule_read_addr = i;
    top->eval();
    std::string packet = packet_hex_from_words(
        top->capsule_word0,
        top->capsule_word1,
        top->capsule_word2,
        top->capsule_word3,
        top->capsule_word4,
        top->capsule_word5);
    capsule.events.push_back(decode_packet_hex(packet));
  }
  return capsule;
}

std::string debug_base(const HarnessOptions& options) {
  std::ostringstream out;
  out << options.benchmark << "_" << options.variant << "_seed" << options.seed << "_"
      << options.mode << "_events.json";
  return (std::filesystem::path(options.debug_dir) / out.str()).generic_string();
}

void write_debug_events(const HarnessOptions& options, const Capsule& capsule) {
  if (!options.debug_events) return;
  std::string error;
  write_capsule_json(debug_base(options), capsule, &error);
}

}  // namespace

HarnessResult run_harness(const HarnessOptions& options) {
  HarnessResult result;
  result.capsule.benchmark = options.benchmark;
  result.capsule.variant = options.variant;
  result.capsule.seed = options.seed;
  result.capsule.mode = options.mode;

  std::map<uint32_t, uint32_t> memory;
  std::string error;
  if (!load_hex(options.firmware, &memory, &error)) {
    result.error_code = "FIRMWARE_LOAD";
    result.notes = error;
    return result;
  }

  Capsule record_capsule;
  if (options.mode == "replay" && !read_capsule_json(options.capsule_path, &record_capsule, &error)) {
    result.error_code = "CAPSULE_LOAD";
    result.notes = error;
    return result;
  }

  VerilatedContext context;
  Vreplaycapsule_verilator_top top{&context};
  const Stimulus stimulus = stimulus_for(options.benchmark, options.variant);
  size_t replay_mmio_index = 0;
  bool replay_ok = true;
  std::string replay_notes = "ok";
  uint32_t irq_pulse_remaining = 0;

  top.clk = 0;
  top.rst_n = 0;
  top.clear = 0;
  top.capture_mode = 3;
  top.mem_ready = 0;
  top.mem_rdata = 0;
  top.irq = 0;
  top.watchdog_enable = options.benchmark == "watchdog_timeout_bug" ? 1 : 0;
  top.external_input_valid = 0;
  top.external_input_value = 0;
  top.capsule_read_addr = 0;

  for (int i = 0; i < 5; ++i) {
    top.clk = 0; top.eval();
    top.clk = 1; top.eval();
    context.timeInc(1);
  }
  top.rst_n = 1;

  uint64_t cycles = 0;
  bool saw_failure = false;
  for (; cycles < options.max_cycles && replay_ok; ++cycles) {
    top.clk = 0;
    top.eval();

    top.mem_ready = top.mem_valid ? 1 : 0;
    top.mem_rdata = 0x00000013u;
    if (top.mem_valid) {
      const uint32_t addr = top.mem_addr;
      if (top.mem_instr) {
        top.mem_rdata = read_word(memory, addr);
      } else if (top.mem_wstrb == 0) {
        if (options.mode == "replay" && (addr == SENSOR_ADDR || addr == COMMAND_ADDR)) {
          top.mem_rdata = replay_mmio_value(record_capsule, &replay_mmio_index, addr, &replay_ok, &replay_notes);
        } else if (addr == SENSOR_ADDR) {
          top.mem_rdata = stimulus.sensor;
        } else if (addr == COMMAND_ADDR) {
          top.mem_rdata = stimulus.command;
        } else {
          top.mem_rdata = read_word(memory, addr);
        }
      } else {
        if (addr < 0x40000000u) {
          write_word(&memory, addr, top.mem_wdata, top.mem_wstrb);
        }
        if (stimulus.irq_after_command && addr == COMMAND_ADDR && (top.mem_wdata & 1u)) {
          irq_pulse_remaining = stimulus.irq_pulse_cycles;
        }
      }
    }

    if (options.mode == "replay") {
      top.irq = irq_from_capsule(record_capsule, top.commit_count);
    } else if (irq_pulse_remaining > 0) {
      top.irq = 1;
      --irq_pulse_remaining;
    } else {
      top.irq = 0;
    }

    top.eval();
    top.clk = 1;
    top.eval();
    context.timeInc(1);

    if (top.property_fail_valid) {
      saw_failure = true;
      result.cycles_to_failure = cycles + 1;
      result.commits_to_failure = top.commit_count;
      break;
    }
  }

  if (!replay_ok) {
    result.error_code = "REPLAY_STIMULUS";
    result.notes = replay_notes;
  } else if (stimulus.expected_property != 0 && !saw_failure) {
    result.error_code = "NO_EXPECTED_FAILURE";
    result.notes = "expected property failure did not occur";
  } else if (stimulus.expected_property != 0 && top.property_id != stimulus.expected_property) {
    result.error_code = "WRONG_PROPERTY";
    result.notes = "wrong property ID";
  } else if (stimulus.expected_property == 0 && saw_failure) {
    result.error_code = "UNEXPECTED_FAILURE";
    result.notes = "fixed/edge variant produced a property failure";
  } else {
    result.ok = true;
    result.notes = saw_failure ? "property failure observed" : "no false property failure";
    result.cycles_to_failure = saw_failure ? result.cycles_to_failure : cycles;
    result.commits_to_failure = top.commit_count;
  }

  result.capsule = read_capsule_from_dut(&top, options);
  write_debug_events(options, result.capsule);
  std::string write_error;
  if (!options.capsule_path.empty() && options.mode == "record") {
    write_capsule_json(options.capsule_path, result.capsule, &write_error);
  }
  if (options.mode == "replay" && result.ok) {
    std::string compare_note;
    result.ok = compare_events(record_capsule, result.capsule, &compare_note);
    result.notes = compare_note;
    if (!result.ok) result.error_code = "EVENT_MISMATCH";
  }
  if (!options.signature_path.empty()) {
    write_signature_json(
        options.signature_path,
        result.capsule,
        result.cycles_to_failure,
        result.commits_to_failure,
        result.ok,
        result.notes,
        &write_error);
  }
  return result;
}
