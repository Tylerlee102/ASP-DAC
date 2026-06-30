#pragma once

#include <cstdint>
#include <string>
#include <vector>

struct CapsuleEvent {
  std::string packet_hex;
  uint32_t event_type = 0;
  uint32_t event_id = 0;
  uint32_t commit = 0;
  uint32_t pc = 0;
  uint32_t addr = 0;
  uint32_t data = 0;
  uint32_t payload_hash = 0;
  uint32_t flags = 0;
  uint32_t schema_version = 1;
  bool replay_required = false;
  bool diagnostic_only = false;
};

struct Capsule {
  std::string benchmark;
  std::string variant;
  int seed = 0;
  std::string mode;
  std::string architecture = "v1";
  std::string recorder_config = "legacy";
  uint32_t packet_width_bits = 168;
  uint32_t property_id = 0;
  uint32_t property_signature = 0;
  bool overflow = false;
  uint32_t stream_event_count = 0;
  uint32_t stream_event_sent_count = 0;
  uint32_t replay_critical_event_count = 0;
  uint32_t stream_stall_count = 0;
  uint32_t dropped_diagnostic_count = 0;
  uint32_t replay_critical_overflow_count = 0;
  std::vector<CapsuleEvent> events;
};

std::string packet_hex_from_words(uint32_t word0, uint32_t word1, uint32_t word2,
                                  uint32_t word3, uint32_t word4, uint32_t word5);
std::string packet_hex_from_v2_words(uint32_t word0, uint32_t word1);
uint32_t packet_payload_hash(const std::string& packet_hex);
uint32_t packet_payload_hash(const std::string& packet_hex, const std::string& architecture);
uint32_t v2_payload_hash(uint32_t event_type, uint32_t commit_index, uint32_t addr, uint32_t data, bool enable);
CapsuleEvent decode_packet_hex(const std::string& packet_hex);
CapsuleEvent decode_packet_hex(const std::string& packet_hex, const std::string& architecture);
void apply_v2_commit_deltas(Capsule* capsule);
bool write_capsule_json(const std::string& path, const Capsule& capsule, std::string* error);
bool read_capsule_json(const std::string& path, Capsule* capsule, std::string* error);
bool write_signature_json(const std::string& path, const Capsule& capsule, uint64_t cycles,
                          uint64_t commits, bool replay_ok, const std::string& notes,
                          std::string* error,
                          bool replay_consumer_checked = false,
                          bool replay_consumer_ok = true,
                          uint32_t replay_consumer_expected = 0,
                          uint32_t replay_consumer_consumed = 0,
                          uint32_t replay_consumer_error_code = 0);
