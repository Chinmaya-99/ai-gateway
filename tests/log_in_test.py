import sys
from pathlib import Path

sys.path.append(
        str(Path(__file__).resolve().parent.parent.parent)
)
from ai_gateway.app.services.auth.auth_service import AuthService

# user=AuthService.register_user(self=AuthService())
# print(user)

log_in=AuthService.login_user(self=AuthService())
print(log_in)


