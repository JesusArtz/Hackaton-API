from src.routes.Auth.login import login
from src.routes.Auth.register import register
from src.routes.User.user_info import get_user_info

ROOT = [
    {
        "path": "/register",
        "method": "POST",
        "handler": register
    },
    {
        "path": "/login",
        "method": "POST",
        "handler": login
    },
    {
        "path": "/user",
        "method": "GET",
        "handler": get_user_info
    },
]