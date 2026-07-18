from starlette.authentication import AuthenticationBackend, AuthCredentials, BaseUser
from starlette.requests import Request


class AdminUser(BaseUser):
    def __init__(self, username: str):
        self.username = username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username


class AdminAuthBackend(AuthenticationBackend):
    async def authenticate(self, request: Request):
        if request.session.get("admin_user"):
            return AuthCredentials(["admin"]), AdminUser(request.session["admin_user"])
        return None
