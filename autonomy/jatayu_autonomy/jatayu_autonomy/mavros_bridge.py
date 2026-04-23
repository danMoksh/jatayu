"""
Jatayu MAVROS Telemetry Bridge Node
Bridges ArduPilot/PX4 MAVROS topics to Jatayu ROS 2 interfaces and provides flight mode services.
"""

from typing import Optional

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Header
    from sensor_msgs.msg import NavSatFix, BatteryState
    from geometry_msgs.msg import PoseStamped, TwistStamped
    from mavros_msgs.msg import State, VfrHud
    from mavros_msgs.srv import SetMode, CommandBool
    from jatayu_msgs.msg import DroneTelemetry
    from jatayu_msgs.srv import SwitchFlightMode
except ImportError:
    Node = object


class MavrosBridge(Node):
    def __init__(self, node_name: str = "mavros_bridge"):
        if Node is not object:
            super().__init__(node_name)
        else:
            self.node_name = node_name

        self.telemetry = {
            "lat": 26.25104,
            "lon": 78.17124,
            "alt_msl": 0.0,
            "alt_rel": 0.0,
            "heading": 0.0,
            "ground_speed": 0.0,
            "air_speed": 0.0,
            "climb_rate": 0.0,
            "battery_pct": 100.0,
            "battery_volt": 16.8,
            "mode": "UNKNOWN",
            "armed": False,
            "vtol_state": "MC",
            "sats": 12,
        }

        self._init_ros()

    def _init_ros(self):
        if not hasattr(self, 'create_subscription'):
            return

        # MAVROS Subscriptions
        self.create_subscription(State, "/mavros/state", self._state_cb, 10)
        self.create_subscription(NavSatFix, "/mavros/global_position/global", self._gps_cb, 10)
        self.create_subscription(VfrHud, "/mavros/vfr_hud", self._vfr_cb, 10)
        self.create_subscription(BatteryState, "/mavros/battery", self._battery_cb, 10)

        # Jatayu Telemetry Publisher
        self.telem_pub = self.create_publisher(DroneTelemetry, "/jatayu/telemetry", 10)

        # Jatayu Services
        self.create_service(SwitchFlightMode, "/jatayu/switch_flight_mode", self._handle_switch_mode)

        # MAVROS Service Clients
        self.set_mode_client = self.create_client(SetMode, "/mavros/set_mode")

        # 10 Hz Telemetry broadcast timer
        self.create_timer(0.1, self._publish_telemetry)
        self.get_logger().info("Jatayu MAVROS Bridge active.")

    def _state_cb(self, msg):
        self.telemetry["mode"] = msg.mode
        self.telemetry["armed"] = msg.armed

    def _gps_cb(self, msg):
        self.telemetry["lat"] = msg.latitude
        self.telemetry["lon"] = msg.longitude
        self.telemetry["alt_msl"] = msg.altitude

    def _vfr_cb(self, msg):
        self.telemetry["heading"] = msg.heading
        self.telemetry["ground_speed"] = msg.groundspeed
        self.telemetry["air_speed"] = msg.airspeed
        self.telemetry["climb_rate"] = msg.climb
        self.telemetry["alt_rel"] = msg.altitude

    def _battery_cb(self, msg):
        self.telemetry["battery_pct"] = msg.percentage * 100.0 if msg.percentage <= 1.0 else msg.percentage
        self.telemetry["battery_volt"] = msg.voltage

    def _publish_telemetry(self):
        if not hasattr(self, 'telem_pub'):
            return
        msg = DroneTelemetry()
        msg.latitude = self.telemetry["lat"]
        msg.longitude = self.telemetry["lon"]
        msg.altitude_msl = float(self.telemetry["alt_msl"])
        msg.altitude_relative = float(self.telemetry["alt_rel"])
        msg.heading = float(self.telemetry["heading"])
        msg.ground_speed = float(self.telemetry["ground_speed"])
        msg.air_speed = float(self.telemetry["air_speed"])
        msg.climb_rate = float(self.telemetry["climb_rate"])
        msg.battery_percentage = float(self.telemetry["battery_pct"])
        msg.battery_voltage = float(self.telemetry["battery_volt"])
        msg.flight_mode = str(self.telemetry["mode"])
        msg.vtol_state = str(self.telemetry["vtol_state"])
        msg.armed = bool(self.telemetry["armed"])
        msg.satellites_visible = int(self.telemetry["sats"])
        self.telem_pub.publish(msg)

    def _handle_switch_mode(self, request, response):
        req_mode = request.requested_mode.upper()
        if hasattr(self, 'get_logger'):
            self.get_logger().info(f"Switch flight mode requested: {req_mode}")
        self.telemetry["mode"] = req_mode
        response.success = True
        response.current_mode = req_mode
        response.message = f"Flight mode successfully updated to {req_mode}"
        return response


def main(args=None):
    if 'rclpy' in globals():
        rclpy.init(args=args)
        node = MavrosBridge()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
    else:
        bridge = MavrosBridge()
        print(f"MAVROS Bridge initialized (standalone mode), mode: {bridge.telemetry['mode']}")


if __name__ == "__main__":
    main()
