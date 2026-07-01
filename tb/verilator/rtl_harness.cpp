#include "rtl_harness.h"

#include "Vreplaycapsule_verilator_top.h"
#include "verilated.h"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <vector>

namespace {

constexpr uint32_t RESET_PC = 0x00000080u;
constexpr uint32_t SENSOR_ADDR = 0x40000000u;
constexpr uint32_t ACTUATOR_ADDR = 0x40000004u;
constexpr uint32_t CONFIG_ADDR = 0x40000008u;
constexpr uint32_t COMMAND_ADDR = 0x4000000cu;
constexpr uint32_t PROFILE2_SENSOR_ADDR = 0x40000040u;
constexpr uint32_t PROFILE2_ACTUATOR_ADDR = 0x40000044u;
constexpr uint32_t PROFILE2_CONFIG_ADDR = 0x40000048u;
constexpr uint32_t PROFILE2_COMMAND_ADDR = 0x4000004cu;

struct Stimulus {
  uint32_t sensor = 850;
  uint32_t command = 0;
  std::vector<uint32_t> sensor_sequence;
  std::vector<uint32_t> command_sequence;
  bool irq_after_command = false;
  uint32_t irq_pulse_cycles = 24;
  uint32_t expected_property = 0;
};

std::string rel(const std::string& path) {
  return std::filesystem::path(path).generic_string();
}

std::string hex32(uint32_t value) {
  std::ostringstream out;
  out << "0x" << std::hex << std::setw(8) << std::setfill('0') << value;
  return out.str();
}

uint64_t packet_word64(const CapsuleEvent& event) {
  return static_cast<uint64_t>(std::stoull(event.packet_hex, nullptr, 16));
}

uint64_t replay_packet_word64(const CapsuleEvent& event, uint32_t* last_commit) {
  uint64_t word = packet_word64(event);
  uint32_t delta = event.commit - *last_commit;
  *last_commit = event.commit;
  const uint32_t delta16 = std::min<uint32_t>(delta, 0xffffu);
  uint8_t flags = static_cast<uint8_t>((word >> 56) & 0xfu);
  uint8_t debug = static_cast<uint8_t>(word & 0xffu);
  if (delta > 0xffu) {
    flags |= 0x8u;
    debug = static_cast<uint8_t>((delta16 >> 8) & 0xffu);
  } else {
    flags &= static_cast<uint8_t>(~0x8u);
  }
  word &= ~(0xfull << 56);
  word &= ~(0xffull << 48);
  word &= ~0xffull;
  word |= static_cast<uint64_t>(flags) << 56;
  word |= static_cast<uint64_t>(delta16 & 0xffu) << 48;
  word |= static_cast<uint64_t>(debug);
  return word;
}

std::string packet_hex_from_stream_word(uint64_t word) {
  return packet_hex_from_v2_words(static_cast<uint32_t>(word & 0xffffffffull),
                                  static_cast<uint32_t>(word >> 32));
}

bool wants_debug_trace(const HarnessOptions& options) {
  return options.debug_events || options.dump_mmio || options.dump_property || options.dump_pc;
}

bool should_stall_valid_stream(
    const HarnessOptions& options,
    const Vreplaycapsule_verilator_top& top,
    size_t captured_words) {
  if (!options.stream_stall_test || options.arch != "v2" || !top.capsule_stream_valid) return false;
  const uint64_t handshakes_or_stalls = static_cast<uint64_t>(captured_words) + top.capsule_stream_stall_count;
  return (handshakes_or_stalls % 4u) == 0u;
}

void sample_capsule_stream(Vreplaycapsule_verilator_top* top, std::vector<uint64_t>* words) {
  if (top->capsule_stream_valid && top->capsule_stream_ready) {
    words->push_back(static_cast<uint64_t>(top->capsule_stream_word));
  }
}

void drain_capsule_stream(
    Vreplaycapsule_verilator_top* top,
    VerilatedContext* context,
    const HarnessOptions& options,
    std::vector<uint64_t>* words) {
  if (options.arch != "v2") return;
  for (int i = 0; i < 10000; ++i) {
    top->clk = 0;
    top->capsule_stream_ready = 1;
    top->eval();
    if (!top->capsule_stream_valid &&
        top->capsule_stream_sent_count >= top->capsule_stream_event_count) {
      break;
    }
    sample_capsule_stream(top, words);
    top->clk = 1;
    top->eval();
    context->timeInc(1);
  }
}

uint32_t replay_required_count(const Capsule& capsule) {
  uint32_t count = 0;
  for (const auto& event : capsule.events) {
    if (event.replay_required) ++count;
  }
  return count;
}

uint32_t arch_select_for(const std::string& arch) {
  return arch == "v2" ? 2u : 1u;
}

uint32_t recorder_config_select_for(const std::string& recorder_config) {
  if (recorder_config == "hashed") return 1u;
  if (recorder_config == "full") return 2u;
  return 0u;
}

std::filesystem::path debug_stem(const HarnessOptions& options) {
  std::ostringstream out;
  out << options.benchmark << "_" << options.variant << "_seed" << options.seed;
  return std::filesystem::path(options.debug_dir) / out.str();
}

void write_debug_lines(const HarnessOptions& options, const std::string& suffix, const std::vector<std::string>& lines) {
  if (lines.empty()) return;
  std::filesystem::create_directories(std::filesystem::path(options.debug_dir));
  const std::filesystem::path path = debug_stem(options).generic_string() + "_" + suffix;
  std::ofstream out;
  if (options.mode == "replay") {
    out.open(path, std::ios::app);
  } else {
    out.open(path);
  }
  out << "[" << options.mode << "]\n";
  for (const auto& line : lines) {
    out << line << "\n";
  }
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
  } else if (benchmark == "commanded_actuator_limit_bug") {
    s.command = 0x55;
    s.expected_property = fixed ? 0 : 1;
  } else if (benchmark == "late_config_sequence_bug") {
    s.expected_property = fixed ? 0 : 5;
  } else if (benchmark == "sensor_debounce_bug") {
    s.sensor_sequence = fixed ? std::vector<uint32_t>{850u, 300u} : std::vector<uint32_t>{850u, 300u};
    s.expected_property = fixed ? 0 : 3;
  } else if (benchmark == "status_clear_on_read_bug") {
    s.command_sequence = fixed ? std::vector<uint32_t>{0x55u, 0u} : std::vector<uint32_t>{0x55u, 0u};
    s.expected_property = fixed ? 0 : 1;
  } else if (benchmark == "platform2_status_window_bug") {
    s.command_sequence = fixed ? std::vector<uint32_t>{0x55u, 0u} : std::vector<uint32_t>{0x55u, 0u};
    s.expected_property = fixed ? 0 : 1;
  } else if (benchmark == "platform2_config_order_bug") {
    s.expected_property = fixed ? 0 : 5;
  } else if (benchmark == "environmental_controller_bug") {
    s.sensor = 650;
    s.command = 0x55;
    s.expected_property = fixed ? 0 : 1;
  } else if (benchmark == "power_rail_sequencer_bug") {
    s.sensor = 850;
    s.command = 0x55;
    s.expected_property = fixed ? 0 : 5;
  }
  return s;
}

uint32_t sequenced_value(const std::vector<uint32_t>& values, size_t* index, uint32_t fallback) {
  if (values.empty()) return fallback;
  const size_t selected = std::min(*index, values.size() - 1);
  ++(*index);
  return values[selected];
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

std::vector<CapsuleEvent> replay_required_events(const Capsule& capsule) {
  std::vector<CapsuleEvent> out;
  for (const auto& event : capsule.events) {
    if (event.replay_required) out.push_back(event);
  }
  return out;
}

void tick(Vreplaycapsule_verilator_top* top, VerilatedContext* context) {
  top->clk = 0;
  top->eval();
  top->clk = 1;
  top->eval();
  context->timeInc(1);
}

void preload_replay_source(
    Vreplaycapsule_verilator_top* top,
    VerilatedContext* context,
    const std::vector<CapsuleEvent>& events) {
  uint32_t last_commit = 0;
  top->replay_source_load_valid = 0;
  top->replay_source_load_addr = 0;
  top->replay_source_load_word = 0;
  for (size_t index = 0; index < events.size(); ++index) {
    top->replay_source_load_addr = static_cast<uint32_t>(index);
    top->replay_source_load_word = replay_packet_word64(events[index], &last_commit);
    top->replay_source_load_valid = 1;
    tick(top, context);
  }
  top->replay_source_load_valid = 0;
  top->replay_source_load_addr = 0;
  top->replay_source_load_word = 0;
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
  if (expected.architecture == "v2" || observed.architecture == "v2") {
    const std::vector<CapsuleEvent> expected_required = replay_required_events(expected);
    const std::vector<CapsuleEvent> observed_required = replay_required_events(observed);
    if (expected_required.size() != observed_required.size()) {
      *notes = "replay-critical event count mismatch";
      return false;
    }
    for (size_t i = 0; i < expected_required.size(); ++i) {
      const CapsuleEvent& lhs = expected_required[i];
      const CapsuleEvent& rhs = observed_required[i];
      if (lhs.event_type != rhs.event_type || lhs.commit != rhs.commit ||
          lhs.addr != rhs.addr || lhs.data != rhs.data ||
          lhs.payload_hash != rhs.payload_hash) {
        std::ostringstream out;
        out << "replay-critical event mismatch at index " << i
            << " expected type=" << lhs.event_type << " commit=" << lhs.commit
            << " addr=" << hex32(lhs.addr) << " data=" << hex32(lhs.data)
            << " hash=" << hex32(lhs.payload_hash)
            << " observed type=" << rhs.event_type << " commit=" << rhs.commit
            << " addr=" << hex32(rhs.addr) << " data=" << hex32(rhs.data)
            << " hash=" << hex32(rhs.payload_hash);
        *notes = out.str();
        return false;
      }
    }
    std::ostringstream out;
    out << "record/replay replay-critical events match";
    if (expected.events.size() != observed.events.size()) {
      out << "; diagnostic/context event counts differ record=" << expected.events.size()
          << " replay=" << observed.events.size();
    }
    *notes = out.str();
    return true;
  }
  if (expected.events.size() != observed.events.size()) {
    *notes = "event count mismatch";
    return false;
  }
  for (size_t i = 0; i < expected.events.size(); ++i) {
    if (expected.architecture == "v2" || observed.architecture == "v2") {
      const CapsuleEvent& lhs = expected.events[i];
      const CapsuleEvent& rhs = observed.events[i];
      if (lhs.event_type != rhs.event_type || lhs.commit != rhs.commit ||
          lhs.addr != rhs.addr || lhs.data != rhs.data ||
          lhs.payload_hash != rhs.payload_hash ||
          lhs.replay_required != rhs.replay_required ||
          lhs.diagnostic_only != rhs.diagnostic_only) {
        std::ostringstream out;
        out << "canonical event mismatch at index " << i
            << " expected type=" << lhs.event_type << " commit=" << lhs.commit
            << " addr=" << hex32(lhs.addr) << " data=" << hex32(lhs.data)
            << " hash=" << hex32(lhs.payload_hash)
            << " observed type=" << rhs.event_type << " commit=" << rhs.commit
            << " addr=" << hex32(rhs.addr) << " data=" << hex32(rhs.data)
            << " hash=" << hex32(rhs.payload_hash);
        *notes = out.str();
        return false;
      }
      continue;
    }
    if (expected.events[i].packet_hex != observed.events[i].packet_hex) {
      std::ostringstream out;
      out << "event packet mismatch at index " << i;
      *notes = out.str();
      return false;
    }
  }
  *notes = expected.architecture == "v2" ? "record/replay canonical events match" : "record/replay capsule packets match";
  return true;
}

Capsule read_capsule_from_dut(
    Vreplaycapsule_verilator_top* top,
    const HarnessOptions& options,
    const std::vector<uint64_t>& stream_words,
    bool property_latched,
    uint32_t latched_property_id,
    uint32_t latched_property_signature) {
  Capsule capsule;
  capsule.benchmark = options.benchmark;
  capsule.variant = options.variant;
  capsule.seed = options.seed;
  capsule.mode = options.mode;
  capsule.architecture = options.arch;
  capsule.recorder_config = options.recorder_config;
  capsule.packet_width_bits = options.arch == "v2" ? 64 : 168;
  capsule.property_id = property_latched ? latched_property_id : top->property_id;
  capsule.property_signature = property_latched ? latched_property_signature : top->property_signature;
  capsule.overflow = top->capsule_overflow || top->capsule_replay_critical_overflow_count != 0;
  capsule.stream_event_count = top->capsule_stream_event_count;
  capsule.stream_event_sent_count = top->capsule_stream_sent_count;
  capsule.replay_critical_event_count = top->capsule_replay_critical_event_count;
  capsule.stream_stall_count = top->capsule_stream_stall_count;
  capsule.dropped_diagnostic_count = top->capsule_dropped_diagnostic_count;
  capsule.replay_critical_overflow_count = top->capsule_replay_critical_overflow_count;
  if (options.arch == "v2") {
    for (uint64_t word : stream_words) {
      capsule.events.push_back(decode_packet_hex(packet_hex_from_stream_word(word), options.arch));
    }
    apply_v2_commit_deltas(&capsule);
    return capsule;
  }
  const uint32_t count = top->capsule_event_count;
  for (uint32_t i = 0; i < count; ++i) {
    top->capsule_read_addr = i;
    top->eval();
    std::string packet;
    if (options.arch == "v2") {
      packet = packet_hex_from_v2_words(top->capsule_word0, top->capsule_word1);
    } else {
      packet = packet_hex_from_words(
          top->capsule_word0,
          top->capsule_word1,
          top->capsule_word2,
          top->capsule_word3,
          top->capsule_word4,
          top->capsule_word5);
    }
    capsule.events.push_back(decode_packet_hex(packet, options.arch));
  }
  apply_v2_commit_deltas(&capsule);
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

HarnessResult run_self_replay_harness(const HarnessOptions& options) {
  HarnessResult final_result;
  final_result.capsule.benchmark = options.benchmark;
  final_result.capsule.variant = options.variant;
  final_result.capsule.seed = options.seed;
  final_result.capsule.mode = options.mode;
  final_result.capsule.architecture = options.arch;
  final_result.capsule.recorder_config = options.recorder_config;
  final_result.capsule.packet_width_bits = 64;
  final_result.replay_stimulus_source = "rtl_replay_mode_controller_capture_store_mmio_irq";

  if (options.arch != "v2") {
    final_result.error_code = "SELF_REPLAY_ARCH";
    final_result.notes = "self_replay mode requires arch=v2";
    return final_result;
  }

  std::map<uint32_t, uint32_t> initial_memory;
  std::string error;
  if (!load_hex(options.firmware, &initial_memory, &error)) {
    final_result.error_code = "FIRMWARE_LOAD";
    final_result.notes = error;
    return final_result;
  }

  struct PhaseResult {
    bool ok = false;
    std::string error_code;
    std::string notes;
    Capsule capsule;
    uint64_t cycles_to_failure = 0;
    uint64_t commits_to_failure = 0;
    bool replay_consumer_checked = false;
    bool replay_consumer_ok = true;
    uint32_t replay_consumer_expected = 0;
    uint32_t replay_consumer_consumed = 0;
    uint32_t replay_consumer_error_code = 0;
    uint32_t replay_source_sent = 0;
    bool replay_source_underflow = false;
  };

  VerilatedContext context;
  Vreplaycapsule_verilator_top top{&context};
  const Stimulus stimulus = stimulus_for(options.benchmark, options.variant);

  auto run_phase = [&](bool replay_phase, const Capsule* record_capsule, uint32_t expected_replay_count) {
    PhaseResult phase;
    HarnessOptions phase_options = options;
    phase_options.mode = replay_phase ? "replay" : "record";
    phase.capsule.benchmark = options.benchmark;
    phase.capsule.variant = options.variant;
    phase.capsule.seed = options.seed;
    phase.capsule.mode = phase_options.mode;
    phase.capsule.architecture = options.arch;
    phase.capsule.recorder_config = options.recorder_config;
    phase.capsule.packet_width_bits = 64;

    std::map<uint32_t, uint32_t> memory = initial_memory;
    size_t sensor_read_index = 0;
    size_t command_read_index = 0;
    uint32_t irq_pulse_remaining = 0;
    uint32_t last_irq_line = 0;
    bool property_latched = false;
    uint32_t latched_property_id = 0;
    uint32_t latched_property_signature = 0;
    bool replay_ok = true;
    std::string replay_notes = "ok";
    bool saw_failure = false;
    std::vector<uint64_t> streamed_capsule_words;
    std::vector<std::string> pc_trace;
    std::vector<std::string> mmio_trace;
    std::vector<std::string> property_trace;

    top.clk = 0;
    top.rst_n = 0;
    top.clear = 0;
    top.capture_mode = options.capture_mode & 0xfu;
    top.arch_select = arch_select_for(options.arch);
    top.recorder_config_select = recorder_config_select_for(options.recorder_config);
    top.replay_consume_start = 0;
    top.replay_consume_expected_count = 0;
    top.replay_consume_valid = 0;
    top.replay_consume_word = 0;
    top.replay_consume_stream_done = 0;
    top.replay_consume_use_source = replay_phase ? 1 : 0;
    top.replay_source_store_clear = replay_phase ? 0 : 1;
    top.replay_source_capture_enable = 0;
    top.replay_source_load_valid = 0;
    top.replay_source_load_addr = 0;
    top.replay_source_load_word = 0;
    top.replay_controller_enable = 1;
    top.replay_controller_arm_record = 0;
    top.replay_controller_start = 0;
    top.capsule_stream_ready = 1;
    top.mem_ready = 0;
    top.mem_rdata = 0;
    top.irq = 0;
    top.watchdog_enable = options.benchmark == "watchdog_timeout_bug" ? 1 : 0;
    top.external_input_valid = 0;
    top.external_input_value = 0;
    top.capsule_read_addr = 0;

    for (int i = 0; i < 5; ++i) {
      tick(&top, &context);
    }
    top.replay_source_store_clear = 0;
    top.replay_source_capture_enable = 0;
    top.rst_n = 1;

    if (!replay_phase) {
      top.replay_controller_arm_record = 1;
      tick(&top, &context);
      top.replay_controller_arm_record = 0;
    }

    if (replay_phase) {
      phase.replay_consumer_checked = true;
      phase.replay_consumer_expected = expected_replay_count;
      top.replay_consume_expected_count = phase.replay_consumer_expected;
      top.replay_controller_start = 1;
      tick(&top, &context);
      top.replay_controller_start = 0;
    }

    uint64_t cycles = 0;
    for (; cycles < options.max_cycles && replay_ok; ++cycles) {
      top.clk = 0;
      top.replay_consume_valid = 0;
      top.replay_consume_stream_done = 0;
      top.eval();

      top.mem_ready = top.mem_valid ? 1 : 0;
      top.mem_rdata = 0x00000013u;
      if (top.mem_valid) {
        const uint32_t addr = top.mem_addr;
        if (top.mem_instr) {
          top.mem_rdata = read_word(memory, addr);
          if ((options.debug_events || options.dump_pc) && pc_trace.size() < 512) {
            std::ostringstream line;
            line << "cycle=" << cycles << " commit=" << top.commit_count
                 << " fetch_pc=" << hex32(addr) << " instr=" << hex32(top.mem_rdata);
            pc_trace.push_back(line.str());
          }
        } else if (top.mem_wstrb == 0) {
          if (replay_phase && addr >= 0x40000000u) {
            top.mem_rdata = 0xd15ea5edu;
          } else if (addr == SENSOR_ADDR || addr == PROFILE2_SENSOR_ADDR) {
            top.mem_rdata = sequenced_value(stimulus.sensor_sequence, &sensor_read_index, stimulus.sensor);
          } else if (addr == COMMAND_ADDR || addr == PROFILE2_COMMAND_ADDR) {
            top.mem_rdata = sequenced_value(stimulus.command_sequence, &command_read_index, stimulus.command);
          } else {
            top.mem_rdata = read_word(memory, addr);
          }
          if ((options.debug_events || options.dump_mmio) && addr >= 0x40000000u) {
            std::ostringstream line;
            line << "cycle=" << cycles << " commit=" << top.commit_count
                 << " read addr=" << hex32(addr) << " data=" << hex32(top.mem_rdata);
            mmio_trace.push_back(line.str());
          }
          if ((options.debug_events || options.dump_property) && addr >= 0x40000000u) {
            std::ostringstream line;
            line << "cycle=" << cycles << " property_input=mmio_read"
                 << " commit=" << top.commit_count << " addr=" << hex32(addr)
                 << " data=" << hex32(top.mem_rdata);
            property_trace.push_back(line.str());
          }
        } else {
          if (addr < 0x40000000u) {
            write_word(&memory, addr, top.mem_wdata, top.mem_wstrb);
          }
          if (!replay_phase && stimulus.irq_after_command &&
              (addr == COMMAND_ADDR || addr == PROFILE2_COMMAND_ADDR) && (top.mem_wdata & 1u)) {
            irq_pulse_remaining = stimulus.irq_pulse_cycles;
          }
          if ((options.debug_events || options.dump_mmio) && addr >= 0x40000000u) {
            std::ostringstream line;
            line << "cycle=" << cycles << " commit=" << top.commit_count
                 << " write addr=" << hex32(addr) << " data=" << hex32(top.mem_wdata)
                 << " wstrb=" << hex32(top.mem_wstrb);
            mmio_trace.push_back(line.str());
          }
          if ((options.debug_events || options.dump_property) && addr >= 0x40000000u) {
            std::ostringstream line;
            line << "cycle=" << cycles << " property_input=mmio_write"
                 << " commit=" << top.commit_count << " addr=" << hex32(addr)
                 << " data=" << hex32(top.mem_wdata);
            property_trace.push_back(line.str());
          } else if ((options.debug_events || options.dump_property) && addr < 0x40000000u) {
            std::ostringstream line;
            line << "cycle=" << cycles << " property_input=store"
                 << " commit=" << top.commit_count << " addr=" << hex32(addr)
                 << " data=" << hex32(top.mem_wdata);
            property_trace.push_back(line.str());
          }
        }
      }

      if (replay_phase) {
        top.irq = 0;
      } else if (irq_pulse_remaining > 0) {
        top.irq = 1;
        --irq_pulse_remaining;
      } else {
        top.irq = 0;
      }
      if ((options.debug_events || options.dump_property) && top.irq != last_irq_line) {
        std::ostringstream line;
        line << "cycle=" << cycles << " property_input=irq_line"
             << " commit=" << top.commit_count << " value=" << hex32(top.irq);
        property_trace.push_back(line.str());
        last_irq_line = top.irq;
      }

      top.capsule_stream_ready = 1;
      top.eval();
      if (should_stall_valid_stream(phase_options, top, streamed_capsule_words.size())) {
        top.capsule_stream_ready = 0;
        top.eval();
      }
      sample_capsule_stream(&top, &streamed_capsule_words);
      top.clk = 1;
      top.eval();
      context.timeInc(1);

      if (replay_phase && top.replay_consume_error) {
        std::ostringstream out;
        out << "hardware replay consumer error_code=" << static_cast<unsigned>(top.replay_consume_error_code)
            << " consumed=" << static_cast<unsigned>(top.replay_consume_consumed_count)
            << "/" << expected_replay_count
            << " source_sent=" << static_cast<unsigned>(top.replay_source_sent_count);
        replay_ok = false;
        replay_notes = out.str();
      }
      if (replay_phase && top.replay_controller_error) {
        std::ostringstream out;
        out << "replay mode controller error_code=" << static_cast<unsigned>(top.replay_controller_error_code)
            << " state=" << static_cast<unsigned>(top.replay_controller_state)
            << " consumed=" << static_cast<unsigned>(top.replay_consume_consumed_count)
            << "/" << expected_replay_count;
        replay_ok = false;
        replay_notes = out.str();
      }

      if ((options.debug_events || options.dump_property) && top.property_fail_valid) {
        std::ostringstream line;
        line << "cycle=" << (cycles + 1) << " property_output=fail"
             << " commit=" << top.commit_count << " property_id=" << static_cast<unsigned>(top.property_id)
             << " signature=" << hex32(top.property_signature);
        property_trace.push_back(line.str());
      }

      if (top.property_fail_valid) {
        saw_failure = true;
        property_latched = true;
        latched_property_id = top.property_id;
        latched_property_signature = top.property_signature;
        phase.cycles_to_failure = cycles + 1;
        phase.commits_to_failure = top.commit_count;
        break;
      }
    }
    if (!saw_failure) {
      phase.cycles_to_failure = cycles;
      phase.commits_to_failure = top.commit_count;
    }

    top.clk = 0;
    top.replay_consume_valid = 0;
    top.replay_consume_stream_done = 0;
    top.eval();
    drain_capsule_stream(&top, &context, phase_options, &streamed_capsule_words);
    top.replay_source_capture_enable = 0;
    top.replay_controller_enable = 0;

    if (!replay_ok) {
      phase.error_code = "REPLAY_STIMULUS";
      phase.notes = replay_notes;
    } else if (stimulus.expected_property != 0 && !saw_failure) {
      phase.error_code = "NO_EXPECTED_FAILURE";
      phase.notes = "expected property failure did not occur";
    } else if (stimulus.expected_property != 0 && latched_property_id != stimulus.expected_property) {
      phase.error_code = "WRONG_PROPERTY";
      phase.notes = "wrong property ID";
    } else if (stimulus.expected_property == 0 && saw_failure) {
      phase.error_code = "UNEXPECTED_FAILURE";
      phase.notes = "fixed/edge variant produced a property failure";
    } else {
      phase.ok = true;
      phase.notes = saw_failure ? "property failure observed" : "no false property failure";
      phase.cycles_to_failure = saw_failure ? phase.cycles_to_failure : cycles;
      phase.commits_to_failure = top.commit_count;
    }

    phase.capsule = read_capsule_from_dut(
        &top,
        phase_options,
        streamed_capsule_words,
        property_latched,
        latched_property_id,
        latched_property_signature);
    if (wants_debug_trace(options)) {
      write_debug_lines(phase_options, "pc_trace.txt", pc_trace);
      write_debug_lines(phase_options, "mmio_trace.txt", mmio_trace);
      write_debug_lines(phase_options, "property_trace.txt", property_trace);
    }
    write_debug_events(phase_options, phase.capsule);

    if (phase.ok) {
      const uint32_t replay_required = replay_required_count(phase.capsule);
      if (phase.capsule.replay_critical_overflow_count != 0) {
        phase.ok = false;
        phase.error_code = "CRITICAL_STREAM_OVERFLOW";
        phase.notes = "replay-critical stream overflow counter was nonzero";
      } else if (phase.capsule.stream_event_sent_count != phase.capsule.stream_event_count ||
                 phase.capsule.stream_event_sent_count != phase.capsule.events.size()) {
        phase.ok = false;
        phase.error_code = "STREAM_COUNT_MISMATCH";
        phase.notes = "streamed capsule word count did not match recorder counters";
      } else if (phase.capsule.replay_critical_event_count != replay_required) {
        phase.ok = false;
        phase.error_code = "CRITICAL_COUNT_MISMATCH";
        phase.notes = "replay-critical counter did not match reconstructed capsule events";
      } else if (options.stream_stall_test && phase.capsule.stream_stall_count == 0) {
        phase.ok = false;
        phase.error_code = "STREAM_STALL_NOT_EXERCISED";
        phase.notes = "stream stall test did not observe any sink stalls";
      } else if (!replay_phase &&
                 (top.replay_source_capture_overflow ||
                  top.replay_source_captured_count != replay_required)) {
        phase.ok = false;
        phase.error_code = "RTL_CAPTURE_STORE";
        phase.notes = "RTL capture store did not retain the replay-critical capsule subset";
      } else if (!replay_phase) {
        std::ostringstream out;
        out << phase.notes << "; rtl replay mode controller retained "
            << static_cast<unsigned>(top.replay_source_captured_count) << "/"
            << replay_required << " replay-critical words for same-instance replay";
        phase.notes = out.str();
      }
    }

    if (replay_phase && phase.ok && record_capsule) {
      std::string compare_note;
      phase.ok = compare_events(*record_capsule, phase.capsule, &compare_note);
      phase.notes = compare_note;
      if (!phase.ok) phase.error_code = "EVENT_MISMATCH";
    }
    if (replay_phase) {
      phase.replay_consumer_consumed = top.replay_consume_consumed_count;
      phase.replay_consumer_error_code = top.replay_consume_error_code;
      phase.replay_source_sent = top.replay_source_sent_count;
      phase.replay_source_underflow = top.replay_source_underflow;
      phase.replay_consumer_ok =
          !top.replay_consume_error &&
          top.replay_consume_all_events &&
          top.replay_consume_consumed_count == phase.replay_consumer_expected &&
          top.replay_source_sent_count == phase.replay_consumer_expected &&
          !top.replay_source_underflow;
      if (phase.ok && !phase.replay_consumer_ok) {
        std::ostringstream out;
        out << "self replay consumer did not accept captured store: consumed="
            << phase.replay_consumer_consumed << "/" << phase.replay_consumer_expected
            << " source_sent=" << phase.replay_source_sent
            << " source_underflow=" << static_cast<unsigned>(phase.replay_source_underflow)
            << " error_code=" << phase.replay_consumer_error_code;
        phase.ok = false;
        phase.error_code = "RTL_CAPTURE_STORE_REPLAY";
        phase.notes = out.str();
      } else if (phase.ok) {
        std::ostringstream out;
        out << phase.notes << "; rtl replay mode controller launched captured-store replay and streamed "
            << phase.replay_source_sent << "/" << phase.replay_consumer_expected
            << " and replay consumer consumed " << phase.replay_consumer_consumed
            << "/" << phase.replay_consumer_expected
            << " without harness preload";
        phase.notes = out.str();
      }
    }
    return phase;
  };

  PhaseResult record = run_phase(false, nullptr, 0);
  if (!record.ok) {
    final_result.ok = false;
    final_result.error_code = record.error_code;
    final_result.notes = record.notes;
    final_result.capsule = record.capsule;
    return final_result;
  }

  const uint32_t expected_replay_count = replay_required_count(record.capsule);
  PhaseResult replay = run_phase(true, &record.capsule, expected_replay_count);
  final_result.ok = replay.ok;
  final_result.error_code = replay.error_code;
  final_result.notes = replay.notes;
  final_result.capsule = replay.capsule;
  final_result.capsule.mode = "self_replay";
  final_result.cycles_to_failure = replay.cycles_to_failure;
  final_result.commits_to_failure = replay.commits_to_failure;
  final_result.replay_consumer_checked = replay.replay_consumer_checked;
  final_result.replay_consumer_ok = replay.replay_consumer_ok;
  final_result.replay_consumer_expected = replay.replay_consumer_expected;
  final_result.replay_consumer_consumed = replay.replay_consumer_consumed;
  final_result.replay_consumer_error_code = replay.replay_consumer_error_code;

  std::string write_error;
  if (!options.capsule_path.empty()) {
    write_capsule_json(options.capsule_path, record.capsule, &write_error);
  }
  if (!options.signature_path.empty()) {
    write_signature_json(
        options.signature_path,
        final_result.capsule,
        final_result.cycles_to_failure,
        final_result.commits_to_failure,
        final_result.ok,
        final_result.notes,
        &write_error,
        final_result.replay_consumer_checked,
        final_result.replay_consumer_ok,
        final_result.replay_consumer_expected,
        final_result.replay_consumer_consumed,
        final_result.replay_consumer_error_code,
        final_result.replay_stimulus_source);
  }
  return final_result;
}

}  // namespace

HarnessResult run_harness(const HarnessOptions& options) {
  if (options.mode == "self_replay") {
    return run_self_replay_harness(options);
  }

  HarnessResult result;
  result.capsule.benchmark = options.benchmark;
  result.capsule.variant = options.variant;
  result.capsule.seed = options.seed;
  result.capsule.mode = options.mode;
  result.capsule.architecture = options.arch;
  result.capsule.recorder_config = options.recorder_config;
  result.capsule.packet_width_bits = options.arch == "v2" ? 64 : 168;

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
  size_t sensor_read_index = 0;
  size_t command_read_index = 0;
  const bool use_replay_consumer = options.mode == "replay" && options.arch == "v2";
  const bool use_replay_source = use_replay_consumer;
  const bool capture_replay_store = options.mode == "record" && options.arch == "v2";
  const std::vector<CapsuleEvent> replay_consumer_events =
      use_replay_consumer ? replay_required_events(record_capsule) : std::vector<CapsuleEvent>{};
  if (use_replay_consumer) {
    result.replay_stimulus_source = "rtl_capsule_source_mmio_irq";
  } else if (options.mode == "replay") {
    result.replay_stimulus_source = "host_replay_stimulus";
  } else {
    result.replay_stimulus_source = "record_environment";
  }
  uint32_t replay_consume_index = 0;
  uint32_t replay_consume_last_commit = 0;
  bool replay_word_valid = false;
  uint64_t replay_word = 0;
  bool replay_ok = true;
  std::string replay_notes = "ok";
  uint32_t irq_pulse_remaining = 0;
  uint32_t last_irq_line = 0;
  bool property_latched = false;
  uint32_t latched_property_id = 0;
  uint32_t latched_property_signature = 0;
  std::vector<uint64_t> streamed_capsule_words;
  std::vector<std::string> pc_trace;
  std::vector<std::string> mmio_trace;
  std::vector<std::string> property_trace;

  top.clk = 0;
  top.rst_n = 0;
  top.clear = 0;
  top.capture_mode = options.capture_mode & 0xfu;
  top.arch_select = arch_select_for(options.arch);
  top.recorder_config_select = recorder_config_select_for(options.recorder_config);
  top.replay_consume_start = 0;
  top.replay_consume_expected_count = 0;
  top.replay_consume_valid = 0;
  top.replay_consume_word = 0;
  top.replay_consume_stream_done = 0;
  top.replay_consume_use_source = use_replay_source ? 1 : 0;
  top.replay_source_store_clear = capture_replay_store ? 1 : 0;
  top.replay_source_capture_enable = 0;
  top.replay_source_load_valid = 0;
  top.replay_source_load_addr = 0;
  top.replay_source_load_word = 0;
  top.replay_controller_enable = 0;
  top.replay_controller_arm_record = 0;
  top.replay_controller_start = 0;
  top.capsule_stream_ready = 1;
  top.mem_ready = 0;
  top.mem_rdata = 0;
  top.irq = 0;
  top.watchdog_enable = options.benchmark == "watchdog_timeout_bug" ? 1 : 0;
  top.external_input_valid = 0;
  top.external_input_value = 0;
  top.capsule_read_addr = 0;

  if (use_replay_source) {
    preload_replay_source(&top, &context, replay_consumer_events);
  }

  for (int i = 0; i < 5; ++i) {
    top.clk = 0; top.eval();
    top.clk = 1; top.eval();
    context.timeInc(1);
  }
  top.replay_source_store_clear = 0;
  top.replay_source_capture_enable = capture_replay_store ? 1 : 0;
  top.rst_n = 1;

  if (use_replay_consumer) {
    result.replay_consumer_checked = true;
    result.replay_consumer_expected = static_cast<uint32_t>(replay_consumer_events.size());
    top.replay_consume_expected_count = result.replay_consumer_expected;
    top.replay_consume_start = 1;
    top.clk = 0; top.eval();
    top.clk = 1; top.eval();
    context.timeInc(1);
    top.replay_consume_start = 0;
  }

  uint64_t cycles = 0;
  bool saw_failure = false;
  for (; cycles < options.max_cycles && replay_ok; ++cycles) {
    top.clk = 0;
    top.replay_consume_valid = 0;
    top.replay_consume_stream_done = 0;

    if (use_replay_consumer && !use_replay_source && !replay_word_valid &&
        replay_consume_index < replay_consumer_events.size()) {
      replay_word = replay_packet_word64(replay_consumer_events[replay_consume_index], &replay_consume_last_commit);
      replay_word_valid = true;
    }
    top.replay_consume_word = replay_word;
    top.replay_consume_valid = use_replay_consumer && !use_replay_source && replay_word_valid;
    top.eval();

    top.mem_ready = top.mem_valid ? 1 : 0;
    top.mem_rdata = 0x00000013u;
    if (top.mem_valid) {
      const uint32_t addr = top.mem_addr;
      if (top.mem_instr) {
        top.mem_rdata = read_word(memory, addr);
        if ((options.debug_events || options.dump_pc) && pc_trace.size() < 512) {
          std::ostringstream line;
          line << "cycle=" << cycles << " commit=" << top.commit_count
               << " fetch_pc=" << hex32(addr) << " instr=" << hex32(top.mem_rdata);
          pc_trace.push_back(line.str());
        }
      } else if (top.mem_wstrb == 0) {
        if (options.mode == "replay" && addr >= 0x40000000u) {
          top.mem_rdata = 0xd15ea5edu;
        } else if (addr == SENSOR_ADDR || addr == PROFILE2_SENSOR_ADDR) {
          top.mem_rdata = sequenced_value(stimulus.sensor_sequence, &sensor_read_index, stimulus.sensor);
        } else if (addr == COMMAND_ADDR || addr == PROFILE2_COMMAND_ADDR) {
          top.mem_rdata = sequenced_value(stimulus.command_sequence, &command_read_index, stimulus.command);
        } else {
          top.mem_rdata = read_word(memory, addr);
        }
        if ((options.debug_events || options.dump_mmio) && addr >= 0x40000000u) {
          std::ostringstream line;
          line << "cycle=" << cycles << " commit=" << top.commit_count
               << " read addr=" << hex32(addr) << " data=" << hex32(top.mem_rdata);
          mmio_trace.push_back(line.str());
        }
        if ((options.debug_events || options.dump_property) && addr >= 0x40000000u) {
          std::ostringstream line;
          line << "cycle=" << cycles << " property_input=mmio_read"
               << " commit=" << top.commit_count << " addr=" << hex32(addr)
               << " data=" << hex32(top.mem_rdata);
          property_trace.push_back(line.str());
        }
      } else {
        if (addr < 0x40000000u) {
          write_word(&memory, addr, top.mem_wdata, top.mem_wstrb);
        }
        if (stimulus.irq_after_command &&
            (addr == COMMAND_ADDR || addr == PROFILE2_COMMAND_ADDR) && (top.mem_wdata & 1u)) {
          irq_pulse_remaining = stimulus.irq_pulse_cycles;
        }
        if ((options.debug_events || options.dump_mmio) && addr >= 0x40000000u) {
          std::ostringstream line;
          line << "cycle=" << cycles << " commit=" << top.commit_count
               << " write addr=" << hex32(addr) << " data=" << hex32(top.mem_wdata)
               << " wstrb=" << hex32(top.mem_wstrb);
          mmio_trace.push_back(line.str());
        }
        if ((options.debug_events || options.dump_property) && addr >= 0x40000000u) {
          std::ostringstream line;
          line << "cycle=" << cycles << " property_input=mmio_write"
               << " commit=" << top.commit_count << " addr=" << hex32(addr)
               << " data=" << hex32(top.mem_wdata);
          property_trace.push_back(line.str());
        } else if ((options.debug_events || options.dump_property) && addr < 0x40000000u) {
          std::ostringstream line;
          line << "cycle=" << cycles << " property_input=store"
               << " commit=" << top.commit_count << " addr=" << hex32(addr)
               << " data=" << hex32(top.mem_wdata);
          property_trace.push_back(line.str());
        }
      }
    }

    if (options.mode == "replay") {
      top.irq = 0;
    } else if (irq_pulse_remaining > 0) {
      top.irq = 1;
      --irq_pulse_remaining;
    } else {
      top.irq = 0;
    }
    if ((options.debug_events || options.dump_property) && top.irq != last_irq_line) {
      std::ostringstream line;
      line << "cycle=" << cycles << " property_input=irq_line"
           << " commit=" << top.commit_count << " value=" << hex32(top.irq);
      property_trace.push_back(line.str());
      last_irq_line = top.irq;
    }

    top.capsule_stream_ready = 1;
    top.eval();
    if (should_stall_valid_stream(options, top, streamed_capsule_words.size())) {
      top.capsule_stream_ready = 0;
      top.eval();
    }
    const bool replay_word_accepted =
        use_replay_consumer && !use_replay_source && replay_word_valid && top.replay_consume_ready;
    sample_capsule_stream(&top, &streamed_capsule_words);
    top.clk = 1;
    top.eval();
    context.timeInc(1);
    if (replay_word_accepted) {
      replay_word_valid = false;
      ++replay_consume_index;
    }

    if (use_replay_consumer && top.replay_consume_error) {
      std::ostringstream out;
      out << "hardware replay consumer error_code=" << static_cast<unsigned>(top.replay_consume_error_code)
          << " consumed=" << static_cast<unsigned>(top.replay_consume_consumed_count)
          << "/" << replay_consumer_events.size();
      if (use_replay_source) {
        out << " source_sent=" << static_cast<unsigned>(top.replay_source_sent_count);
      }
      replay_ok = false;
      replay_notes = out.str();
    }

    if ((options.debug_events || options.dump_property) && top.property_fail_valid) {
      std::ostringstream line;
      line << "cycle=" << (cycles + 1) << " property_output=fail"
           << " commit=" << top.commit_count << " property_id=" << static_cast<unsigned>(top.property_id)
           << " signature=" << hex32(top.property_signature);
      property_trace.push_back(line.str());
    }

    if (top.property_fail_valid) {
      saw_failure = true;
      property_latched = true;
      latched_property_id = top.property_id;
      latched_property_signature = top.property_signature;
      result.cycles_to_failure = cycles + 1;
      result.commits_to_failure = top.commit_count;
      break;
    }
  }
  if (!saw_failure) {
    result.cycles_to_failure = cycles;
    result.commits_to_failure = top.commit_count;
  }

  top.clk = 0;
  top.replay_consume_valid = 0;
  top.replay_consume_stream_done = 0;
  top.eval();

  drain_capsule_stream(&top, &context, options, &streamed_capsule_words);
  top.replay_source_capture_enable = 0;

  if (!replay_ok) {
    result.error_code = "REPLAY_STIMULUS";
    result.notes = replay_notes;
  } else if (stimulus.expected_property != 0 && !saw_failure) {
    result.error_code = "NO_EXPECTED_FAILURE";
    result.notes = "expected property failure did not occur";
  } else if (stimulus.expected_property != 0 && latched_property_id != stimulus.expected_property) {
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

  result.capsule = read_capsule_from_dut(
      &top,
      options,
      streamed_capsule_words,
      property_latched,
      latched_property_id,
      latched_property_signature);
  if (wants_debug_trace(options)) {
    write_debug_lines(options, "pc_trace.txt", pc_trace);
    write_debug_lines(options, "mmio_trace.txt", mmio_trace);
    write_debug_lines(options, "property_trace.txt", property_trace);
  }
  write_debug_events(options, result.capsule);
  if (result.ok && options.arch == "v2") {
    const uint32_t replay_required = replay_required_count(result.capsule);
    if (result.capsule.replay_critical_overflow_count != 0) {
      result.ok = false;
      result.error_code = "CRITICAL_STREAM_OVERFLOW";
      result.notes = "replay-critical stream overflow counter was nonzero";
    } else if (result.capsule.stream_event_sent_count != result.capsule.stream_event_count ||
               result.capsule.stream_event_sent_count != result.capsule.events.size()) {
      result.ok = false;
      result.error_code = "STREAM_COUNT_MISMATCH";
      result.notes = "streamed capsule word count did not match recorder counters";
    } else if (result.capsule.replay_critical_event_count != replay_required) {
      result.ok = false;
      result.error_code = "CRITICAL_COUNT_MISMATCH";
      result.notes = "replay-critical counter did not match reconstructed capsule events";
    } else if (options.stream_stall_test && result.capsule.stream_stall_count == 0) {
      result.ok = false;
      result.error_code = "STREAM_STALL_NOT_EXERCISED";
      result.notes = "stream stall test did not observe any sink stalls";
    } else if (capture_replay_store &&
               (top.replay_source_capture_overflow ||
                top.replay_source_captured_count != replay_required)) {
      result.ok = false;
      result.error_code = "RTL_CAPTURE_STORE";
      result.notes = "RTL capture store did not retain the replay-critical capsule subset";
    } else if (capture_replay_store) {
      std::ostringstream out;
      out << result.notes << "; rtl capture store retained "
          << static_cast<unsigned>(top.replay_source_captured_count) << "/"
          << replay_required << " replay-critical words for reset-persistent source replay";
      result.notes = out.str();
    }
  }
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
  if (use_replay_consumer) {
    result.replay_consumer_consumed = top.replay_consume_consumed_count;
    result.replay_consumer_error_code = top.replay_consume_error_code;
    result.replay_consumer_ok =
        !top.replay_consume_error &&
        top.replay_consume_all_events &&
        top.replay_consume_consumed_count == result.replay_consumer_expected &&
        ((use_replay_source && top.replay_source_sent_count == result.replay_consumer_expected &&
          !top.replay_source_underflow) ||
         (!use_replay_source && replay_consume_index == result.replay_consumer_expected));
    if (result.ok && !result.replay_consumer_ok) {
      std::ostringstream out;
      out << "hardware replay consumer did not accept full capsule: consumed="
          << result.replay_consumer_consumed << "/" << result.replay_consumer_expected
          << " error_code=" << result.replay_consumer_error_code;
      if (use_replay_source) {
        out << " source_sent=" << static_cast<unsigned>(top.replay_source_sent_count)
            << " source_underflow=" << static_cast<unsigned>(top.replay_source_underflow);
      }
      result.ok = false;
      result.error_code = "RTL_REPLAY_CONSUMER";
      result.notes = out.str();
    } else if (result.ok) {
      std::ostringstream out;
      out << result.notes << "; rtl capsule source streamed "
          << (use_replay_source ? static_cast<unsigned>(top.replay_source_sent_count) : replay_consume_index)
          << "/" << result.replay_consumer_expected << " and replay consumer consumed "
          << result.replay_consumer_consumed << "/" << result.replay_consumer_expected
          << " while driving MMIO/IRQ replay";
      result.notes = out.str();
    }
  }
  if (!options.signature_path.empty()) {
    write_signature_json(
        options.signature_path,
        result.capsule,
        result.cycles_to_failure,
        result.commits_to_failure,
        result.ok,
        result.notes,
        &write_error,
        result.replay_consumer_checked,
        result.replay_consumer_ok,
        result.replay_consumer_expected,
        result.replay_consumer_consumed,
        result.replay_consumer_error_code,
        result.replay_stimulus_source);
  }
  return result;
}
