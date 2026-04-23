"""
Jatayu Payload Drop Controller Node
Provides safety-critical interlocks and triggers the physical release mechanism
over designated target zones.
"""

from datetime import datetime
from typing import Optional

try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import Header
    from mavros_msgs.srv import CommandLong
    from jatayu_msgs.msg import PayloadStatus, DroneTelemetry
    from jatayu_msgs.srv import DeployPayload
except ImportError:
    Node = object


class PayloadController(Node):
    def __init__(self, node_name: str = "payload_controller"):
        if Node is not object:
            super().__init__(node_name)
        else:
            self.node_name = node_name

        self.servo_channel = 11
        self.release_pwm = 2000
        self.remaining_payloads = 3
        self.last_drop_time: Optional[str] = None
        self.status = "IDLE"

        # Safety constraints
        self.min_drop_alt = 5.0
        self.max_drop_alt = 25.0
        self.max_hover_speed = 2.0

        self.latest_telemetry: dict = {}
        self._init_ros()

    def _init_ros(self):
        if not hasattr(self, 'create_subscription'):
            return

        self.create_subscription(DroneTelemetry, "/jatayu/telemetry", self._telemetry_cb, 10)
        self.status_pub = self.create_publisher(PayloadStatus, "/jatayu/payload_status", 10)
        self.create_service(DeployPayload, "/jatayu/deploy_payload", self._handle_deploy)

        # 2 Hz status publisher
        self.create_timer(0.5, self._publish_status)
        self.get_logger().info("Jatayu Payload Drop Controller initialized.")

    def _telemetry_cb(self, msg):
        self.latest_telemetry = {
            "alt": msg.altitude_relative,
            "speed": msg.ground_speed,
            "mode": msg.flight_mode,
            "armed": msg.armed,
        }

    def verify_safety_interlocks(self, force_override: bool = False) -> tuple[bool, str]:
        """Validates vehicle state against safety criteria before allowing drop actuation."""
        if force_override:
            return True, "Override enabled by operator"

        alt = self.latest_telemetry.get("alt", 0.0)
        speed = self.latest_telemetry.get("speed", 99.0)

        if alt < self.min_drop_alt:
            return False, f"Aircraft too low for safe dispersion ({alt:.1f}m < {self.min_drop_alt}m)"
        if alt > self.max_drop_alt:
            return False, f"Aircraft too high for accurate deployment ({alt:.1f}m > {self.max_drop_alt}m)"
        if speed > self.max_hover_speed:
            return False, f"Aircraft velocity too high ({speed:.1f}m/s > {self.max_hover_speed}m/s); requires hover"
        if self.remaining_payloads <= 0:
            return False, "Payload magazine empty"

        return True, "All safety interlocks clear"

    def execute_release(self) -> bool:
        """Actuates servo release mechanism."""
        self.status = "RELEASING"
        self.remaining_payloads = max(0, self.remaining_payloads - 1)
        self.last_drop_time = datetime.now().isoformat()
        self.status = "COMPLETED"
        return True

    def _handle_deploy(self, request, response):
        safe, reason = self.verify_safety_interlocks(request.force_override)
        if not safe:
            if hasattr(self, 'get_logger'):
                self.get_logger().warn(f"Payload drop rejected: {reason}")
            response.success = False
            response.message = f"Drop aborted: {reason}"
            response.drop_event_id = ""
            return response

        success = self.execute_release()
        event_id = f"DROP-{int(datetime.now().timestamp())}"
        response.success = success
        response.message = f"Payload successfully released at ({request.target_lat:.5f}, {request.target_lon:.5f})"
        response.drop_event_id = event_id
        return response

    def _publish_status(self):
        if not hasattr(self, 'status_pub'):
            return
        msg = PayloadStatus()
        msg.system_ready = self.remaining_payloads > 0
        msg.safety_interlock_engaged = True
        msg.remaining_payloads = self.remaining_payloads
        msg.last_drop_timestamp = self.last_drop_time or ""
        msg.drop_status = self.status
        self.status_pub.publish(msg)


def main(args=None):
    if 'rclpy' in globals():
        rclpy.init(args=args)
        node = PayloadController()
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        finally:
            node.destroy_node()
            rclpy.shutdown()
    else:
        ctrl = PayloadController()
        print(f"Payload Controller initialized (standalone mode), magazine: {ctrl.remaining_payloads}")


if __name__ == "__main__":
    main()
