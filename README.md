# artemis_simulation
Simulation for Artemis

## Installing dependencies

### Installing system dependencies
Run the following commands:
```sh
sudo apt install python-is-python3 python3-pip
```

### Installing ROS Foxy
Follow the installation guide here: [ROS2 Foxy Installation](https://docs.ros.org/en/foxy/Installation/Ubuntu-Install-Debians.html), up to and including the `Environment setup` section.
In the `Install ROS 2 packages` section, install the `ros-foxy-desktop` package, not the `ros-foxy-base`.
In the `Environment setup` section, you can add the `source` line to your `.bashrc`.

### Creating a ROS2 workspace
Create the following folder architecture in your home directory:
Clone the repo in the `artemis_ws/src` directory.
```sh
mkdir -p artemis_ws/src
cd artemis_ws/src
git clone https://github.com/robotique-udes/artemis_simulation
```

### Downloading Ardupilot and installing its depencencies
Run the following command from the repo root:
```sh
artemis_ardupilot/cmake/setup_sitl.py ./artemis_ardupilot
```

## Building ArduPilot
ArduPilot will be built by `colcon` with the rest of the package, provided you installed the dependencies before.
Run the following command in your workspace root (`artemis_ws`):
```sh
colcon build --symlink-install
```
You can then add the workspace setup to your `.bashrc` (`source ~/artemis_ws/install/setup.sh`).

## Running the SITL using MAVProxy
The first time you run it, you will need to pass the `-w` flag, to wipe the virtual EEPROM and load the default parameters (https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html).
```sh
ros2 run artemis_ardupilot sim_vehicle -w
```

After that, you can just run the following command:
```sh
ros2 run artemis_ardupilot sim_vehicle
```
By default, it will launch the underlying ArduPilot simulator with the following arguments:
- `-v ArduCopter` :: Using copter
- `--console` :: Launch the MAVProxy console
- `--map` :: Launch the MAVProxy map
- `-L UdeS` :: The drone starts in the parking of Université de Sherbrooke

If you launch the simulation with any manual parameter, these will not be passed, except for `-v ArduCopter`, which is always passed, as it is the only one that is built anyway.
This allows you to launch the simulation easily with the default settings, but you can also access all the underlying options of the ArduPilot simulation.
