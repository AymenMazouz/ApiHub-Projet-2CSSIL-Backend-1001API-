class NotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self._message = message
        super().__init__(message)

    @property
    def message(self) -> str:
        return self._message if self._message else "Not found"


class BadRequestError(Exception):
    def __init__(self, message: str) -> None:
        self._message = message
        super().__init__(message)

    @property
    def message(self) -> str:
        return self._message if self._message else "Bad request"
