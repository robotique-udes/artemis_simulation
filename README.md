# artemis_simulation
Simulation for Artemis

## Installing dependencies
Run the following command from the repo root:
```sh
cmake/setup_sitl.py .
```

## Building ArduPilot
ArduPilot will be built by `colcon` with the rest of the package, provided you installed the dependencies before.

## Running the SITL using MAVProxy
The first time you run it, you will need to pass the `-w` flag, to wipe the virtual EEPROM and load the default parameters (https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html).
```sh
ros2 run artemis_simulation sim_vehicle -w
```

After that, you can just run the following command:
```sh
ros2 run artemis_simulation sim_vehicle
```
By default, it will launch the underlying ArduPilot simulator with the following arguments:
- `-v ArduCopter` :: Using copter
- `--console` :: Launch the MAVProxy console
- `--map` :: Launch the MAVProxy map
- `-L UdeS` :: The drone starts in the parking of Université de Sherbrooke

If you launch the simulation with any manual parameter, these will not be passed, except for `-v ArduCopter`, which is always passed, as it is the only one that is built anyway.
This allows you to launch the simulation easily with the default settings, but you can also access all the underlying options of the ArduPilot simulation.
