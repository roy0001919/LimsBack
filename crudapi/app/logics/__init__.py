import requests


def login():
    loginurl = "http://172.20.10.5:8080/senaite/@@API/senaite/v1/login?__ac_name=admin&__ac_password=admin"
    reslogin = requests.get(loginurl)
    return reslogin


reslogin = login()
