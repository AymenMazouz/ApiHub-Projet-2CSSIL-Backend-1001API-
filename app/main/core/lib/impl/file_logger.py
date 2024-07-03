import json
from pathlib import Path
import datetime
from typing import Any, Dict
from app.main.core.lib.logger import Logger


class FileLogger(Logger):
    def __init__(self) -> None:
        print("FileLogger init")
        Path("logs/infos").mkdir(parents=True, exist_ok=True)
        Path("logs/errors").mkdir(parents=True, exist_ok=True)
        self.info_file = open(
            f"logs/infos/{datetime.datetime.now().strftime('%Y-%m-%d')}.log", "a"
        )
        self.error_file = open(
            f"logs/errors/{datetime.datetime.now().strftime('%Y-%m-%d')}.log", "a"
        )

    def info(self, context: str, payload: Dict[str, Any]):
        print(f"{datetime.datetime.now()} - {context} - {json.dumps(payload)}")
        self.info_file.write(
            f"{datetime.datetime.now()} - {context} - {json.dumps(payload)}\n"
        )
        self.info_file.flush()

    def error(self, context: str, payload: Dict[str, Any]):
        print(f"{datetime.datetime.now()} {context} {json.dumps(payload)}")
        self.error_file.write(
            f"{datetime.datetime.now()} - {context} - {json.dumps(payload)}\n"
        )
        self.error_file.flush()
