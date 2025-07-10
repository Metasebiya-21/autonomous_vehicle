# autonomous_vehicle
# Autonomous Vehicle Workspace

This repository contains the ROS2 workspace and Ignition Gazebo simulation environment for the autonomous vehicle project.

---

## Prerequisites

- ROS2 Humble installed and sourced
- Ignition Gazebo installed (compatible with ROS2 Humble)
- `colcon` build tool installed
- `ros_gz_bridge` package installed

---

## Setup and Build

Open a terminal and run:

```bash
cd ~/autonomous_vehicle_ws
colcon build --symlink-install
source /opt/ros/humble/setup.bash
source install/setup.bash
