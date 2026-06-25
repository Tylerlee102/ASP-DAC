`ifndef REPLAYCAPSULE_EVENT_PKG_SV
`define REPLAYCAPSULE_EVENT_PKG_SV

package replaycapsule_event_pkg;
  localparam int RC_EVENT_TYPE_W = 4;
  localparam int RC_EVENT_FLAG_W = 4;
  localparam int RC_WORD_W = 32;
  localparam int RC_EVENT_WIDTH = RC_EVENT_TYPE_W + RC_EVENT_FLAG_W + (5 * RC_WORD_W);

  typedef enum logic [RC_EVENT_TYPE_W-1:0] {
    EV_COMMIT          = 4'h0,
    EV_BRANCH          = 4'h1,
    EV_JUMP            = 4'h2,
    EV_STORE           = 4'h3,
    EV_LOAD            = 4'h4,
    EV_MMIO_READ       = 4'h5,
    EV_MMIO_WRITE      = 4'h6,
    EV_INTERRUPT_ENTER = 4'h7,
    EV_INTERRUPT_EXIT  = 4'h8,
    EV_EXTERNAL_INPUT  = 4'h9,
    EV_PROPERTY_FAIL   = 4'ha,
    EV_CHECKPOINT_HASH = 4'hb
  } rc_event_type_e;

  typedef enum logic [3:0] {
    CAPTURE_ALL              = 4'h0,
    CAPTURE_MMIO_INTERRUPT   = 4'h1,
    CAPTURE_PROPERTY_AWARE   = 4'h2,
    CAPTURE_REPLAYCAPSULE_RV = 4'h3
  } rc_capture_mode_e;

  function automatic logic [RC_EVENT_WIDTH-1:0] rc_pack_event(
    input logic [RC_EVENT_TYPE_W-1:0] event_type,
    input logic [RC_EVENT_FLAG_W-1:0] flags,
    input logic [31:0] event_id,
    input logic [31:0] commit_index,
    input logic [31:0] pc,
    input logic [31:0] addr,
    input logic [31:0] data
  );
    rc_pack_event = {event_type, flags, event_id, commit_index, pc, addr, data};
  endfunction

  function automatic logic [RC_EVENT_TYPE_W-1:0] rc_get_type(
    input logic [RC_EVENT_WIDTH-1:0] event_packet
  );
    rc_get_type = event_packet[RC_EVENT_WIDTH-1 -: RC_EVENT_TYPE_W];
  endfunction

  function automatic logic [31:0] rc_get_event_id(
    input logic [RC_EVENT_WIDTH-1:0] event_packet
  );
    rc_get_event_id = event_packet[159:128];
  endfunction

  function automatic logic [31:0] rc_get_commit_index(
    input logic [RC_EVENT_WIDTH-1:0] event_packet
  );
    rc_get_commit_index = event_packet[127:96];
  endfunction

  function automatic logic [31:0] rc_get_pc(
    input logic [RC_EVENT_WIDTH-1:0] event_packet
  );
    rc_get_pc = event_packet[95:64];
  endfunction

  function automatic logic [31:0] rc_get_addr(
    input logic [RC_EVENT_WIDTH-1:0] event_packet
  );
    rc_get_addr = event_packet[63:32];
  endfunction

  function automatic logic [31:0] rc_get_data(
    input logic [RC_EVENT_WIDTH-1:0] event_packet
  );
    rc_get_data = event_packet[31:0];
  endfunction
endpackage

`endif
