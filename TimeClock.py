import os, sys, requests, getpass, keyring, tkinter, time
from tkinter import *
from tkinter import messagebox

def loginSetup():

    while True:
        userInput = input("\nLogin Data not detected, would you like to proceed with First Time Setup? (Y or N)\n")

        if (userInput.upper() == "Y"):
            
            userName = input("\nPlease input your username now: ")

            while True:
                userPass = ""
                userPass = getpass.getpass("Please input your password: ")

                if (userPass == getpass.getpass("Please verify your password: ")):
                    keyring.set_password("TimeClockManager", "username", userName)
                    keyring.set_password("TimeClockManager", userName, userPass)
                    break

                else:
                    print("\nPasswords do not match, please try again.\n")

            break

        elif (userInput.upper() == "N"):
            print("\nGoodbye!")
            sys.exit(0)

        else:
            print("\nERROR: Invalid Operator Detected \'%s\' please try again." % (userInput))

def getJWT():
    userName = keyring.get_password("TimeClockManager", "username") 

    url = "https://clock.payrollservers.us/AuthenticationService/OwnerCredentialsGrant/login"

    payload = {
     "username": userName,
     "password": keyring.get_password("TimeClockManager", userName),
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

#def clockIn(webToken):

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


#def clockOut(webToken):

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

def clockIn(webToken):
    print(webToken)

def clockOut(webToken):
    print(webToken)


def buttonClick(buttonType):
    currentTime = time.strftime("%I:%M:%S", time.localtime())
    if(buttonType == 1):
        # Run Clock In Function, Print Time, Append Time to Log
        clockIn(getJWT())
        messagebox.showinfo("Clocked In!", "Clocked in at: " + currentTime)

    elif(buttonType == 2): 
        # Run Clock Out Function, Print Time, Append Time to Log
        clockOut(getJWT())
        messagebox.showinfo("Clocked Out!", "Clocked out at: " + currentTime)

def menuClick(menuType):
    if(menuType == 1):
        print(getJWT())

def guiMain():
    window = tkinter.Tk()
    window.title("Time Clock Manager")
    window.geometry("300x100")
    
    clockIn = Button(window, text="Clock In", width=9, height=3, command=lambda: buttonClick(1))
    clockIn.place(relx=0.10, rely=0.20)
    clockOut = Button(window, text="Clock Out", width=9, height=3, command=lambda: buttonClick(2))
    clockOut.place(relx=0.50, rely=0.20)

    menuBar = Menu(window)
    window.config(menu=menuBar)

    adminMenu = Menu(menuBar)
    menuBar.add_cascade(label="Admin", menu=adminMenu)
    adminMenu.add_command(label = "Perform First Time Login Setup", command=lambda: loginSetup())
    adminMenu.add_separator()
    adminMenu.add_command(label = "Get JWT", command=lambda: menuClick(1))

    window.mainloop()


if (keyring.get_password("TimeClockManager", "username") is None):
    loginSetup()

guiMain()
