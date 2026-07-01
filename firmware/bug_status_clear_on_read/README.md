# bug_status_clear_on_read

This expanded benchmark models a command or status register whose unsafe request
bit clears after the firmware reads it.

The failing firmware acts on the stale first read even after the second read has
cleared the request. The fixed firmware confirms the status before actuating and
uses a safe actuator value when the second read shows the request is gone.
