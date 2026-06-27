`ifndef REPLAYCAPSULE_CONFIG_SVH
`define REPLAYCAPSULE_CONFIG_SVH

localparam int RC_CFG_MINIMAL    = 0;
localparam int RC_CFG_CORE       = 1;
localparam int RC_CFG_HASHED     = 2;
localparam int RC_CFG_DIAGNOSTIC = 3;
localparam int RC_CFG_FULL       = 4;

localparam logic [3:0] RC_CFG_MINIMAL_CAPTURE_MODE    = 4'h1;
localparam logic [3:0] RC_CFG_CORE_CAPTURE_MODE       = 4'h3;
localparam logic [3:0] RC_CFG_HASHED_CAPTURE_MODE     = 4'h3;
localparam logic [3:0] RC_CFG_DIAGNOSTIC_CAPTURE_MODE = 4'h0;
localparam logic [3:0] RC_CFG_FULL_CAPTURE_MODE       = 4'h0;

`endif
