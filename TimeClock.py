import os, sys, os.path, requests, getpass, GUI 
from os.path import exists


def loginSetup():
    if(os.path.exists("Login.txt")):
        os.remove("Login.txt")

    while True:
        userInput = input("\nLogin Data file not detected, would you like to proceed with First Time Setup? (Y or N)\n")

        if (userInput.upper() == "Y"):
            loginWrite = open("Login.txt", "w+")

            userName = input("\nPlease input your username now: ")

            while True:
                userPass = ""
                userPass = getpass.getpass("Please input your password: ")
                #userPass2 = input("Please verify your password: ")

                if (userPass == getpass.getpass("Please verify your password: ")):
                    loginWrite.write(userName + "\n" + userPass)
                    loginWrite.close()
                    break;

                else:
                    print("\nPasswords do not match, please try again.\n")

            break;

        elif (userInput.upper() == "N"):
            print("\nGoodbye!")
            sys.exit(0)

        else:
            print("\nERROR: Invalid Operator Detected \'%s\' please try again." % (userInput))

def getJWT():
    loginFile = open("Login.txt", "r")
    userName = loginFile.readline().strip()
    password = loginFile.readline().strip()

    url = "https://clock.payrollservers.us/AuthenticationService/OwnerCredentialsGrant/login"

    payload = {
     "username": userName,
     "password": password,
     "site": ""
}
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)

    responseJson = response.json()
    try:
        return responseJson["jwt"]
    except:
        userInput = input("\nAn error has occured, this is usually because of an improper Username / Password configuration. Would you like to perform first time setup now?\n")
        if userInput.upper() == "Y":
            loginSetup()
            print("\nLogin Setup completed. Please retry last command now.\n")
        else:
            print("\nGoodbye.")
            sys.exit(0)

def clockIn(webToken):
    import requests

    url = "https://clock.payrollservers.us/ClockService/Punch"

    payload = {
     "clockPrompts": [],
     "dataCollectionMeta": [],
     "expectedPunches": ["PunchIn"]
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://clock.payrollservers.us/?wl=erccolorado.payrollservers.us",
        "jwt": webToken,
        "punch": "PunchIn",
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://clock.payrollservers.us",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    response = requests.request("POST", url, json=payload, headers=headers)


def clockOut(webToken):
    import requests

    url = "https://clock.payrollservers.us/ClockService/Punch"

    payload = {
     "clockPrompts": [],
     "dataCollectionMeta": [],
     "expectedPunches": ["PunchOut"]
    }
    headers = {
     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) Gecko/20100101 Firefox/101.0",
     "Accept": "application/json, text/plain, */*",
     "Accept-Language": "en-US,en;q=0.5",
     "Accept-Encoding": "gzip, deflate, br",
     "Referer": "https://clock.payrollservers.us/?wl=erccolorado.payrollservers.us",
     "jwt": webToken,
     "punch": "PunchOut",
     "Content-Type": "application/json;charset=utf-8",
     "Origin": "https://clock.payrollservers.us",
     "Connection": "keep-alive",
     "Sec-Fetch-Dest": "empty",
     "Sec-Fetch-Mode": "cors",
     "Sec-Fetch-Site": "same-origin"
    }

    response = requests.request("POST", url, json=payload, headers=headers)


if(not os.path.exists("Login.txt")):
    loginSetup()

print(getJWT())





