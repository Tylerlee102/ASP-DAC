#include "capsule_io.h"

#include <algorithm>
#include <exception>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <regex>
#include <sstream>

namespace {

uint32_t parse_hex_u32(const std::string& text) {
  return static_cast<uint32_t>(std::stoul(text, nullptr, 16));
}

std::string json_escape(const std::string& value) {
  std::ostringstream out;
  for (char ch : value) {
    if (ch == '\\' || ch == '"') {
      out << '\\' << ch;
    } else if (ch == '\n') {
      out << "\\n";
    } else {
      out << ch;
    }
  }
  return out.str();
}

std::string packet_field(const std::string& packet, size_t offset, size_t count) {
  if (packet.size() < offset + count) {
    return std::string(count, '0');
  }
  return packet.substr(offset, count);
}

std::string normalize_packet_hex_width(std::string packet, size_t chars) {
  packet.erase(std::remove(packet.begin(), packet.end(), 'x'), packet.end());
  if (packet.rfind("0", 0) == 0 && packet.size() > chars) {
    packet = packet.substr(packet.size() - chars);
  }
  if (packet.size() < chars) {
    packet = std::string(chars - packet.size(), '0') + packet;
  }
  return packet;
}

std::string normalize_packet_hex(std::string packet) {
  return normalize_packet_hex_width(packet, 42);
}

std::string hex_u32(uint32_t value) {
  std::ostringstream out;
  out << "0x" << std::hex << std::setw(8) << std::setfill('0') << value;
  return out.str();
}

bool replay_required_event(uint32_t event_type) {
  return event_type == 5 || event_type == 6 || event_type == 7 || event_type == 8 || event_type == 10;
}

constexpr uint32_t V2_FLAG_DICT_HIT = 1u << 2;
constexpr uint32_t V2_FLAG_HASH = 1u << 1;
constexpr uint32_t V2_FLAG_DELTA_WIDE = 1u << 3;
constexpr uint32_t V2_DICT_ENTRIES = 8;
constexpr uint32_t V2_MMIO_BASE = 0x40000000u;

}  // namespace

std::string packet_hex_from_words(uint32_t word0, uint32_t word1, uint32_t word2,
                                  uint32_t word3, uint32_t word4, uint32_t word5) {
  std::ostringstream out;
  out << std::hex << std::setfill('0') << std::nouppercase;
  out << std::setw(2) << (word5 & 0xffu);
  out << std::setw(8) << word4;
  out << std::setw(8) << word3;
  out << std::setw(8) << word2;
  out << std::setw(8) << word1;
  out << std::setw(8) << word0;
  return out.str();
}

std::string packet_hex_from_v2_words(uint32_t word0, uint32_t word1) {
  std::ostringstream out;
  out << std::hex << std::setfill('0') << std::nouppercase;
  out << std::setw(8) << word1;
  out << std::setw(8) << word0;
  return out.str();
}

uint32_t packet_payload_hash(const std::string& packet_hex) {
  return packet_payload_hash(packet_hex, "v1");
}

uint32_t packet_payload_hash(const std::string& packet_hex, const std::string& architecture) {
  const std::string packet = normalize_packet_hex_width(packet_hex, architecture == "v2" ? 16 : 42);
  uint32_t hash = 2166136261u;
  for (char ch : packet) {
    hash ^= static_cast<uint8_t>(ch);
    hash *= 16777619u;
  }
  return hash;
}

uint32_t v2_payload_hash(uint32_t event_type, uint32_t commit_index, uint32_t addr, uint32_t data, bool enable) {
  if (!enable) return data;
  uint32_t mixed = data ^ ((event_type & 0xfu) * 0x11111111u);
  mixed ^= ((commit_index & 0xffffu) << 16) | ((commit_index >> 16) & 0xffffu);
  mixed ^= ((addr & 0xffu) << 24) | ((addr >> 8) & 0x00ffffffu);
  return (mixed << 5) ^ (mixed >> 2) ^ 0x9e3779b9u;
}

CapsuleEvent decode_packet_hex(const std::string& packet_hex) {
  return decode_packet_hex(packet_hex, "v1");
}

CapsuleEvent decode_packet_hex(const std::string& packet_hex, const std::string& architecture) {
  if (architecture == "v2") {
    std::string packet = normalize_packet_hex_width(packet_hex, 16);
    CapsuleEvent event;
    event.packet_hex = packet;
    event.event_type = parse_hex_u32(packet_field(packet, 0, 1));
    const uint32_t flags = parse_hex_u32(packet_field(packet, 1, 1));
    const uint32_t commit_delta = parse_hex_u32(packet_field(packet, 2, 2));
    const uint32_t address_token = parse_hex_u32(packet_field(packet, 4, 2));
    const uint32_t payload = parse_hex_u32(packet_field(packet, 6, 8));
    const uint32_t debug_context = parse_hex_u32(packet_field(packet, 14, 2));
    event.schema_version = 2;
    event.event_id = 0;
    event.flags = flags;
    event.commit = commit_delta;
    event.pc = 0;
    event.addr = address_token;
    event.data = payload;
    if (event.event_type == 5 || event.event_type == 6) {
      event.addr = 0x40000000u | address_token;
    } else if (event.event_type == 10) {
      event.addr = address_token;
    }
    event.payload_hash = v2_payload_hash(event.event_type, event.commit, event.addr, event.data, (flags & V2_FLAG_HASH) != 0u);
    event.replay_required = replay_required_event(event.event_type);
    event.diagnostic_only = !event.replay_required;
    return event;
  }

  std::string packet = normalize_packet_hex(packet_hex);
  CapsuleEvent event;
  event.schema_version = 1;
  event.packet_hex = packet;
  event.event_type = parse_hex_u32(packet_field(packet, 0, 1));
  event.event_id = parse_hex_u32(packet_field(packet, 2, 8));
  event.commit = parse_hex_u32(packet_field(packet, 10, 8));
  event.pc = parse_hex_u32(packet_field(packet, 18, 8));
  event.addr = parse_hex_u32(packet_field(packet, 26, 8));
  event.data = parse_hex_u32(packet_field(packet, 34, 8));
  event.payload_hash = packet_payload_hash(packet);
  event.replay_required = replay_required_event(event.event_type);
  event.diagnostic_only = !event.replay_required;
  return event;
}

void apply_v2_commit_deltas(Capsule* capsule) {
  if (!capsule || capsule->architecture != "v2") return;
  uint32_t commit = 0;
  uint32_t dict[V2_DICT_ENTRIES] = {};
  bool dict_valid[V2_DICT_ENTRIES] = {};
  uint32_t write_ptr = 0;
  for (size_t i = 0; i < capsule->events.size(); ++i) {
    const std::string packet = normalize_packet_hex_width(capsule->events[i].packet_hex, 16);
    const uint32_t flags = parse_hex_u32(packet_field(packet, 1, 1));
    const uint32_t commit_delta_low = parse_hex_u32(packet_field(packet, 2, 2));
    const uint32_t address_token = parse_hex_u32(packet_field(packet, 4, 2));
    const uint32_t debug_context = parse_hex_u32(packet_field(packet, 14, 2));
    const uint32_t commit_delta = ((flags & V2_FLAG_DELTA_WIDE) != 0u)
        ? ((debug_context << 8) | commit_delta_low)
        : commit_delta_low;
    commit += commit_delta;
    capsule->events[i].schema_version = 2;
    capsule->events[i].flags = flags;
    capsule->events[i].commit = commit;
    capsule->events[i].event_id = static_cast<uint32_t>(i);
    if (capsule->events[i].event_type == 5 || capsule->events[i].event_type == 6) {
      if ((flags & V2_FLAG_DICT_HIT) != 0u && address_token < V2_DICT_ENTRIES && dict_valid[address_token]) {
        capsule->events[i].addr = dict[address_token];
      } else {
        capsule->events[i].addr = V2_MMIO_BASE | address_token;
        bool hit = false;
        for (uint32_t j = 0; j < V2_DICT_ENTRIES; ++j) {
          if (dict_valid[j] && dict[j] == capsule->events[i].addr) {
            hit = true;
            break;
          }
        }
        if (!hit) {
          dict[write_ptr] = capsule->events[i].addr;
          dict_valid[write_ptr] = true;
          write_ptr = (write_ptr + 1u) % V2_DICT_ENTRIES;
        }
      }
    }
    capsule->events[i].payload_hash = v2_payload_hash(
        capsule->events[i].event_type,
        capsule->events[i].commit,
        capsule->events[i].addr,
        capsule->events[i].data,
        (flags & V2_FLAG_HASH) != 0u);
  }
}

bool write_capsule_json(const std::string& path, const Capsule& capsule, std::string* error) {
  try {
    std::filesystem::create_directories(std::filesystem::path(path).parent_path());
    std::ofstream out(path);
    out << "{\n";
    out << "  \"benchmark\": \"" << json_escape(capsule.benchmark) << "\",\n";
    out << "  \"variant\": \"" << json_escape(capsule.variant) << "\",\n";
    out << "  \"seed\": " << capsule.seed << ",\n";
    out << "  \"mode\": \"" << json_escape(capsule.mode) << "\",\n";
    out << "  \"architecture\": \"" << json_escape(capsule.architecture) << "\",\n";
    out << "  \"schema_version\": " << (capsule.architecture == "v2" ? 2 : 1) << ",\n";
    out << "  \"recorder_config\": \"" << json_escape(capsule.recorder_config) << "\",\n";
    out << "  \"packet_width_bits\": " << capsule.packet_width_bits << ",\n";
    out << "  \"property_id\": " << capsule.property_id << ",\n";
    out << "  \"property_signature\": \"0x" << std::hex << std::setw(8) << std::setfill('0')
        << capsule.property_signature << std::dec << "\",\n";
    out << "  \"overflow\": " << (capsule.overflow ? "true" : "false") << ",\n";
    out << "  \"stream_event_count\": " << capsule.stream_event_count << ",\n";
    out << "  \"stream_event_sent_count\": " << capsule.stream_event_sent_count << ",\n";
    out << "  \"replay_critical_event_count\": " << capsule.replay_critical_event_count << ",\n";
    out << "  \"stream_stall_count\": " << capsule.stream_stall_count << ",\n";
    out << "  \"dropped_diagnostic_count\": " << capsule.dropped_diagnostic_count << ",\n";
    out << "  \"replay_critical_overflow_count\": " << capsule.replay_critical_overflow_count << ",\n";
    out << "  \"events\": [\n";
    for (size_t i = 0; i < capsule.events.size(); ++i) {
      const auto& event = capsule.events[i];
      out << "    {\"index\": " << i
          << ", \"cycle\": null"
          << ", \"packet\": \"" << event.packet_hex
          << "\", \"schema_version\": " << event.schema_version
          << ", \"flags\": " << event.flags
          << ", \"flags_hex\": \"" << hex_u32(event.flags)
          << "\", \"event_type\": " << event.event_type
          << ", \"event_id\": " << event.event_id
          << ", \"commit\": " << event.commit
          << ", \"commit_index\": " << event.commit
          << ", \"pc\": \"" << hex_u32(event.pc)
          << "\", \"addr\": \"" << hex_u32(event.addr)
          << "\", \"data\": \"" << hex_u32(event.data)
          << "\", \"mmio_address\": \"" << hex_u32(event.addr)
          << "\", \"mmio_value\": \"" << hex_u32(event.data)
          << "\", \"raw_mmio_value\": \"" << hex_u32((event.event_type == 5 || event.event_type == 6) ? event.data : 0)
          << "\", \"interrupt_cause\": " << (event.event_type == 7 || event.event_type == 8 ? event.data : 0)
          << ", \"interrupt_pending\": " << (event.event_type == 7 ? "true" : "false")
          << ", \"interrupt_taken\": " << (event.event_type == 7 ? "true" : "false")
          << ", \"interrupt_pending_or_taken\": " << (event.event_type == 7 || event.event_type == 8 ? "true" : "false")
          << ", \"property_id\": " << (event.event_type == 10 ? event.addr & 0xffu : capsule.property_id)
          << ", \"payload_hash\": \"" << hex_u32(event.payload_hash)
          << "\", \"replay_required\": " << (event.replay_required ? "true" : "false")
          << ", \"diagnostic_only\": " << (event.diagnostic_only ? "true" : "false")
          << ", \"source\": \"" << json_escape(capsule.mode)
          << "\", \"notes\": \"" << (event.replay_required ? "replay-critical" : "diagnostic/context")
          << "\"}";
      out << (i + 1 == capsule.events.size() ? "\n" : ",\n");
    }
    out << "  ]\n";
    out << "}\n";
    return true;
  } catch (const std::exception& exc) {
    if (error) *error = exc.what();
    return false;
  }
}

bool read_capsule_json(const std::string& path, Capsule* capsule, std::string* error) {
  try {
    std::ifstream in(path);
    if (!in) {
      if (error) *error = "could not open capsule";
      return false;
    }
    std::stringstream buffer;
    buffer << in.rdbuf();
    const std::string text = buffer.str();
    std::smatch match;
    if (std::regex_search(text, match, std::regex("\"benchmark\"\\s*:\\s*\"([^\"]*)\""))) capsule->benchmark = match[1];
    if (std::regex_search(text, match, std::regex("\"variant\"\\s*:\\s*\"([^\"]*)\""))) capsule->variant = match[1];
    if (std::regex_search(text, match, std::regex("\"seed\"\\s*:\\s*(\\d+)"))) capsule->seed = std::stoi(match[1]);
    if (std::regex_search(text, match, std::regex("\"mode\"\\s*:\\s*\"([^\"]*)\""))) capsule->mode = match[1];
    if (std::regex_search(text, match, std::regex("\"architecture\"\\s*:\\s*\"([^\"]*)\""))) capsule->architecture = match[1];
    if (std::regex_search(text, match, std::regex("\"recorder_config\"\\s*:\\s*\"([^\"]*)\""))) capsule->recorder_config = match[1];
    if (std::regex_search(text, match, std::regex("\"packet_width_bits\"\\s*:\\s*(\\d+)"))) capsule->packet_width_bits = std::stoul(match[1]);
    const std::regex property_id_re("\"property_id\"\\s*:\\s*(\\d+)");
    for (auto it = std::sregex_iterator(text.begin(), text.end(), property_id_re); it != std::sregex_iterator(); ++it) {
      capsule->property_id = std::stoul((*it)[1]);
    }
    if (std::regex_search(text, match, std::regex("\"property_signature\"\\s*:\\s*\"0x([0-9a-fA-F]+)\""))) {
      capsule->property_signature = parse_hex_u32(match[1]);
    }
    capsule->overflow = std::regex_search(text, std::regex("\"overflow\"\\s*:\\s*true"));
    if (std::regex_search(text, match, std::regex("\"stream_event_count\"\\s*:\\s*(\\d+)"))) capsule->stream_event_count = std::stoul(match[1]);
    if (std::regex_search(text, match, std::regex("\"stream_event_sent_count\"\\s*:\\s*(\\d+)"))) capsule->stream_event_sent_count = std::stoul(match[1]);
    if (std::regex_search(text, match, std::regex("\"replay_critical_event_count\"\\s*:\\s*(\\d+)"))) capsule->replay_critical_event_count = std::stoul(match[1]);
    if (std::regex_search(text, match, std::regex("\"stream_stall_count\"\\s*:\\s*(\\d+)"))) capsule->stream_stall_count = std::stoul(match[1]);
    if (std::regex_search(text, match, std::regex("\"dropped_diagnostic_count\"\\s*:\\s*(\\d+)"))) capsule->dropped_diagnostic_count = std::stoul(match[1]);
    if (std::regex_search(text, match, std::regex("\"replay_critical_overflow_count\"\\s*:\\s*(\\d+)"))) capsule->replay_critical_overflow_count = std::stoul(match[1]);
    capsule->events.clear();
    std::vector<uint32_t> expected_hashes;
    std::vector<bool> has_expected_hash;
    const std::regex event_re("\\{[^\\{\\}]*\"packet\"\\s*:\\s*\"([0-9a-fA-F]+)\"[^\\{\\}]*\\}");
    size_t index = 0;
    for (auto it = std::sregex_iterator(text.begin(), text.end(), event_re); it != std::sregex_iterator(); ++it, ++index) {
      const std::string object = (*it).str();
      CapsuleEvent event = decode_packet_hex((*it)[1], capsule->architecture);
      bool found_hash = false;
      uint32_t expected_hash = 0;
      if (std::regex_search(object, match, std::regex("\"payload_hash\"\\s*:\\s*\"?0x?([0-9a-fA-F]+)\"?"))) {
        found_hash = true;
        expected_hash = parse_hex_u32(match[1]);
      }
      capsule->events.push_back(event);
      expected_hashes.push_back(expected_hash);
      has_expected_hash.push_back(found_hash);
    }
    apply_v2_commit_deltas(capsule);
    for (size_t i = 0; i < capsule->events.size(); ++i) {
      if (has_expected_hash[i] && expected_hashes[i] != capsule->events[i].payload_hash) {
        if (error) {
          std::ostringstream out;
          out << "payload hash mismatch at event index " << i;
          *error = out.str();
        }
        return false;
      }
    }
    return true;
  } catch (const std::exception& exc) {
    if (error) *error = exc.what();
    return false;
  }
}

bool write_signature_json(const std::string& path, const Capsule& capsule, uint64_t cycles,
                          uint64_t commits, bool replay_ok, const std::string& notes,
                          std::string* error,
                          bool replay_consumer_checked,
                          bool replay_consumer_ok,
                          uint32_t replay_consumer_expected,
                          uint32_t replay_consumer_consumed,
                          uint32_t replay_consumer_error_code) {
  try {
    std::filesystem::create_directories(std::filesystem::path(path).parent_path());
    std::ofstream out(path);
    out << "{\n";
    out << "  \"benchmark\": \"" << json_escape(capsule.benchmark) << "\",\n";
    out << "  \"variant\": \"" << json_escape(capsule.variant) << "\",\n";
    out << "  \"seed\": " << capsule.seed << ",\n";
    out << "  \"mode\": \"" << json_escape(capsule.mode) << "\",\n";
    out << "  \"architecture\": \"" << json_escape(capsule.architecture) << "\",\n";
    out << "  \"recorder_config\": \"" << json_escape(capsule.recorder_config) << "\",\n";
    out << "  \"packet_width_bits\": " << capsule.packet_width_bits << ",\n";
    out << "  \"property_id\": " << capsule.property_id << ",\n";
    out << "  \"property_signature\": \"0x" << std::hex << std::setw(8) << std::setfill('0')
        << capsule.property_signature << std::dec << "\",\n";
    out << "  \"cycles_to_failure\": " << cycles << ",\n";
    out << "  \"commits_to_failure\": " << commits << ",\n";
    out << "  \"event_count\": " << capsule.events.size() << ",\n";
    out << "  \"capsule_bytes\": " << capsule.events.size() * ((capsule.packet_width_bits + 7) / 8) << ",\n";
    out << "  \"overflow\": " << (capsule.overflow ? "true" : "false") << ",\n";
    out << "  \"stream_event_count\": " << capsule.stream_event_count << ",\n";
    out << "  \"stream_event_sent_count\": " << capsule.stream_event_sent_count << ",\n";
    out << "  \"replay_critical_event_count\": " << capsule.replay_critical_event_count << ",\n";
    out << "  \"stream_stall_count\": " << capsule.stream_stall_count << ",\n";
    out << "  \"dropped_diagnostic_count\": " << capsule.dropped_diagnostic_count << ",\n";
    out << "  \"replay_critical_overflow_count\": " << capsule.replay_critical_overflow_count << ",\n";
    out << "  \"replay_ok\": " << (replay_ok ? "true" : "false") << ",\n";
    out << "  \"replay_consumer_checked\": " << (replay_consumer_checked ? "true" : "false") << ",\n";
    out << "  \"replay_consumer_ok\": " << (replay_consumer_ok ? "true" : "false") << ",\n";
    out << "  \"replay_consumer_expected\": " << replay_consumer_expected << ",\n";
    out << "  \"replay_consumer_consumed\": " << replay_consumer_consumed << ",\n";
    out << "  \"replay_consumer_error_code\": " << replay_consumer_error_code << ",\n";
    out << "  \"notes\": \"" << json_escape(notes) << "\"\n";
    out << "}\n";
    return true;
  } catch (const std::exception& exc) {
    if (error) *error = exc.what();
    return false;
  }
}
