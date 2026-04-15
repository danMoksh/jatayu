# TargetDetection.msg
std_msgs/Header header

string target_id
string track_id
float32 confidence
string pose_classification      # standing, lying_down, distressed, unknown
uint8 severity_index            # 1 (low) to 10 (critical)

# Bounding box in normalized image coordinates [x1, y1, x2, y2]
float32[4] bbox

# Georeferenced WGS84 coordinates calculated via direct projection
float64 estimated_lat
float64 estimated_lon
float32 position_uncertainty_m
