# PayloadStatus.msg
std_msgs/Header header

bool system_ready
bool safety_interlock_engaged
uint8 remaining_payloads
string last_drop_timestamp
string drop_status              # IDLE, ARMED, RELEASING, COMPLETED, FAILED
