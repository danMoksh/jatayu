"""
Unit tests for Jatayu VTOL Mission Executive state machine transitions.
"""

import unittest
from jatayu_autonomy.mission_executive import MissionExecutive, VTOLState


class TestMissionExecutive(unittest.TestCase):
    def setUp(self):
        self.executive = MissionExecutive(node_name="test_executive")

    def test_initial_state(self):
        self.assertEqual(self.executive.current_state, VTOLState.STANDBY)

    def test_state_transition(self):
        self.executive.transition_to(VTOLState.VTOL_TAKEOFF)
        self.assertEqual(self.executive.current_state, VTOLState.VTOL_TAKEOFF)

    def test_takeoff_to_transition(self):
        self.executive.transition_to(VTOLState.VTOL_TAKEOFF)
        self.executive.latest_telemetry = {"alt": 36.0, "airspeed": 5.0}
        self.executive.step_state_machine()
        self.assertEqual(self.executive.current_state, VTOLState.TRANSITION_TO_FW)

    def test_transition_to_survey(self):
        self.executive.transition_to(VTOLState.TRANSITION_TO_FW)
        self.executive.latest_telemetry = {"airspeed": 17.5}
        self.executive.step_state_machine()
        self.assertEqual(self.executive.current_state, VTOLState.WAYPOINT_SURVEY)

    def test_hover_and_drop_sequence(self):
        self.executive.transition_to(VTOLState.TRANSITION_TO_MC)
        self.executive.latest_telemetry = {"groundspeed": 0.8, "alt": 12.0}
        self.executive.step_state_machine()
        self.assertEqual(self.executive.current_state, VTOLState.PRECISION_HOVER)

        self.executive.step_state_machine()
        self.assertEqual(self.executive.current_state, VTOLState.PAYLOAD_DELIVERY)


if __name__ == "__main__":
    unittest.main()
