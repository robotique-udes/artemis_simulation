#! /usr/bin/env python
import logging
import shutil
import subprocess
from typing import Set, Union, Tuple
import sys
from pathlib import Path
import argparse
from dataclasses import dataclass


class ExpandUserPath:
    def __new__(cls, path: Union[str, Path]) -> Path:
        return Path(path).expanduser().resolve()


def get_installed_apt_packages() -> Set[str]:
    return {
        line.split()[1].split(":")[0]
        for line in subprocess.check_output(["dpkg", "-l"]).decode().splitlines()
        if line.startswith("ii")
    }


def get_missing_apt_packages() -> Set[str]:
    PACKAGES = {
        "git",
        f"libpython{sys.version_info.major}.{sys.version_info.minor}-dev",
        f"libpython{sys.version_info.major}-dev",
        "libgtk-3-dev",
        f"python{sys.version_info.major}-wxgtk{sys.version_info.major + 1}.0",
    }
    return PACKAGES - get_installed_apt_packages()


def update_apt_cache():
    subprocess.check_call(["sudo", "apt-get", "update"])


def install_apt_packages(packages: Set[str]):
    if len(packages) > 0:
        subprocess.check_call(["sudo", "apt-get", "install", "-y", *packages])


def get_installed_pip_packages() -> Set[str]:
    return {
        line.split()[0]
        for line in subprocess.check_output([sys.executable, "-m", "pip", "list"]).decode().lower().splitlines()
    }


def get_missing_pip_packages() -> Tuple[Set[str], Set[str]]:
    PACKAGES_LV1 = {
        "attrdict",
        "matplotlib",
        "Pillow",
        "kiwisolver",
    }
    PACKAGES_LV2 = {
        "pymavlink",
        "MAVProxy",
    }

    missing_pkgs = set(map(str.lower, (PACKAGES_LV1 | PACKAGES_LV2))) - get_installed_pip_packages()
    return missing_pkgs & PACKAGES_LV1, missing_pkgs & PACKAGES_LV2


def missing_pip_packages_is_empty(packages: Tuple[Set[str], Set[str]]) -> bool:
    return len(packages[0] | packages[1]) == 0


def install_pip_packages(packages: Tuple[Set[str], Set[str]]):
    for package_lvl in packages:
        if len(package_lvl) > 0:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *package_lvl])


def is_repo_cloned(path: Union[str, Path]) -> bool:
    path = ExpandUserPath(path)
    return path.exists() and (path / ".git").exists()


def clone_repo(url: str, path: Union[str, Path]):
    path = ExpandUserPath(path)
    path.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["git", "clone", url, str(path)])
    subprocess.check_call(["git", "submodule", "update", "--init", "--recursive"], cwd=path)


def install_ardupilot_dependencies(path: Union[str, Path]):
    subprocess.check_call(["./Tools/environment_install/install-prereqs-ubuntu.sh", "-y"], cwd=path)


def build_ardupilot(path: Union[str, Path]):
    subprocess.check_call(["./waf copter"], shell=True, cwd=path)


def create_parent_dir(path: Union[str, Path]):
    epath = ExpandUserPath(path)
    if not epath.is_dir():
        epath = epath.parent
    epath.mkdir(parents=True, exist_ok=True)


def copy_file(src: Union[str, Path], dest: Union[str, Path]):
    shutil.copy(ExpandUserPath(src), ExpandUserPath(dest))


def file_is_up_to_date(old: Union[str, Path], new: Union[str, Path]) -> bool:
    eold = ExpandUserPath(old)
    enew = ExpandUserPath(new)
    return eold.exists() and enew.exists() and eold.stat().st_mtime >= enew.stat().st_mtime


def is_configured(path: Union[str, Path]) -> bool:
    build_path = ExpandUserPath(path) / "build"
    return (
        build_path.exists()
        and (build_path / "c4che").exists()
        and (build_path / "c4che" / "_cache.py").exists()
        and (build_path / "c4che" / "build.config.py").exists()
        and (build_path / "c4che" / "sitl_cache.py").exists()
        and (build_path / "sitl").exists()
        and (build_path / "sitl" / "ap_config.h").exists()
        and (build_path / "config.log").exists()
        and (build_path / ".lock-waf_linux_build").exists()
    )


def configure_ardupilot(path: Union[str, Path]):
    subprocess.check_call(["./waf configure"], shell=True, cwd=path)


@dataclass
class Args:
    build: bool
    src_path: Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src_path", type=ExpandUserPath)
    parser.add_argument("--build", action="store_true", default=False)
    args = parser.parse_args(namespace=Args)

    ARDUPILOT_PATH = args.src_path / "ardupilot" / "ardupilot"
    if args.build is True:
        # Check for missing dependencies
        missing_apt = get_missing_apt_packages()
        if len(missing_apt) != 0:
            logging.error(
                f"Missing apt packages: {missing_apt}. Run `cmake/setup_sitl.py .` in the artemis_simulation package root to install them."
            )
            sys.exit(1)
        missing_pip = get_missing_pip_packages()
        if not missing_pip_packages_is_empty(missing_pip):
            logging.warning(f"Missing pip packages: {missing_pip}. Installing them...")
            install_pip_packages(missing_pip)
        if not is_repo_cloned(ARDUPILOT_PATH):
            logging.error(
                f"ArduPilot not initialized to {ARDUPILOT_PATH}. Run `cmake/setup_sitl.py .` in the artemis_simulation package root to fetch and initialize it."
            )
            sys.exit(1)
        if not is_configured(ARDUPILOT_PATH):
            logging.warning(f"ArduPilot not configured. Configuring...")
            configure_ardupilot(ARDUPILOT_PATH)

        # Build ardupilot
        build_ardupilot(ARDUPILOT_PATH)

        # Copy locations.txt
        LOCATIONS_CONFIG_PATH = ExpandUserPath("~/.config/ardupilot/locations.txt")
        LOCATIONS_PATH = args.src_path / "resources/locations.txt"
        if not LOCATIONS_CONFIG_PATH.exists():
            create_parent_dir(LOCATIONS_CONFIG_PATH)
        if not file_is_up_to_date(LOCATIONS_CONFIG_PATH, LOCATIONS_PATH):
            copy_file(src=LOCATIONS_PATH, dest=LOCATIONS_CONFIG_PATH)

    else:
        # Will need `sudo` and/or take time, so we don't want to run it every time we build
        # Install apt packages
        missing_apt = get_missing_apt_packages()
        if len(missing_apt) != 0:
            update_apt_cache()
        install_apt_packages(missing_apt)
        # Install pip packages
        missing_pip = get_missing_pip_packages()
        if not missing_pip_packages_is_empty(missing_pip):
            install_pip_packages(missing_pip)

        # Clone ardupilot
        if not is_repo_cloned(ARDUPILOT_PATH):
            clone_repo("https://github.com/ArduPilot/ardupilot.git", ARDUPILOT_PATH)
            install_ardupilot_dependencies(ARDUPILOT_PATH)

        # Configure sitl for copter
        if not is_configured(ARDUPILOT_PATH):
            configure_ardupilot(ARDUPILOT_PATH)
