class FoxopsApiError(Exception):
    def __init__(self, message: str):
        super().__init__()
        self.message = message


class AuthenticationError(Exception):
    pass


class IncarnationDoesNotExistError(FoxopsApiError):
    pass
