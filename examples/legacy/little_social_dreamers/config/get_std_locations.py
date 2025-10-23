import xdg
import pydantic
import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
import socket

ApiKeyT = type("ApiKey", (str,), {})
RessourceDirT = type("RessourceDir", (Path,), {})


class StdLocations(pydantic.BaseModel):
    data_dir: RessourceDirT
    config_dir: RessourceDirT
    temp_dir: RessourceDirT
    default_api_key: ApiKeyT
    socket: socket.SocketType

    @classmethod
    def get_locations(cls) -> "StdLocations":
        # Try XDG locations
        try:
            data_dir = xdg.xdg_data_home() / "little_social_dreamers"
            config_dir = xdg.xdg_config_home() / "little_social_dreamers"
            temp_dir = xdg.xdg_cache_home() / "little_social_dreamers"
            return cls(data_dir=data_dir, config_dir=config_dir, temp_dir=temp_dir)
        except Exception:
            pass

        # Try .env file in current directory and basic environment variables

        load_dotenv()
        data_dir = os.getenv("LSD_DATA_DIR")
        config_dir = os.getenv("LSD_CONFIG_DIR")
        temp_dir = os.getenv("LSD_TEMP_DIR")
        if data_dir and config_dir and temp_dir:
            return cls(
                data_dir=Path(data_dir),
                config_dir=Path(config_dir),
                temp_dir=Path(temp_dir),
            )

        # If nothing is found, ask the user to create the folders
        user_input = input(
            """Failed to get standard locations. Do you want to create the necessary folders?

            If you want to create the folders, you can create the .lsd and .config/lsd directories in your home directory.
            Proceed? (y/n)

            (Alternatively, you can set the environment variables LSD_DATA_DIR, LSD_CONFIG_DIR, and LSD_TEMP_DIR to the desired locations. 
            Or you can set the XDG_DATA_HOME, XDG_CONFIG_HOME, and XDG_CACHE_HOME environment variables to the desired locations.)"""
        )
        if user_input == "y":
            data_dir = home_dir / ".lsd" / "data"
            config_dir = home_dir / ".config" / "lsd"
            temp_dir = home_dir / ".lsd" / "temp"
            for dir in [data_dir, config_dir, temp_dir]:
                dir.mkdir(parents=True, exist_ok=True)
            return cls(data_dir=data_dir, config_dir=config_dir, temp_dir=temp_dir)
        else:
            raise RuntimeError("Failed to get standard locations.")
