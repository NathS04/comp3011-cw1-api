class NotFoundException(Exception):
    def __init__(self, name: str):
        self.name = name

class DuplicateException(Exception):
    def __init__(self, name: str):
        self.name = name

class AuthException(Exception):
    def __init__(self, detail: str):
        self.detail = detail
