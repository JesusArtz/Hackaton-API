import requests

def Validate(curp):
    url = f"https://curp-renapo.p.rapidapi.com/v1/curp/{curp}"

    headers = {
        "content-type": "application/octet-stream",
        "X-RapidAPI-Key": "bf9c1883c5msha625339a27415e9p1bbcd6jsndc40c5a9f5fa",
        "X-RapidAPI-Host": "curp-renapo.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers)

    if response.json()['renapo_valid'] == True:
        return True