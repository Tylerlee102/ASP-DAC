localparam int RCV2_CFG_MINIMAL    = 0;
localparam int RCV2_CFG_CORE       = 1;
localparam int RCV2_CFG_HASHED     = 2;
localparam int RCV2_CFG_DIAGNOSTIC = 3;
localparam int RCV2_CFG_FULL       = 4;

localparam int RCV2_WORD_WIDTH = 64;

localparam logic [7:0] RCV2_ERR_NONE               = 8'd0;
localparam logic [7:0] RCV2_ERR_MISSING_EVENT      = 8'd1;
localparam logic [7:0] RCV2_ERR_DUPLICATE_EVENT    = 8'd2;
localparam logic [7:0] RCV2_ERR_REORDERED_EVENT    = 8'd3;
localparam logic [7:0] RCV2_ERR_WRONG_MMIO_VALUE   = 8'd4;
localparam logic [7:0] RCV2_ERR_WRONG_IRQ_CAUSE    = 8'd5;
localparam logic [7:0] RCV2_ERR_WRONG_PAYLOAD_HASH = 8'd6;
localparam logic [7:0] RCV2_ERR_TRUNCATED_CAPSULE  = 8'd7;

localparam int RCV2_FLAG_DIAGNOSTIC = 0;
localparam int RCV2_FLAG_HASH       = 1;
localparam int RCV2_FLAG_DICT_HIT   = 2;
localparam int RCV2_FLAG_DELTA_WIDE = 3;

function automatic logic [3:0] rcv2_capture_mode_for_config(input int cfg);
  begin
    case (cfg)
      RCV2_CFG_MINIMAL:    rcv2_capture_mode_for_config = 4'h1;
      RCV2_CFG_CORE:       rcv2_capture_mode_for_config = 4'h3;
      RCV2_CFG_HASHED:     rcv2_capture_mode_for_config = 4'h3;
      RCV2_CFG_DIAGNOSTIC: rcv2_capture_mode_for_config = 4'h0;
      RCV2_CFG_FULL:       rcv2_capture_mode_for_config = 4'h0;
      default:             rcv2_capture_mode_for_config = 4'h3;
    endcase
  end
endfunction

function automatic logic rcv2_config_has_hash(input int cfg);
  begin
    rcv2_config_has_hash = (cfg == RCV2_CFG_HASHED) || (cfg == RCV2_CFG_DIAGNOSTIC) || (cfg == RCV2_CFG_FULL);
  end
endfunction

function automatic logic rcv2_config_has_diagnostics(input int cfg);
  begin
    rcv2_config_has_diagnostics = (cfg == RCV2_CFG_DIAGNOSTIC) || (cfg == RCV2_CFG_FULL);
  end
endfunction

function automatic logic [3:0] rcv2_word_type(input logic [RCV2_WORD_WIDTH-1:0] word);
  begin
    rcv2_word_type = word[63:60];
  end
endfunction

function automatic logic [3:0] rcv2_word_flags(input logic [RCV2_WORD_WIDTH-1:0] word);
  begin
    rcv2_word_flags = word[59:56];
  end
endfunction

function automatic logic [7:0] rcv2_word_delta(input logic [RCV2_WORD_WIDTH-1:0] word);
  begin
    rcv2_word_delta = word[55:48];
  end
endfunction

function automatic logic [7:0] rcv2_word_addr_token(input logic [RCV2_WORD_WIDTH-1:0] word);
  begin
    rcv2_word_addr_token = word[47:40];
  end
endfunction

function automatic logic [31:0] rcv2_word_payload(input logic [RCV2_WORD_WIDTH-1:0] word);
  begin
    rcv2_word_payload = word[39:8];
  end
endfunction

function automatic logic [7:0] rcv2_word_debug(input logic [RCV2_WORD_WIDTH-1:0] word);
  begin
    rcv2_word_debug = word[7:0];
  end
endfunction
