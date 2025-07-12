# Autonomous Vehicle Project

Welcome to the Autonomous Vehicle Project! This is a fun project where we build a self-driving car using ROS 2 and a simulation tool called Ignition Gazebo. You can run a virtual car, track its position, and plan its path to move around.

---

## What You Need to Get Started

Before you begin, make sure you have these things installed on your computer (using Ubuntu 22.04):

- **ROS 2 Humble**: The main software for robot programming.
- **Ignition Gazebo Fortress**: A tool to create a virtual world for the car.
- **Some Tools**:
  - `colcon` (to build the project).
  - `vcstool` (to manage files).
  - `rosdep` (to install extra parts).
- **Extra Packages**:
  - `ros-humble-ros-ign-gazebo`, `ros-humble-ros-ign-bridge`, `ros-humble-ros-ign-interfaces` (to connect ROS and Gazebo).
  - `ignition-fortress` (the specific Gazebo version).

### How to Install Everything

Open a terminal and run these commands one by one:

```bash
sudo apt update
sudo apt install -y python3-vcstool python3-colcon-common-extensions rosdep
sudo rosdep init
rosdep update
sudo apt install -y ros-humble-ros-ign-gazebo ros-humble-ros-ign-bridge ros-humble-ros-ign-interfaces
sudo apt install -y ignition-fortress
```

- Check if it worked:
  - Type `echo $ROS_DISTRO` (should say `humble`).
  - Type `ign gazebo --versions` (should show Fortress 6.17.0).

---

## Setting Up the Project

1. **Get the Project Files**:
   - Open a terminal and go to your home folder:
     ```bash
     cd ~
     ```
   - Make a new folder for the project and enter it:
     ```bash
     mkdir -p autonomous_vehicle_ws/src
     cd autonomous_vehicle_ws
     ```
   - Copy the project files into the `src` folder (ask someone for the files if you don’t have them).

2. **Prepare the Project**:
   - Install any missing parts:
     ```bash
     rosdep install --from-paths src --ignore-src -r -y
     ```

3. **Build the Project**:
   - Build everything:
     ```bash
     colcon build --symlink-install
     ```
   - Tell your computer where the project is:
     ```bash
     source /opt/ros/humble/setup.bash
     source install/setup.bash
     ```

4. **Check Everything**:
   - See the project parts: `ros2 pkg list | grep autonomous_vehicle` (should show your project).
   - Find Gazebo: `which ign_gazebo` (should show a path like `/usr/bin/ign_gazebo`).

---

## Running the Project

### Start the Virtual World
- Open a terminal and start the car’s world:
  ```bash
  ign gazebo -v 4 -r ~/autonomous_vehicle_ws/src/autonomous_vehicle/worlds/simple_world.sdf
  ```
- This creates a flat area where the car can move.

### Connect ROS and Gazebo
- Open a new terminal and set up the bridge to share data between ROS and Gazebo:
  ```bash
  source /opt/ros/humble/setup.bash
  source ~/autonomous_vehicle_ws/install/setup.bash
  ros2 run ros_gz_bridge parameter_bridge /camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image /imu/data@sensor_msgs/msg/Imu@ignition.msgs.IMU /gps/fix@sensor_msgs/msg/NavSatFix@ignition.msgs.NavSat
  ```
- This links the car’s camera, IMU, and GPS data so your program can use it.

### Run the Car’s Brain
Open new terminals and run these one by one:
1. **Run Sensor Fusion**
  - ros2 run autonomous_vehicle sensor_fusion --ros-args --log-level debug

1. **Run Path Planner**
ros2 run autonomous_vehicle path_planning --ros-args --log-level debug
1. **Track the Car’s Position**:
   - Type:
     ```bash
     ros2 run autonomous_vehicle rcnn_localization
     ```
   - This tells the car where it is (starts at 10.0, 0.0).

2. **Combine Sensor Data**:
   - Type:
     ```bash
     ros2 run autonomous_vehicle sensor_fusion > sensor_fusion.log 2>&1 &
     ```
   - Check the log: `cat sensor_fusion.log`.
   - This mixes data to help the car move.

3. **Plan the Car’s Path**:
   - Type:
     ```bash
     ros2 run autonomous_vehicle path_planning
     ```
   - This decides where the car should go.

4. **Drive the Car**:
   - Type:
     ```bash
     ros2 run teleop_twist_keyboard teleop_twist_keyboard
     ```
   - Use `w` to go forward, `s` to go back, `a` to turn left, `d` to turn right.

### Watch the Car
- Open a new terminal and type:
  ```bash
  rviz2
  ```
- Add a “Path” box and set it to `/path`, and an “Odometry” box set to `/odometry/filtered`.
- You’ll see the car’s position and planned path on the screen!

---

## If Something Goes Wrong

- **Nothing Happens**: Make sure all commands are run and everything is installed. Type `ros2 topic list` to see active topics.
- **Car Doesn’t Move**: Check `simple_world.sdf` has a car with wheels and a “DiffDrive” part. Test with:
  ```bash
  ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}" -r 10
  ```
- **No Path**: Make sure `path_planning` knows where to go (it aims for 20.0, 10.0 by default).

---

## Tips for Developers

- Put your code files in `~/autonomous_vehicle_ws/src/autonomous_vehicle/autonomous_vehicle/`.
- Change `simple_world.sdf` to add a cool car model (like a Range Rover!) with the right parts.
- Save logs with `> log_file.log 2>&1 &` to see what’s happening.
- Test the car’s sensors (`/imu/data`, `/gps/fix`) when it moves.

---

## Making It Better

- Add a start button file (like `launch/autonomous_vehicle.launch.py`) to run everything at once.
- Let `path_planning` pick different destinations.
- Write notes about how `sensor_fusion` and `path_planning` work.

Have fun building your autonomous car! If you need help, ask someone or look at the logs. Happy driving!

---
