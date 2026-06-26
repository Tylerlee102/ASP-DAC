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

std::string normalize_packet_hex(std::string packet) {
  packet.erase(std::remove(packet.begin(), packet.end(), 'x'), packet.end());
  if (packet.rfind("0", 0) == 0 && packet.size() > 42) {
    packet = packet.substr(packet.size() - 42);
  }
  if (packet.size() < 42) {
    packet = std::string(42 - packet.size(), '0') + packet;
  }
  return packet;
}

std::string hex_u32(uint32_t value) {
  std::ostringstream out;
  out << "0x" << std::hex << std::setw(8) << std::setfill('0') << value;
  return out.str();
}

bool replay_required_event(uint32_t event_type) {
  return event_type == 5 || event_type == 6 || event_type == 7 || event_type == 8 || event_type == 10;
}

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

uint32_t packet_payload_hash(const std::string& packet_hex) {
  const std::string packet = normalize_packet_hex(packet_hex);
  uint32_t hash = 2166136261u;
  for (char ch : packet) {
    hash ^= static_cast<uint8_t>(ch);
    hash *= 16777619u;
  }
  return hash;
}

CapsuleEvent decode_packet_hex(const std::string& packet_hex) {
  std::string packet = normalize_packet_hex(packet_hex);
  CapsuleEvent event;
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

bool write_capsule_json(const std::string& path, const Capsule& capsule, std::string* error) {
  try {
    std::filesystem::create_directories(std::filesystem::path(path).parent_path());
    std::ofstream out(path);
    out << "{\n";
    out << "  \"benchmark\": \"" << json_escape(capsule.benchmark) << "\",\n";
    out << "  \"variant\": \"" << json_escape(capsule.variant) << "\",\n";
    out << "  \"seed\": " << capsule.seed << ",\n";
    out << "  \"mode\": \"" << json_escape(capsule.mode) << "\",\n";
    out << "  \"property_id\": " << capsule.property_id << ",\n";
    out << "  \"property_signature\": \"0x" << std::hex << std::setw(8) << std::setfill('0')
        << capsule.property_signature << std::dec << "\",\n";
    out << "  \"overflow\": " << (capsule.overflow ? "true" : "false") << ",\n";
    out << "  \"events\": [\n";
    for (size_t i = 0; i < capsule.events.size(); ++i) {
      const auto& event = capsule.events[i];
      out << "    {\"index\": " << i
          << ", \"cycle\": null"
          << ", \"packet\": \"" << event.packet_hex
          << "\", \"event_type\": " << event.event_type
          << ", \"event_id\": " << event.event_id
          << ", \"commit\": " << event.commit
          << ", \"commit_index\": " << event.commit
          << ", \"pc\": \"" << hex_u32(event.pc)
          << "\", \"addr\": \"" << hex_u32(event.addr)
          << "\", \"data\": \"" << hex_u32(event.data)
          << "\", \"mmio_address\": \"" << hex_u32(event.addr)
          << "\", \"mmio_value\": \"" << hex_u32(event.data)
          << "\", \"interrupt_cause\": " << (event.event_type == 7 || event.event_type == 8 ? event.data : 0)
          << ", \"interrupt_pending\": " << (event.event_type == 7 ? "true" : "false")
          << ", \"interrupt_taken\": " << (event.event_type == 7 ? "true" : "false")
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
    const std::regex property_id_re("\"property_id\"\\s*:\\s*(\\d+)");
    for (auto it = std::sregex_iterator(text.begin(), text.end(), property_id_re); it != std::sregex_iterator(); ++it) {
      capsule->property_id = std::stoul((*it)[1]);
    }
    if (std::regex_search(text, match, std::regex("\"property_signature\"\\s*:\\s*\"0x([0-9a-fA-F]+)\""))) {
      capsule->property_signature = parse_hex_u32(match[1]);
    }
    capsule->overflow = std::regex_search(text, std::regex("\"overflow\"\\s*:\\s*true"));
    capsule->events.clear();
    const std::regex event_re("\\{[^\\{\\}]*\"packet\"\\s*:\\s*\"([0-9a-fA-F]+)\"[^\\{\\}]*\\}");
    size_t index = 0;
    for (auto it = std::sregex_iterator(text.begin(), text.end(), event_re); it != std::sregex_iterator(); ++it, ++index) {
      const std::string object = (*it).str();
      CapsuleEvent event = decode_packet_hex((*it)[1]);
      if (std::regex_search(object, match, std::regex("\"payload_hash\"\\s*:\\s*\"?0x?([0-9a-fA-F]+)\"?"))) {
        const uint32_t expected_hash = parse_hex_u32(match[1]);
        if (expected_hash != event.payload_hash) {
          if (error) {
            std::ostringstream out;
            out << "payload hash mismatch at event index " << index;
            *error = out.str();
          }
          return false;
        }
      }
      capsule->events.push_back(event);
    }
    return true;
  } catch (const std::exception& exc) {
    if (error) *error = exc.what();
    return false;
  }
}

bool write_signature_json(const std::string& path, const Capsule& capsule, uint64_t cycles,
                          uint64_t commits, bool replay_ok, const std::string& notes,
                          std::string* error) {
  try {
    std::filesystem::create_directories(std::filesystem::path(path).parent_path());
    std::ofstream out(path);
    out << "{\n";
    out << "  \"benchmark\": \"" << json_escape(capsule.benchmark) << "\",\n";
    out << "  \"variant\": \"" << json_escape(capsule.variant) << "\",\n";
    out << "  \"seed\": " << capsule.seed << ",\n";
    out << "  \"mode\": \"" << json_escape(capsule.mode) << "\",\n";
    out << "  \"property_id\": " << capsule.property_id << ",\n";
    out << "  \"property_signature\": \"0x" << std::hex << std::setw(8) << std::setfill('0')
        << capsule.property_signature << std::dec << "\",\n";
    out << "  \"cycles_to_failure\": " << cycles << ",\n";
    out << "  \"commits_to_failure\": " << commits << ",\n";
    out << "  \"event_count\": " << capsule.events.size() << ",\n";
    out << "  \"capsule_bytes\": " << capsule.events.size() * 21 << ",\n";
    out << "  \"overflow\": " << (capsule.overflow ? "true" : "false") << ",\n";
    out << "  \"replay_ok\": " << (replay_ok ? "true" : "false") << ",\n";
    out << "  \"notes\": \"" << json_escape(notes) << "\"\n";
    out << "}\n";
    return true;
  } catch (const std::exception& exc) {
    if (error) *error = exc.what();
    return false;
  }
}
