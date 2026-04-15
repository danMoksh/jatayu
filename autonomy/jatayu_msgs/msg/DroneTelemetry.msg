# DroneTelemetry.msg
std_msgs/Header header

float64 latitude
float64 longitude
float32 altitude_msl
float32 altitude_relative
float32 heading
float32 ground_speed
float32 air_speed
float32 climb_rate
float32 battery_percentage
float32 battery_voltage

string flight_mode
string vtol_state          # MC, TRANSITION_TO_FW, FW, TRANSITION_TO_MC
bool armed
bool gps_healthy
uint8 satellites_visible
