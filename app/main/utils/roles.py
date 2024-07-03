class Role:
    ADMIN = "admin"
    USER = "user"
    SUPPLIER = "supplier"

    @staticmethod
    def role_exists(role: str):
        return role in (
            getattr(Role, attr)
            for attr in dir(Role)
            if not callable(getattr(Role, attr))
        )
