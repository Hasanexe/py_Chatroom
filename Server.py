#Cem Gulboy, Hasan Bagci, Elif Fer, Iris Sirin
#Server Side

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
import random
import time
sock = None
clients = []
nicknames = []

def broadcast(msg,sender):
    for client in clients:
        if client != sender:
            client.send(msg.encode('utf-8'))

def listen (connection,address,nickname,K_aes,K_hmac,iv):
    while True:
        try:            
            msg = connection.recv(1024).decode("utf-8")
            msg = nickname + ": " + msg
            listbox1.insert(END,msg)
            listbox1.yview(END)
            broadcast(msg,connection)
        except:
            listbox1.insert(END,nickname + " disconnected")
            listbox1.yview(END)
            index = clients.index(connection)
            clients.remove(connection)
            connection.close()
            nicknames.remove(nicknames[index])
            break
        if not msg:
            break

def login(name,password):
    users = []
    file = open("users.txt", "r")
    for line in file:
        line = line.strip()
        salt = line.split("\t")[1]
        hashedPass = line.split("\t")[2]
        if name in nicknames:
            return 3
        if line.split("\t")[0].lower() == name:
            if hashedPass == SHA256.new((password+salt).encode("utf-8")).hexdigest():
                file.close()
                return 0
            else:
                file.close()
                return 2
    file.close()
    return 1

def connect ():
    global sock
    sock = socket(AF_INET,SOCK_STREAM)
    sock.bind(("localhost",int(textPort.get())))
    sock.listen(5)
    listbox1.insert(END,"Server has started on port: "+textPort.get())
    listbox1.yview(END)
    while True:
        connection,address = sock.accept()
##        listbox1.insert(END,"Connection from ", address)
##        listbox1.yview(END)
##        connection.send("nick".encode('utf-8'))
        
        E = Curve.get_curve('secp256k1')# Pick Eliptic Curve
        n = E.order                     #Pick Group
        P = E.generator                 #Pick Generator
        sB = random.randint(2, n-1)     #Create Secret For Server(B) (Random num from group)
        pB = sB * P                     #Create Public for Server(B)

        
        pA = connection.recv(2048).decode("utf-8") #Receive Public A
        x,y = pA.split("|<<>>|")
        pA = Point(int(x), int(y),E)        #Merge Public A

        
        data = str(pB.x)+"|<<>>|"+str(pB.y)
        connection.sendall(data.encode('utf-8')) #Send Public B
        
        KAB = sB * pA               #Calculate Shared KEY
        #K = SHA3_256.new(KAB.x.to_bytes((KAB.x.bit_length() + 7) // 8, byteorder='big')+b'TOP SECRET')

        K_aes = SHA3_256.new((str(KAB.x)+'TOP SECRET'+str(KAB.y)).encode("utf-8")).hexdigest()
        K_hmac = SHA3_256.new((str(KAB.y)+'HMAAACCCC'+str(KAB.x)).encode("utf-8")).hexdigest()


        ## ------------------Begin AES
        iv = connection.recv(1024)

        key = bytes(K_aes[0:32], "utf-8")
        cipher = AES.new(key, AES.MODE_CBC, iv)

        
        listbox1.insert(END,"AES Key Created: "+str(K_aes))
        listbox1.yview(END)
        listbox1.insert(END,"HMAC Key Created: "+str(K_hmac))
        listbox1.yview(END)

        
        data = connection.recv(1024)
        listbox1.insert(END,"Credentials Received(Encrypted): "+str(data))
        listbox1.yview(END)
        data = cipher.decrypt(data)
        credentials = data.decode("utf-8")
        ##print("decmsg = ", unpad(decmsg, AES.block_size))
        nickname,password,dummy = credentials.split("|<<>>|")
        checkLogin = login(nickname.lower(),password)
        if checkLogin == 0:
            connection.send("srvcon".encode('utf-8'))
            nicknames.append(nickname)
            clients.append(connection)
            listbox1.insert(END,nickname + " Connected")
            listbox1.yview(END)
            broadcast(nickname+" Connected",connection)
            t = Thread(target=listen,args=(connection,address,nickname,K_aes,K_hmac,iv))
            t.start()
        elif checkLogin == 2:
            connection.send("Password incorrect".encode('utf-8'))
            listbox1.insert(END,nickname + " login attempt failed")
            listbox1.yview(END)
            connection.close()
        elif checkLogin == 1:
            connection.send("User Not Found".encode('utf-8'))
            listbox1.insert(END,"Someone tried login with following name: "+nickname)
            listbox1.yview(END)
            connection.close()
        elif checkLogin == 3:
            connection.send("User Already Connected".encode('utf-8'))
            listbox1.insert(END,nickname + " Tried to connect again and blocked")
            listbox1.yview(END)
            connection.close()           
                
    sock.close()

def startListening(event=NONE):
    if len(textPort.get())!=0 and textPort.get().isnumeric():
        button1['state'] = DISABLED
        button2['state'] = NORMAL
        t = Thread(target=connect)
        t.start()

def stopListening(event=NONE):
    global sock
    for client in clients:
            client.close()
    sock.close()
    listbox1.insert(END,"Server has stopped listening.")
    listbox1.yview(END)
    button1['state'] = NORMAL
    button2['state'] = DISABLED

def clearTB(event):
    textMsg.set("")

def quitt():
    global sock
    for client in clients:
        client.close()
    #sock.close()
    master.destroy()

master = Tk()
master.title("Server Application")
master.geometry("850x250")

#List Box (Info shows here, right side.)
listFrame = Frame(master)
listFrame.pack(side=RIGHT)

scroll = Scrollbar(listFrame)
scroll.pack(side=RIGHT,fill=Y,padx=10)

listbox1 = Listbox(listFrame,height = 10 , width = 100,yscrollcommand=scroll.set)
listbox1.pack()
scroll.config(command = listbox1.yview)

#Text Frame
framemain= Frame(master)
framemain.pack(side=LEFT)

framePort = Frame(framemain)
framePort.pack()

frameButton = Frame(framemain)
frameButton.pack()

#Label (Port number text)
label1 = Label(framePort,text="Port Number")
label1.pack(side=LEFT)

#Text Box (Enter port number here.)
textMsg = StringVar()
textMsg.set("Enter Port Number")

textPort = Entry(framePort,textvariable=textMsg)
textPort.bind("<FocusIn>",clearTB)
textPort.bind("<Return>",startListening)
textPort.pack(padx=10)

#Button
button1 = Button(frameButton,text='Start Listening',command=startListening)
button1.pack(side=TOP, pady=10)

button2 = Button(frameButton,text='Stop Listening', command=stopListening, state = DISABLED)
button2.pack(side=LEFT)

master.protocol('WM_DELETE_WINDOW', quitt)
mainloop()
