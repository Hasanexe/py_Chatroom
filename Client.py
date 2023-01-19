#Client Side

from tkinter import *
from socket import *
from threading import *
sock = socket(AF_INET,SOCK_STREAM)


def receive():
    while True:
        try:
            msg = sock.recv(1024).decode("utf-8")
            listbox1.insert(END,msg)
            listbox1.yview(END)
        except ConnectionAbortedError:
            listbox1.insert(END,"Connection Aborted")
            sock.close()
            break
        except:
            listbox1.insert(END,"Unexpected Error")
            listbox1.yview(END)
            sock.close()
            break
        if not msg:
            listbox1.insert(END,"Server Disconnected")
            sock.close()
            break

def connect(event=NONE):
    sock.connect((textIP.get(),int(textPort.get())))
    button1['state'] = DISABLED
    button2['state'] = NORMAL
    button3['state'] = NORMAL
    #msg = sock.recv(1024).decode("utf-8")
    sock.send(bytes(textUsername.get(),"utf-8"))
    t = Thread(target=receive)
    t.start()

def disconnect(event=NONE):
    sock.close()
    button1['state'] = NORMAL
    button2['state'] = DISABLED
    button3['state'] = DISABLED

def sendMessage(event=NONE):
    sock.send(bytes(textbox5.get(),"utf-8"))
    listbox1.insert(END,"You: "+textbox5.get())
    listbox1.yview(END)
    textMsg.set("")

def clearTB(event):
    textMsg.set("")

def quitt():
    sock.close()
    masterClient.destroy()


masterClient = Tk()
masterClient.title("Client Application")
masterClient.geometry("850x250")

#-----------RIGHT SIDE--------------

textMsg = StringVar()
textMsg.set("Enter your message here..")

#List Box
listFrame1 = Frame(masterClient)
listFrame1.pack(side=RIGHT)

listFrame = Frame(listFrame1)
listFrame.pack(side=TOP)

#listFrame TOP
scroll = Scrollbar(listFrame)
scroll.pack(side=RIGHT,fill=Y,padx=3)

listbox1 = Listbox(listFrame,height = 10 , width = 100,yscrollcommand=scroll.set)
listbox1.pack(side=LEFT,pady=5)
scroll.config(command = listbox1.yview)

#BOTTOM
textbox5 = Entry(listFrame1,textvariable=textMsg, width=35)
textbox5.bind("<Return>",sendMessage)
textbox5.bind("<FocusIn>",clearTB)
textbox5.pack(pady=5)

button3 = Button(listFrame1,text='Send',command=sendMessage, width = 10,  state = DISABLED)
button3.pack(pady=5)

#-----------LEFT SIDE--------------

#Frame
frameMain = Frame(masterClient)
frameMain.pack(side=LEFT)

frameIP = Frame(frameMain)
frameIP.pack(pady=2)

framePort = Frame(frameMain)
framePort.pack(pady=2)

frameUsername = Frame(frameMain)
frameUsername.pack(pady=2)

framePassword = Frame(frameMain)
framePassword.pack(pady=2)

frameButtons = Frame(frameMain)
frameButtons.pack(side = BOTTOM)

#Label
label1 = Label(frameIP,text="IP Address")
label1.pack(side=LEFT,padx = 8,ipadx = 7)

label2 = Label(framePort,text="Port Number")
label2.pack(side=LEFT,padx = 8)

label3 = Label(frameUsername,text="Username")
label3.pack(side=LEFT,padx = 8,ipadx = 8)

label4 = Label(frameMain,text="Password")
label4.pack(side=LEFT,padx = 8,ipadx = 10)

#Text Box
textIP = Entry(frameIP,width = 25)
textIP.pack(padx = 5)

textPort = Entry(framePort,width = 25)
textPort.pack(padx = 5)

textUsername = Entry(frameUsername,width = 25)
textUsername.pack(padx = 5)

textPassword = Entry(frameMain,width = 25)
textPassword.pack(padx = 5)

#Button
button1 = Button(frameButtons,text='Connect',width = 10,command=connect)
button1.pack(pady=5)

button2 = Button(frameButtons,text='Disconnect',width = 10,  state = DISABLED,command=disconnect)
button2.pack()

masterClient.protocol('WM_DELETE_WINDOW', quitt)
mainloop()
