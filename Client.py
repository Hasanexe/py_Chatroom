#Cem Gulboy, Hasan Bagci, Elif Fer, Iris Sirin
#Client Side

from ecpy.curves   import Curve, Point
from ecpy.keys     import ECPublicKey, ECPrivateKey
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Hash import SHA3_256
from Crypto.Hash import HMAC
from tkinter import *
from socket import *
from threading import *
import time
import random

cipher_global = None
sock = None
connected = False

#----------------------------------------------
##K = SHA3_256.new(KAB1.x.to_bytes((KAB1.x.bit_length() + 7) // 8, byteorder='big')+b'TOP SECRET')


def receive(key,iv):
    cipher1 = AES.new(key, AES.MODE_CBC, iv)
    global connected
    global sock
    while True:
        if connected == False:
            break
        try:
            #msg = sock.recv(1024).decode("utf-8")
            
            msg = sock.recv(1024)
            msg = dec(msg,cipher1)
            listbox1.insert(END,msg)
            listbox1.yview(END)
        except ConnectionAbortedError:
            listbox1.insert(END,"Connection Aborted")
            sock.close()
            connected = False
            break
        except:
            listbox1.insert(END,"Server Disconnected")
            listbox1.yview(END)
            sock.close()
            connected = False
            button1['state'] = NORMAL
            button2['state'] = DISABLED
            button3['state'] = DISABLED
            break
        if not msg:
            listbox1.insert(END,"Server Disconnected")
            sock.close()
            connected = False
            button1['state'] = NORMAL
            button2['state'] = DISABLED
            button3['state'] = DISABLED
            break

def enc(msg,cipher):
    data = bytes(msg+"|<<>>|"+'dummy',"utf-8")
    data = pad(data, AES.block_size)
    data = cipher.encrypt(data)
    return data

def dec(msg,cipher):
    data = cipher.decrypt(msg)
    #data = unicode(data, errors='ignore')
    data = data.decode("utf-8",'ignore')
    print(data)
    data,dummy = data.split("|<<>>|")
    return data


def connect(event=NONE):
    global cipher_global
    global connected
    global sock
    if connected == False:
        try:
            sock = socket(AF_INET,SOCK_STREAM)
            sock.connect((textIP.get(),int(textPort.get())))


            iv = get_random_bytes(AES.block_size) #Initialization Vector
            
            E = Curve.get_curve('secp256k1')# Pick Eliptic Curve
            n = E.order                     #Pick Group
            P = E.generator                 #Pick Generator
            sA = random.randint(2, n-1)     #Create Secret For Client(A) (Random num from group)
            pA = sA * P                     #Create Public for client(A)

            
            
            sock.sendall(bytes(str(pA.x)+"|<<>>|"+str(pA.y),"utf-8")) #Send Public A 

            pB = sock.recv(1024).decode("utf-8") #Receive Public B
                               
            x,y = pB.split("|<<>>|")
            pB = Point(int(x), int(y),E) #Merge Public B
            
            KAB = sA * pB               #Calculate Shared KEY

            K_aes = SHA3_256.new((str(KAB.x)+'TOP SECRET'+str(KAB.y)).encode("utf-8")).hexdigest()
            K_hmac = SHA3_256.new((str(KAB.y)+'HMAAACCCC'+str(KAB.x)).encode("utf-8")).hexdigest()
            
            ## ------------------Begin AES
            sock.sendall(iv)
            key = bytes(K_aes[0:32], "utf-8")


            
            cipher = AES.new(key, AES.MODE_CBC, iv)
            cipher_global = cipher
            
            data = bytes(textUsername.get()+"|<<>>|"+textPassword.get()+"|<<>>|"+'dummy',"utf-8")
            data = pad(data, AES.block_size)
            data = cipher.encrypt(data)
            sock.send(data)
##
##            hmac_key = bytes("pass", "utf-8")
##            message = bytes("Elif", "utf-8")
##            hmac = HMAC.new(K_hmac, message, SHA256)
##            print(hmac.hexdigest())

            
            
            msg = sock.recv(1024).decode("utf-8")
            if msg == "srvcon":
                listbox1.insert(END,"Login Successful")
                listbox1.yview(END)
                connected = True
                button1['state'] = DISABLED
                button2['state'] = NORMAL
                button3['state'] = NORMAL
                t = Thread(target=receive,args=(key,iv))
                t.start()
            else:
                listbox1.insert(END,msg)
                listbox1.yview(END)
                sock.close()
        except:
            listbox1.insert(END,"Couldn't Connect, Make sure server is up,")
            listbox1.yview(END)        
    

def disconnect(event=NONE):
    global connected
    global sock
    if connected:
        sock.close()
        connected = False
        button1['state'] = NORMAL
        button2['state'] = DISABLED
        button3['state'] = DISABLED

def sendMessage(event=NONE):
    global cipher_global
    global connected
    if connected:
        global sock
        data = enc(textbox5.get(),cipher_global)
        sock.sendall(data)
        listbox1.insert(END,"You: "+textbox5.get())
        listbox1.yview(END)
        textMsg.set("")

def clearTB(event):
    textMsg.set("")

def quitt():
    global connected
    global sock
    if connected:
        sock.close()
        connected = False
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
