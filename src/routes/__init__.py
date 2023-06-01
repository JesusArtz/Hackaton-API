from src.routes.Auth.login import login
from src.routes.Auth.register import register
from src.routes.User.user_info import get_user_info
from src.routes.User.deposit import payment_sheet
from src.routes.User.save_transactions import save_transactions

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
    {
        "path": "/payment-sheet",
        "method": "POST",
        "handler": payment_sheet
    },
    {
        "path": "/save-transactions",
        "method": "POST",
        "handler": save_transactions
    }
    
]