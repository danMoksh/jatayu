# JATAYU ROS 2 Autonomy & Flight Stack Guide

The `autonomy` workspace houses the native ROS 2 nodes, messages, and services powering the Jatayu VTOL aircraft.

---

## 1. Package Overview

| Package | Type | Description |
| :--- | :--- | :--- |
| **`jatayu_msgs`** | `ament_cmake` | Interface definitions for telemetry, target detections, payload events, and flight mode service commands. |
| **`jatayu_autonomy`** | `ament_python` | Autonomous flight executive, MAVROS translation bridge, camera georeferencing, and payload actuator nodes. |

---

## 2. ROS 2 Topics

### Published Topics

| Topic | Message Type | Rate | Description |
| :--- | :--- | :--- | :--- |
| `/jatayu/telemetry` | `jatayu_msgs/msg/DroneTelemetry` | 10 Hz | Normalized vehicle state (GPS coordinates, MSL/AGL altitude, heading, speeds, battery, flight mode). |
| `/jatayu/vtol_state` | `std_msgs/msg/String` | 5 Hz | High-level VTOL state machine phase (`STANDBY`, `TRANSITION_TO_FW`, etc.). |
| `/jatayu/target_detected` | `jatayu_msgs/msg/TargetDetection` | Event | Georeferenced target record with calculated ground latitude, longitude, and severity. |
| `/jatayu/target_markers` | `visualization_msgs/msg/MarkerArray` | Event | 3D RViz visualization markers for detected survivors and search targets. |
| `/jatayu/payload_status` | `jatayu_msgs/msg/PayloadStatus` | 2 Hz | Status of the physical release mechanism, magazine count, and safety interlocks. |

### Subscribed Topics

| Topic | Source Node | Description |
| :--- | :--- | :--- |
| `/mavros/state` | MAVROS / Autopilot | Raw vehicle connection and arming status. |
| `/mavros/global_position/global` | MAVROS / Autopilot | Raw WGS84 GPS latitude and longitude fix. |
| `/mavros/vfr_hud` | MAVROS / Autopilot | Airspeed, groundspeed, climb rate, and heading. |
| `/mavros/battery` | MAVROS / Autopilot | Voltage and remaining battery capacity. |

---

## 3. ROS 2 Services

| Service Name | Service Type | Description |
| :--- | :--- | :--- |
| `/jatayu/switch_flight_mode` | `jatayu_msgs/srv/SwitchFlightMode` | Instructs the flight stack to switch modes (`QHOVER`, `QLOITER`, `AUTO`, `GUIDED`, `RTL`, `QRTL`). |
| `/jatayu/deploy_payload` | `jatayu_msgs/srv/DeployPayload` | Triggers payload actuation after verifying safety interlocks. |

---

## 4. Building and Running

### Prerequisites
- Ubuntu 22.04 LTS
- ROS 2 Humble Desktop
- Colcon build tools: `sudo apt install python3-colcon-common-extensions`

### Colcon Build
```bash
# In your ROS 2 workspace:
mkdir -p ~/jatayu_ws/src
cp -r /path/to/jatayu/autonomy/* ~/jatayu_ws/src/
cd ~/jatayu_ws

# Source ROS 2 Humble
source /opt/ros/humble/setup.bash

# Build all Jatayu packages
colcon build --symlink-install

# Source your workspace
source install/setup.bash
```

### Launching the Full Autonomy Stack
```bash
ros2 launch jatayu_autonomy mission_autonomy.launch.py
```

### Launching MAVROS Bridge Standalone
```bash
ros2 launch jatayu_autonomy mavros_bridge.launch.py
```
