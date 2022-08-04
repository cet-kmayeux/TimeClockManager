import os, sys, requests, keyring, webbrowser, csv
import tkinter as tk
from tkinter import messagebox
from time import strftime
from sys import platform
from os.path import exists

def loginSetup():
    LoginCreator().run()

#This function gets the Json Web Token needed to authorize the user clocking in / out
def getJWT():

    userName = keyring.get_password("TimeClockManager", "username") 

    url = "https://clock.payrollservers.us/AuthenticationService/OwnerCredentialsGrant/login"

    payload = {
     "username": userName,
     "password": keyring.get_password("TimeClockManager", userName),
     "site": ""
}
    headers = {"Content-Type": "application/json"}

#Send a POST request to the target URL with the above data, storing the response into a variable
    response = requests.request("POST", url, json=payload, headers=headers)

    responseJson = response.json()

#If the response is a JWT as intended, return the token itself, otherwise, prompt the user for a password reset as that is the likely reason for a failure
    try:
        return responseJson["jwt"]
    except:
        userChoice = messagebox.askyesno("JWT ERROR", "An error has occured, this is usually because of an improper Username / Password configuration. Would you like to perform first time setup now?")
        if userChoice == True:
            loginSetup()
        else:
            messagebox.showinfo("Quit By User", "Goodbye.")
            sys.exit(0)


def clockStateCheck(buttonType):
    filename = "TimeClockInfo.csv"
    fields = ['Name', 'Date', 'Time', 'State']

    if(not exists(filename)):
        with open (filename, "a+") as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(fields)
        return True
    else:
        with open (filename, 'r') as csvFile:
            csvreader = csv.reader(csvFile)
            csvreader = list(csvreader)

            if (buttonType == 1):
                if ((csvreader[-1][-1]) == "Clocked In"):
                    return messagebox.askyesno("ERROR", "Last recorded action was: CLOCKING IN.\n\n Do you really want to Clock In again?")
                else:
                    return True

            elif (buttonType == 2):
                if ((csvreader[-1][-1]) == "Clocked Out"):
                    return messagebox.askyesno("ERROR", "Last recorded action was: CLOCKING OUT.\n\n Do you really want to Clock Out again?")
                else:
                    return True


def clockIn(webToken):
    filename = "TimeClockInfo.csv"
    date = strftime('%x')
    time = strftime('%I:%M:%S %p')

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

#Send a POST request containing the above data, including the user's JWT, this should lead to a Clocked In state
    response = requests.request("POST", url, json=payload, headers=headers)

    rows = [keyring.get_password("TimeClockManager", "username"), date, time, 'Clocked In']
    with open (filename, 'a') as csvFile:
        csvwriter = csv.writer(csvFile)
        csvwriter.writerow(rows)

def clockOut(webToken):
    filename = "TimeClockInfo.csv"
    date = strftime('%x')
    time = strftime('%I:%M:%S %p')

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

#Send a POST request containing the above data, including the user's JWT, this should lead to a Clocked Out state
    response = requests.request("POST", url, json=payload, headers=headers)

    rows = [keyring.get_password("TimeClockManager", "username"), date, time, 'Clocked Out']
    with open (filename, 'a') as csvFile:
        csvwriter = csv.writer(csvFile)
        csvwriter.writerow(rows)

#Opens the login page for the TimeClock site in a new window using the default browser
def goSite():
    webbrowser.open("https://clock.payrollservers.us/?wl=erccolorado.payrollservers.us#/clock/web/login", new=1, autoraise=True)



class MainUI(tk.Tk):
    def __init__(self, master=None):
        # build ui
        self.MainGUI = tk.Tk() if master is None else tk.Toplevel(master)
        self.frame1 = tk.Frame(self.MainGUI)
        self.goSite = tk.Button(self.frame1)
        self.goSite.configure(
            borderwidth=0,
            highlightbackground="#707ec9",
            text="Timeclock Website",
        )
        self.goSite.pack(pady=20, side="bottom")
        self.goSite.configure(command=lambda: self.buttonClick(3))
        self.clockIn = tk.Button(self.frame1)
        self.clockIn.configure(
            borderwidth=0,
            highlightbackground="#707ec9",
            text="Clock In",
        )
        self.clockIn.pack(padx=25, side="left")
        self.clockIn.configure(command=lambda: self.buttonClick(1))
        self.clockOut = tk.Button(self.frame1)
        self.clockOut.configure(
            borderwidth=0,
            highlightbackground="#707ec9",
            text="Clock Out",
        )
        self.clockOut.pack(padx=25, side="left")
        self.clockOut.configure(command=lambda: self.buttonClick(2))
        self.frame1.configure(background="#707ec9", height=200, width=200)
        self.frame1.place(relx=0.15, rely=0.5, x=0, y=0)
        self.clockFace = tk.Label(self.MainGUI)
        self.clockFace.configure(background="#707ec9", font="{Courier New} 52 {}")
        self.clockFace.place(
            anchor="nw", relheight=0.3, relwidth=0.9, relx=0.05, rely=0.05, x=0, y=0
        )
        
        menuBar = tk.Menu(self.MainGUI)
        admin = tk.Menu(menuBar)
        admin.add_command(label="Perform Login Setup", command=lambda: loginSetup())
        admin.add_command(label="Get JWT", command=lambda: messagebox.showinfo("", getJWT()))
        menuBar.add_cascade(label="Admin", menu=admin)


        self.MainGUI.configure(
            background="#707ec9", borderwidth=5, height=250, relief="ridge", menu=menuBar
        )
        self.MainGUI.configure(width=400)
        self.MainGUI.title("Time Clock Manager")

#Starts the clock face shown in the GUI
        self.time()

        # Main widget
        self.mainwindow = self.MainGUI

#When run, if the user doesn't have a login setup, open the Login Creation Window along with the main window
    def run(self):
        if (keyring.get_password("TimeClockManager", "username") is None):
            LoginCreator().run()
        self.mainwindow.mainloop()

    def buttonClick(self, buttonType):
        currentTime = strftime('%I:%M:%S %p')
        if(buttonType == 1):
            # Run Clock In Function, Print Time, Append Time to Log
            if(clockStateCheck(buttonType) == True):
                clockIn(getJWT())
                messagebox.showinfo("Clocked In!", "Clocked in at: " + currentTime)

        elif(buttonType == 2): 
            # Run Clock Out Function, Print Time, Append Time to Log
            if(clockStateCheck(buttonType) == True):
                clockOut(getJWT())
                messagebox.showinfo("Clocked Out!", "Clocked out at: " + currentTime)
            
            # Go to the Time Clock Website without logging in
        elif(buttonType == 3):
            goSite()

#Sets up the clock face and increments it every second
    def time(self):
        string = strftime('%I:%M:%S %p')
        self.clockFace.config(text = string)
        self.clockFace.after(1000, self.time)


class LoginCreator:
    def __init__(self, master=None):
        # build ui
        self.CredentialEntry = tk.Tk() if master is None else tk.Toplevel(master)
        self.loginMessage = tk.Message(self.CredentialEntry)
        self.loginMessage.configure(
            anchor="n",
            font="{Arial} 20 {}",
            justify="center",
            text="Please input your login credentials and then press submit.",
        )
        self.loginMessage.configure(width=340)
        self.loginMessage.place(
            anchor="nw", relwidth=0.9, relx=0.05, rely=0.05, x=0, y=0
        )
        self.userNameEntry = tk.Entry(self.CredentialEntry)
        self.userNameEntry.place(anchor="nw", relx=0.3, rely=0.45, x=0, y=0)
        self.userNameLabel = tk.Label(self.CredentialEntry)
        self.userNameLabel.configure(font="{Arial} 12 {}", text="Username")
        self.userNameLabel.place(anchor="nw", relx=0.1, rely=0.45, x=0, y=0)

        self.passwordEntry = tk.Entry(self.CredentialEntry, show="*")
        self.passwordEntry.place(anchor="nw", relx=0.3, rely=0.60, x=0, y=0)
        self.passwordLabel = tk.Label(self.CredentialEntry)
        self.passwordLabel.configure(font="{Arial} 12 {}", text="Password")
        self.passwordLabel.place(anchor="nw", relx=0.1, rely=0.60, x=0, y=0)

        self.passwordReEntry = tk.Entry(self.CredentialEntry, show="*")
        self.passwordReEntry.place(anchor="nw", relx=0.3, rely=0.75, x=0, y=0)
        self.passwordReLabel = tk.Label(self.CredentialEntry)
        self.passwordReLabel.configure(font="{Arial} 12 {}", text="Reenter Password")
        self.passwordReLabel.place(anchor="nw", relx=0.03, rely=0.75, x=0, y=0)

        self.submitButton = tk.Button(self.CredentialEntry)
        self.submitButton.configure(
            highlightbackground="#707ec9", text="Submit"
        )
        self.submitButton.place(anchor="nw", relx=0.78, rely=0.87, x=0, y=0)
        self.submitButton.configure(command=self.buttonClick)
        self.CredentialEntry.configure(background="#707ec9", height=250, width=400)
        self.CredentialEntry.title("Login Setup")

        

        # Main widget
        self.mainwindow = self.CredentialEntry

    def run(self):
        self.mainwindow.mainloop()

#On submission button click, verify that the passwords are the same, if so, submit info to keyring and close window; if not, prompt user to try again
    def buttonClick(self):
        userName = self.userNameEntry.get()
        password = self.passwordEntry.get()
        passwordRe = self.passwordReEntry.get()

        if (password == passwordRe):
            keyring.set_password("TimeClockManager", "username", userName)
            keyring.set_password("TimeClockManager", userName, password)

            messagebox.showinfo("Success", "Login Information Successfully Created")
            self.CredentialEntry.destroy()

        elif (password != passwordRe):
            messagebox.showerror('error', 'Passwords do not match, please try again!')
            self.passwordEntry.delete(0, 254)
            self.passwordReEntry.delete(0, 254)


if __name__ == "__main__":
    app = MainUI()
    app.run()
