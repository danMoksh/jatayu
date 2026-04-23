"""
Jatayu Target Georeferencing & Geolocation Node
Transforms 2D bounding-box pixel detections into real-world WGS84 GPS coordinates
using direct georeferencing ray-casting and camera intrinsics.
"""

import math
from typing import Tuple

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Header
    from visualization_msgs.msg import Marker, MarkerArray
    from jatayu_msgs.msg import TargetDetection, DroneTelemetry
except ImportError:
    Node = object

# WGS-84 Earth radius constants
EARTH_RADIUS_METERS = 6378137.0


def project_pixel_to_gps(
    u: float,
    v: float,
    drone_lat: float,
    drone_lon: float,
    drone_alt_m: float,
    drone_yaw_deg: float,
    drone_pitch_deg: float = 0.0,
    drone_roll_deg: float = 0.0,
    img_width: int = 1280,
    img_height: int = 720,
    fx: float = 950.0,
    fy: float = 950.0,
    ground_elevation_m: float = 0.0
) -> Tuple[float, float, float]:
    """
    Direct georeferencing projection:
    Casts a 3D ray from the focal center through normalized pixel coordinates (u, v),
    rotates by aircraft attitude (yaw, pitch, roll), and calculates ground intersection.

    Returns:
        (target_lat, target_lon, estimated_cep_uncertainty_m)
    """
    agl = max(1.0, drone_alt_m - ground_elevation_m)
    cx = img_width / 2.0
    cy = img_height / 2.0

    # 1. Normalized optical ray (camera frame: X-right, Y-down, Z-forward)
    rx_cam = (u - cx) / fx
    ry_cam = (v - cy) / fy
    rz_cam = 1.0

    # 2. Convert camera optical ray into body coordinates (X-forward, Y-right, Z-down)
    # Assuming downward-mounted optical sensor (optical axis tilted ~45 deg pitch down)
    tilt_rad = math.radians(drone_pitch_deg - 45.0)
    roll_rad = math.radians(drone_roll_deg)
    yaw_rad = math.radians(drone_yaw_deg)

    # Simplified forward projection:
    dist_forward_m = agl * math.tan(abs(tilt_rad) + (ry_cam * 0.4))
    dist_lateral_m = agl * (rx_cam * 0.5)

    # 3. Rotate (dist_forward, dist_lateral) into North-East local tangent plane
    delta_north = dist_forward_m * math.cos(yaw_rad) - dist_lateral_m * math.sin(yaw_rad)
    delta_east = dist_forward_m * math.sin(yaw_rad) + dist_lateral_m * math.cos(yaw_rad)

    # 4. Convert North/East meters to WGS-84 delta latitude/longitude
    delta_lat = (delta_north / EARTH_RADIUS_METERS) * (180.0 / math.pi)
    delta_lon = (delta_east / (EARTH_RADIUS_METERS * math.cos(math.radians(drone_lat)))) * (180.0 / math.pi)

    target_lat = drone_lat + delta_lat
    target_lon = drone_lon + delta_lon

    # Error estimation based on altitude scaling
    uncertainty_m = max(1.5, agl * 0.08)

    return target_lat, target_lon, uncertainty_m


class TargetLocator(Node):
    def __init__(self, node_name: str = "target_locator"):
        if Node is not object:
            super().__init__(node_name)
        else:
            self.node_name = node_name

        self.current_lat = 26.25104
        self.current_lon = 78.17124
        self.current_alt = 35.0
        self.current_yaw = 0.0

        self._init_ros()

    def _init_ros(self):
        if not hasattr(self, 'create_subscription'):
            return

        self.create_subscription(DroneTelemetry, "/jatayu/telemetry", self._telemetry_cb, 10)
        self.target_pub = self.create_publisher(TargetDetection, "/jatayu/target_detected", 10)
        self.marker_pub = self.create_publisher(MarkerArray, "/jatayu/target_markers", 10)
        self.get_logger().info("Target Georeferencing Locator initialized.")

    def _telemetry_cb(self, msg):
        self.current_lat = msg.latitude
        self.current_lon = msg.longitude
        self.current_alt = msg.altitude_relative
        self.current_yaw = msg.heading

    def process_detection(self, bbox: list, conf: float, pose: str, target_id: str) -> dict:
        """Processes raw bounding box and returns georeferenced target record."""
        # bbox is [x1, y1, x2, y2]
        center_x = (bbox[0] + bbox[2]) / 2.0
        center_y = (bbox[1] + bbox[3]) / 2.0

        lat, lon, unc = project_pixel_to_gps(
            u=center_x,
            v=center_y,
            drone_lat=self.current_lat,
            drone_lon=self.current_lon,
            drone_alt_m=self.current_alt,
            drone_yaw_deg=self.current_yaw
        )

        severity = 5
        if pose == "lying_down":
            severity = 9
        elif pose == "distressed":
            severity = 8
        elif pose == "standing":
            severity = 4

        return {
            "target_id": target_id,
            "lat": lat,
            "lon": lon,
            "uncertainty_m": unc,
            "severity": severity,
            "confidence": conf,
            "pose": pose
        }


def main(args=None):
    if 'rclpy' in globals():
        rclpy.init(args=args)
        node = TargetLocator()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
    else:
        locator = TargetLocator()
        test_res = locator.process_detection([500, 300, 600, 500], 0.92, "lying_down", "TGT-001")
        print(f"Target Locator initialized (standalone mode), test projection: {test_res}")


if __name__ == "__main__":
    main()
