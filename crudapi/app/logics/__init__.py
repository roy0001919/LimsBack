import requests


def login():
    loginurl = "http://3.139.254.61:8080/senaite/@@API/senaite/v1/login?__ac_name=admin&__ac_password=admin"
    reslogin = requests.get(loginurl)
    return reslogin


reslogin = login()
