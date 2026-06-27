#include "rtl_harness.h"

#include <iostream>
#include <string>

double sc_time_stamp() { return 0.0; }

namespace {

bool require_value(int* index, int argc, char** argv, std::string* value) {
  if (*index + 1 >= argc) return false;
  *value = argv[++(*index)];
  return true;
}

bool parse_args(int argc, char** argv, HarnessOptions* options) {
  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    std::string value;
    if (arg == "--mode" && require_value(&i, argc, argv, &value)) {
      options->mode = value;
    } else if (arg == "--benchmark" && require_value(&i, argc, argv, &value)) {
      options->benchmark = value;
    } else if (arg == "--variant" && require_value(&i, argc, argv, &value)) {
      options->variant = value;
    } else if (arg == "--firmware" && require_value(&i, argc, argv, &value)) {
      options->firmware = value;
    } else if (arg == "--capsule" && require_value(&i, argc, argv, &value)) {
      options->capsule_path = value;
    } else if (arg == "--signature" && require_value(&i, argc, argv, &value)) {
      options->signature_path = value;
    } else if (arg == "--seed" && require_value(&i, argc, argv, &value)) {
      options->seed = std::stoi(value);
    } else if (arg == "--max-cycles" && require_value(&i, argc, argv, &value)) {
      options->max_cycles = std::stoull(value);
    } else if (arg == "--debug-events") {
      options->debug_events = true;
    } else if (arg == "--dump-mmio") {
      options->dump_mmio = true;
    } else if (arg == "--dump-property") {
      options->dump_property = true;
    } else if (arg == "--dump-pc") {
      options->dump_pc = true;
    } else if (arg == "--dump-disasm-context") {
      options->dump_disasm_context = true;
    } else if (arg == "--debug-dir" && require_value(&i, argc, argv, &value)) {
      options->debug_dir = value;
    } else {
      std::cerr << "unknown or incomplete argument: " << arg << "\n";
      return false;
    }
  }
  return !options->benchmark.empty() && !options->variant.empty() && !options->firmware.empty() &&
         !options->capsule_path.empty() && !options->signature_path.empty() &&
         (options->mode == "record" || options->mode == "replay");
}

void usage(const char* argv0) {
  std::cerr
      << "usage: " << argv0 << " --mode record|replay --benchmark NAME --variant NAME\n"
      << "  --firmware firmware/build/<benchmark>/<variant>.hex\n"
      << "  --capsule results/raw/rtl_capsules/<name>.json\n"
      << "  --signature results/raw/rtl_signatures/<name>.json\n"
      << "  [--seed N] [--max-cycles N] [--debug-events]\n"
      << "  [--dump-mmio] [--dump-property] [--dump-pc] [--dump-disasm-context]\n"
      << "  [--debug-dir DIR]\n";
}

}  // namespace

int main(int argc, char** argv) {
  HarnessOptions options;
  if (!parse_args(argc, argv, &options)) {
    usage(argv[0]);
    return 2;
  }

  HarnessResult result = run_harness(options);
  std::cout << (result.ok ? "PASS" : "FAIL") << " " << options.mode
            << " benchmark=" << options.benchmark
            << " variant=" << options.variant
            << " seed=" << options.seed
            << " property=" << static_cast<unsigned>(result.capsule.property_id)
            << " events=" << result.capsule.events.size()
            << " cycles=" << result.cycles_to_failure
            << " commits=" << result.commits_to_failure
            << " notes=\"" << result.notes << "\"\n";
  if (!result.ok && !result.error_code.empty()) {
    std::cerr << "error_code=" << result.error_code << "\n";
  }
  return result.ok ? 0 : 1;
}
