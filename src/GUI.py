import tkinter, time
from tkinter import *
from tkinter import messagebox


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
