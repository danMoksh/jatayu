#!/usr/bin/env bash
# ==============================================================================
# Jatayu VTOL ArduPilot SITL Simulation Runner
# Launches ArduPlane QuadPlane with MAVProxy forwarding telemetry to GCS & ROS 2
# ==============================================================================

set -e

# Default Home Location (MITS Gwalior)
HOME_LAT="26.25104"
HOME_LON="78.17124"
HOME_ALT="212"
HOME_HDG="0"

echo "=================================================="
echo "  Starting Jatayu VTOL SITL Simulation"
echo "  Coordinates: ${HOME_LAT}, ${HOME_LON} (${HOME_ALT}m MSL)"
echo "=================================================="

# Check if ArduPilot SITL is installed in system path
if command -v sim_vehicle.py >/dev/null 2>&1; then
    sim_vehicle.py -v ArduPlane \
        -f quadplane \
        -L "${HOME_LAT},${HOME_LON},${HOME_ALT},${HOME_HDG}" \
        --add-param-file="$(dirname "$0")/ardupilot/quadplane.parm" \
        --out=tcp:127.0.0.1:5760 \
        --out=udp:127.0.0.1:14550 \
        --console
else
    echo "ArduPilot sim_vehicle.py not detected in PATH."
    echo "Using Docker-based SITL fallback or manual MAVLink stream."
    echo "To run SITL via docker:"
    echo "  docker run -it --rm --net=host radarku/ardupilot-sitl arduplane -f quadplane"
fi
