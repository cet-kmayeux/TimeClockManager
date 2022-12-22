import os, sys, requests, keyring, webbrowser, csv
import tkinter as tk
import base64
from tkinter import messagebox
from time import strftime
from sys import platform
from os.path import exists

def loginSetup():
    LoginCreator().run()

#This function gets the Json Web Token needed to authorize the user clocking in / out
def getJWT():
    internetStatus = app.internetCheck()

    if (internetStatus == 2):
        app.internetState.config(background="#ffb900", text = 'WARNING: Payroll Server Offline')
        messagebox.showinfo("WARNING", "You Currently Do Not Have Connection to the Payroll Servers\n\nExiting Script, Your Attempt Has Been Logged")
        return False
    elif (internetStatus == 0):
        app.internetState.config(background="#c9000b", text = 'ERROR: No Internet Connection')
        messagebox.showinfo("ERROR", "You Currently Do Not Have Internet Access, Please See Your System's Administrator\n\nExiting Script, Your Attempt Has Been Logged")
        return False
    elif (internetStatus == 1):
        app.internetState.config(background="#707ec9", text = '')

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

    with open (filename, 'r', newline='') as csvFile:
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
    time = strftime('%I:%M:%S%p')

    url = "https://clock.payrollservers.us/ClockService/Punch"

    if (webToken == False):
        rows = ['ERROR', keyring.get_password("TimeClockManager", "username"), date, time, base64.b64encode(bytes(time,'utf-8')), 'Clock In Attempted, But Failed']
        with open (filename, 'a', newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(rows)
        return False

    elif (webToken == "StateSet"):
        rows = ['DEBUG', keyring.get_password("TimeClockManager", "username"), date, time, base64.b64encode(bytes(time,'utf-8')), 'Clocked In']
        with open (filename, 'a', newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(rows)
        app.clockState.config(text="Current State: Clocked In", background="#00c900")

    else:
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

        rows = ['SUCCESS', keyring.get_password("TimeClockManager", "username"), date, time, base64.b64encode(bytes(time,'utf-8')), 'Clocked In']
        with open (filename, 'a', newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(rows)
        
        return True

def clockOut(webToken):
    filename = "TimeClockInfo.csv"
    date = strftime('%x')
    time = strftime('%I:%M:%S%p')

    url = "https://clock.payrollservers.us/ClockService/Punch"

    if (webToken == False):
        rows = ['ERROR', keyring.get_password("TimeClockManager", "username"), date, time, base64.b64encode(bytes(time,'utf-8')), 'Clock Out Attempted, But Failed']
        with open (filename, 'a', newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(rows)
        
        return False
    
    elif (webToken == "StateSet"):
        rows = ['DEBUG', keyring.get_password("TimeClockManager", "username"), date, time, base64.b64encode(bytes(time,'utf-8')), 'Clocked Out']
        with open (filename, 'a', newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(rows)
        app.clockState.config(text="Current State: Clocked Out", background="#c9000b")

    else:

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

        rows = ['SUCCESS', keyring.get_password("TimeClockManager", "username"), date, time, base64.b64encode(bytes(time,'utf-8')), 'Clocked In']
        with open (filename, 'a', newline='') as csvFile:
            csvwriter = csv.writer(csvFile)
            csvwriter.writerow(rows)

        return True

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
        self.clockState = tk.Label(self.MainGUI)
        self.clockState.configure(anchor="n", font="{Arial} 16 {}")

        self.clockStateSetter()

        self.clockState.place(
            anchor="nw", relheight=0.1, relwidth=0.6, relx=0.2, rely=0.33, x=0, y=0
        )
        self.versionNum = tk.Label(self.MainGUI)
        self.versionNum.configure(background="#707ec9", text="Version 2.5")
        self.versionNum.place(anchor="nw", relx=0.78, rely=0.9, x=0, y=0)

        self.internetState = tk.Label(self.MainGUI)
        self.internetState.configure(background="#707ec9", font="{Arial} 16 {}")
        self.internetState.place(
            anchor="nw", relheight=0.1, relwidth=0.65, relx=0.008, rely=0.89, x=0, y=0
        )
        
        menuBar = tk.Menu(self.MainGUI)
        debug = tk.Menu(menuBar)
        logs = tk.Menu(menuBar)

        logs.add_command(label="Show Time Logs", command=lambda:messagebox.showinfo("", open("TimeClockInfo.csv").read()))
        menuBar.add_cascade(label="Logs", menu=logs)

        debug.add_command(label="Perform Login Setup", command=lambda: loginSetup())
        debug.add_command(label="Get JWT", command=lambda: messagebox.showinfo("", getJWT()))
        debug.add_command(label="Set State: Clocked In", command=lambda: clockIn("StateSet"))
        debug.add_command(label="Set State: Clocked Out", command=lambda: clockOut("StateSet"))
        menuBar.add_cascade(label="Debug", menu=debug)


        self.MainGUI.configure(background="#707ec9", borderwidth=5, height=250, relief="ridge", menu=menuBar )
        self.MainGUI.configure(width=400)
        self.MainGUI.title("Time Clock Manager")

        #Starts the clock face shown in the GUI
        self.time()

        #Starts the internet checker GUI element
        self.internetCheck()

        # Main widget
        self.mainwindow = self.MainGUI

#When run, if the user doesn't have a login setup, open the Login Creation Window along with the main window
    def run(self):
        if (keyring.get_password("TimeClockManager", "username") is None):
            LoginCreator().run()
        self.mainwindow.mainloop()

    def buttonClick(self, buttonType):
        if(buttonType == 1):
            # Run Clock In Function, Print Time, Append Time to Log
            if(clockStateCheck(buttonType) == True):
                if(messagebox.askyesno("Caution", "Are you sure you wish to Clock In?") == True):
                    if (clockIn(getJWT()) == True):
                        self.clockState.configure(text="Current State: Clocked In", background="#00c900")
                        messagebox.showinfo("Clocked In!", "Clocked in at: " + strftime('%I:%M:%S %p'))

        elif(buttonType == 2): 
            # Run Clock Out Function, Print Time, Append Time to Log
            if(clockStateCheck(buttonType) == True):
                if(messagebox.askyesno("Caution", "Are you sure you wish to Clock Out?") == True):
                    if (clockOut(getJWT()) == True):
                        self.clockState.configure(text="Current State: Clocked Out", background="#c9000b")
                        messagebox.showinfo("Clocked Out!", "Clocked out at: " + strftime('%I:%M:%S %p'))

            
        # Go to the Time Clock Website without logging in
        elif(buttonType == 3):
            goSite()

#Sets up the clock face and increments it every second
    def time(self):
        string = strftime('%I:%M:%S %p')
        self.clockFace.config(text = string)
        self.clockFace.after(1000, self.time)

    def clockStateSetter(self):
        filename = "TimeClockInfo.csv"
        fields = ['Debug', 'Name', 'Date', 'Time', 'AuthCheck', 'State']
        if(not exists(filename)):
            with open (filename, "a+", newline='') as csvFile:
                csvwriter = csv.writer(csvFile)
                csvwriter.writerow(fields)
            self.clockState.configure(background="#707ec9", text="Current State:")
        else:
            with open (filename, 'r', newline='') as csvFile:
                csvreader = csv.reader(csvFile)
                csvreader = list(csvreader)
                if ((csvreader[-1][-1]) == "Clocked In"):
                    self.clockState.config(text="Current State: Clocked In", background="#00c900")
                elif ((csvreader[-1][-1]) == "Clocked Out"):
                    self.clockState.config(text="Current State: Clocked Out", background="#c9000b")

    #Checks for an internet connection. Initially checks the actual timeclock, then checks google on failure.
    def internetCheck(self):
        self.internetState.after(3600000, self.internetCheck)
        timeout = 1
        try:
            requests.head("https://clock.payrollservers.us", timeout=timeout)
            self.internetState.config(background="#707ec9", text = '')
            return 1
        except requests.ConnectionError:
            try:
                requests.head("https://www.google.com/", timeout=timeout)
                self.internetState.config(background="#ffb900", text = 'WARNING: Payroll Server Offline')
                return 2
            except requests.ConnectionError:
                self.internetState.config(background="#c9000b", text = 'ERROR: No Internet Connection')
                return 0


class LoginCreator:
    def __init__(self, master=None):
        # build ui
        self.CredentialEntry = tk.Tk() if master is None else tk.Toplevel(master)
        self.CredentialEntry.title("Login Entry")
        self.loginMessage = tk.Message(self.CredentialEntry)
        self.loginMessage.configure(
            anchor="w", background="#707ec9", font="{Arial} 20 {}", justify="left"
        )
        self.loginMessage.configure(
            text="Please input your login credentials and then press submit.", width=300
        )
        self.loginMessage.place(anchor="nw", relwidth=0.9, relx=0, rely=0, x=0, y=0)
        self.userNameEntry = tk.Entry(self.CredentialEntry)
        self.userNameEntry.configure(background="#c0c9c4")
        self.userNameEntry.place(
            anchor="nw", relwidth=0.30, relx=0.4, rely=0.45, x=0, y=0
        )
        self.userNameLabel = tk.Label(self.CredentialEntry)
        self.userNameLabel.configure(
            background="#707ec9", font="{Arial} 12 {}", text="Username"
        )
        self.userNameLabel.place(anchor="nw", relx=0.05, rely=0.45, x=0, y=0)
        self.passwordEntry = tk.Entry(self.CredentialEntry, show='*')
        self.passwordEntry.configure(background="#c0c9c4")
        self.passwordEntry.place(
            anchor="nw", relwidth=0.30, relx=0.4, rely=0.60, x=0, y=0
        )
        self.passwordLabel = tk.Label(self.CredentialEntry)
        self.passwordLabel.configure(
            background="#707ec9", font="{Arial} 12 {}", text="Password"
        )
        self.passwordLabel.place(anchor="nw", relx=0.05, rely=0.60, x=0, y=0)
        self.passwordReEntry = tk.Entry(self.CredentialEntry, show='*')
        self.passwordReEntry.configure(background="#c0c9c4")
        self.passwordReEntry.place(
            anchor="nw", relwidth=0.30, relx=0.4, rely=0.75, x=0, y=0
        )
        self.passwordReLabel = tk.Label(self.CredentialEntry)
        self.passwordReLabel.configure(
            background="#707ec9", font="{Arial} 12 {}", text="Reenter Password"
        )
        self.passwordReLabel.place(anchor="nw", relx=0, rely=0.75, x=0, y=0)
        self.submitButton = tk.Button(self.CredentialEntry)
        self.submitButton.configure(
            cursor="pointinghand", highlightbackground="#707ec9", text="Submit"
        )
        self.submitButton.place(anchor="nw", relx=0.68, rely=0.87, x=0, y=0)
        self.submitButton.configure(command=self.buttonClick)
        self.CredentialEntry.configure(
            background="#707ec9", borderwidth=5, height=250, relief="ridge"
        )
        self.CredentialEntry.configure(width=300)

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
