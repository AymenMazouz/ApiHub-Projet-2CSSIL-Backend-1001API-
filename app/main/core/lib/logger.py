from typing import Any, Dict


class Logger:
    def info(self, context: str, payload: Dict[str, Any]):
        raise Exception("You must implement this method in a subclass.")

    def error(self, msg: str, payload: Dict[str, Any]):
        raise Exception("You must implement this method in a subclass.")
