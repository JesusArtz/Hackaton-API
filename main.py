from __init__ import APP
from src.routes import ROOT

for route in ROOT:
    APP.add_url_rule(route["path"], view_func=route["handler"], methods=[route["method"]])

if __name__ == '__main__':
    APP.run(debug=True, host="0.0.0.0", port=5000)