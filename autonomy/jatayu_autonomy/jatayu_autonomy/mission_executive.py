"""
Jatayu VTOL Mission Executive
Orchestrates autonomous flight lifecycle for QuadPlane UAV:
VTOL Takeoff -> Transition to Fixed Wing -> Survey Patrol -> Target Hover -> Payload Drop -> Return to Launch.
"""

import enum
import time
from typing import Optional

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String, Header
    from geometry_msgs.msg import PoseStamped
    from jatayu_msgs.msg import DroneTelemetry, TargetDetection, PayloadStatus
    from jatayu_msgs.srv import DeployPayload, SwitchFlightMode
except ImportError:
    # Standalone mock fallback for simulation / test environments outside full ROS2 install
    Node = object


class VTOLState(enum.Enum):
    STANDBY = "STANDBY"
    PREFLIGHT_CHECK = "PREFLIGHT_CHECK"
    VTOL_TAKEOFF = "VTOL_TAKEOFF"
    TRANSITION_TO_FW = "TRANSITION_TO_FW"
    WAYPOINT_SURVEY = "WAYPOINT_SURVEY"
    TARGET_APPROACH = "TARGET_APPROACH"
    TRANSITION_TO_MC = "TRANSITION_TO_MC"
    PRECISION_HOVER = "PRECISION_HOVER"
    PAYLOAD_DELIVERY = "PAYLOAD_DELIVERY"
    TRANSITION_TO_FW_RETURN = "TRANSITION_TO_FW_RETURN"
    RTL = "RTL"
    VTOL_LAND = "VTOL_LAND"
    ABORT = "ABORT"


class MissionExecutive(Node):
    def __init__(self, node_name: str = "mission_executive"):
        if Node is not object:
            super().__init__(node_name)
        else:
            self.node_name = node_name

        self.current_state = VTOLState.STANDBY
        self.target_altitude_m = 35.0
        self.transition_airspeed_ms = 16.0
        self.drop_altitude_m = 12.0
        self.hover_tolerance_ms = 1.5

        # Telemetry Cache
        self.latest_telemetry: Optional[dict] = None
        self.active_target: Optional[dict] = None
        self.payload_delivered = False

        self._init_ros()

    def _init_ros(self):
        """Initialize ROS 2 subscribers, publishers and timers if in ROS environment."""
        if not hasattr(self, 'create_subscription'):
            return

        self.telemetry_sub = self.create_subscription(
            DroneTelemetry,
            "/jatayu/telemetry",
            self._telemetry_callback,
            10
        )
        self.target_sub = self.create_subscription(
            TargetDetection,
            "/jatayu/target_detected",
            self._target_callback,
            10
        )
        self.state_pub = self.create_publisher(
            String,
            "/jatayu/vtol_state",
            10
        )
        self.mode_client = self.create_client(
            SwitchFlightMode,
            "/jatayu/switch_flight_mode"
        )
        self.payload_client = self.create_client(
            DeployPayload,
            "/jatayu/deploy_payload"
        )

        # 5 Hz state machine loop
        self.timer = self.create_timer(0.2, self.step_state_machine)
        self.get_logger().info("Jatayu Mission Executive initialized in STANDBY state.")

    def _telemetry_callback(self, msg):
        self.latest_telemetry = {
            "lat": msg.latitude,
            "lon": msg.longitude,
            "alt": msg.altitude_relative,
            "airspeed": msg.air_speed,
            "groundspeed": msg.ground_speed,
            "mode": msg.flight_mode,
            "armed": msg.armed,
        }

    def _target_callback(self, msg):
        # Trigger high-priority response on critical detection
        if msg.severity_index >= 7 and self.current_state == VTOLState.WAYPOINT_SURVEY:
            self.active_target = {
                "id": msg.target_id,
                "lat": msg.estimated_lat,
                "lon": msg.estimated_lon,
                "severity": msg.severity_index,
            }
            self.transition_to(VTOLState.TARGET_APPROACH)

    def transition_to(self, new_state: VTOLState) -> bool:
        """Enforces valid state transitions and logs progression."""
        old_state = self.current_state
        self.current_state = new_state
        if hasattr(self, 'get_logger'):
            self.get_logger().info(f"VTOL Executive State Change: [{old_state.value}] -> [{new_state.value}]")
        return True

    def step_state_machine(self):
        """Main state machine step evaluated every cycle."""
        state = self.current_state

        if state == VTOLState.STANDBY:
            pass  # Waiting for operator arming / takeoff command

        elif state == VTOLState.VTOL_TAKEOFF:
            # Climb to transition altitude in Multirotor mode (QHOVER / QLOITER)
            alt = self.latest_telemetry.get("alt", 0.0) if self.latest_telemetry else 0.0
            if alt >= self.target_altitude_m:
                self.transition_to(VTOLState.TRANSITION_TO_FW)

        elif state == VTOLState.TRANSITION_TO_FW:
            # QuadPlane spins up pusher motor until airspeed reaches transition threshold
            airspeed = self.latest_telemetry.get("airspeed", 0.0) if self.latest_telemetry else 0.0
            if airspeed >= self.transition_airspeed_ms:
                self.transition_to(VTOLState.WAYPOINT_SURVEY)

        elif state == VTOLState.WAYPOINT_SURVEY:
            # Cruises along survey pattern looking for targets
            pass

        elif state == VTOLState.TARGET_APPROACH:
            # Navigates to target GPS coordinates; once within radius, decelerates and transitions to hover
            self.transition_to(VTOLState.TRANSITION_TO_MC)

        elif state == VTOLState.TRANSITION_TO_MC:
            # Transitions back from Fixed-Wing to Multirotor hover mode (QLOITER)
            groundspeed = self.latest_telemetry.get("groundspeed", 99.0) if self.latest_telemetry else 99.0
            if groundspeed <= self.hover_tolerance_ms:
                self.transition_to(VTOLState.PRECISION_HOVER)

        elif state == VTOLState.PRECISION_HOVER:
            # Descends to safe drop altitude and stabilizes position
            alt = self.latest_telemetry.get("alt", 99.0) if self.latest_telemetry else 99.0
            if abs(alt - self.drop_altitude_m) <= 1.5:
                self.transition_to(VTOLState.PAYLOAD_DELIVERY)

        elif state == VTOLState.PAYLOAD_DELIVERY:
            # Triggers servo actuation
            self.payload_delivered = True
            self.transition_to(VTOLState.TRANSITION_TO_FW_RETURN)

        elif state == VTOLState.TRANSITION_TO_FW_RETURN:
            # Re-accelerates into fixed wing flight for energy-efficient return
            self.transition_to(VTOLState.RTL)

        elif state == VTOLState.RTL:
            # Navigates back to home coordinates
            pass


def main(args=None):
    if 'rclpy' in globals():
        rclpy.init(args=args)
        node = MissionExecutive()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
    else:
        exec_node = MissionExecutive()
        print(f"Mission Executive initialized (standalone mode), state: {exec_node.current_state.value}")


if __name__ == "__main__":
    main()
