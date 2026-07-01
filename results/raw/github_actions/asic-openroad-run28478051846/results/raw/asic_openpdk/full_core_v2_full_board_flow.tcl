set rc_status PASS
proc rc_try {label body} {
  global rc_status
  if {[catch {uplevel 1 $body} err]} {
    puts "RC_OPENROAD_ERROR $label $err"
    set rc_status FAIL
  }
}
read_liberty .tools/openpdk/nangate45/NangateOpenCellLibrary_typical.lib
read_lef .tools/openpdk/nangate45/NangateOpenCellLibrary.combined.lef
read_verilog results/raw/asic_openpdk/full_core_v2_full_board_yosys_area_mapped.v
link_design full_core_replaycapsule_v2_board_top
read_sdc constraints/asic_openpdk.sdc
initialize_floorplan -site FreePDK45_38x28_10R_NP_162NW_34O -die_area {0 0 375.972 375.972} -core_area {20.000 20.000 355.972 355.972}
rc_try make_tracks {make_tracks}
rc_try place_pins {place_pins -hor_layer metal3 -ver_layer metal2}
rc_try global_placement {global_placement -density 0.55}
rc_try detailed_placement {detailed_placement}
rc_try estimate_parasitics_placement {estimate_parasitics -placement}
rc_try repair_design {repair_design}
if {[llength [info commands clock_tree_synthesis]] != 0} {
  rc_try clock_tree_synthesis {clock_tree_synthesis -root_buf CLKBUF_X3 -buf_list {CLKBUF_X1 CLKBUF_X2 CLKBUF_X3}}
  rc_try detailed_placement_after_cts {detailed_placement}
} else {
  puts "RC_OPENROAD_WARN clock_tree_synthesis command unavailable"
}
rc_try global_route {global_route}
puts "RC_OPENROAD_WARN detailed_route disabled; using global-routed timing/power evidence"
if {[catch {estimate_parasitics -global_routing} err]} {
  puts "RC_OPENROAD_WARN estimate_parasitics_global $err"
  rc_try estimate_parasitics_placement_final {estimate_parasitics -placement}
}
puts "RC_OPENROAD_METRIC_BEGIN"
report_design_area
report_wns
report_tns
report_checks -path_delay max
report_power
puts "RC_OPENROAD_METRIC_END"
rc_try write_def {write_def results/raw/asic_openpdk/full_core_v2_full_board_openroad.def}
if {[llength [info commands write_db]] != 0} { rc_try write_db {write_db results/raw/asic_openpdk/full_core_v2_full_board_openroad.odb} }
puts "RC_OPENROAD_STATUS $rc_status"
if {$rc_status ne "PASS"} { exit 2 }
