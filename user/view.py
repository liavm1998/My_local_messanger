import threading
import tkinter.messagebox
from functools import partial
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from user.module import *


class login_menu:
    def __init__(self, address):
        self.user_name = None
        self.module = None
        login = Tk()
        e = Entry(master=login)
        e.pack()
        e.insert(0, "enter user name")

        button = Button(login, text="login", padx=20, pady=10,
                        command=lambda: self.finished_login(e=e, login=login, address=address))
        button.pack()
        login.mainloop()

    def finished_login(self, e: Entry, login: Tk, address):
        self.user_name = e.get()

        self.module = user_module(address, self.user_name)
        # self.module.connect(('192.168.56.1', 50000), self.user_name)  # windows
        self.module.connect(('10.0.2.4', 50000), self.user_name)  # for linox!!!
        login.destroy()


class message_sender:
    def __init__(self, window: Tk):
        self.entry = Entry(master=window, width=100)

    def read(self):
        ans = self.entry.get()
        return ans

    def pack(self):
        self.entry.grid(row=2, column=1)


class chat_frame:
    def __init__(self, window: Tk):
        self.cf = LabelFrame(master=window, width=600, height=600)

    def pack(self):
        self.cf.grid(row=1, column=1)
        self.cf.grid_propagate(False)

    def push(self, label: str):
        message = Label(master=self.cf, text=label)
        message.grid()
        # self.cf.grid()


class send_button:
    def __init__(self, window: Tk, command):
        self.sb = Button(master=window, text="send", command=command)

    def pack(self):
        self.sb.grid(row=2, column=3)

    def on_click(self):
        pass


class refresh_button:
    def __init__(self, window: Tk, command):
        self.rb = Button(master=window, text="refresh", command=command)

    def pack(self):
        self.rb.grid(row=2, column=2)


class MyClientGUI:

    def __init__(self, address):
        self.safe_closing = True
        self.address = address

        login = login_menu(self.address)
        self.login_window = False
        self.module = login.module
        self.user_name = login.user_name
        self.message = None
        self.target = 'broadcast'
        # main window
        self.window = Tk()
        # chat frame
        self.cf = chat_frame(self.window)
        self.cf.pack()
        # message entry
        self.me = message_sender(window=self.window)
        self.me.pack()
        # send button
        write = partial(self.send_message)
        self.sb = send_button(window=self.window, command=write)
        self.sb.pack()
        # choose box
        # combo box
        self.cb = Combobox(self.window, values=["users", "files"])
        self.cb.grid(column=2, row=0)
        # refresh button
        self.rb = refresh_button(window=self.window, command=self.insert_list)
        self.rb.pack()
        # list view
        self.lv = List_view(window=self.window)
        self.lv.pack()
        # download button
        self.db = Button(master=self.window, text="download", command=self.download)
        self.db.grid(column=3, row=3)
        # u connected start listening
        t = threading.Thread(target=self.listen)
        t.start()
        # self.listen()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing())
        self.window.mainloop()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing())



    def download(self):
        if self.cb.get() == "users":
            pass
        try:
            file_name = self.lv.lb.get(self.lv.lb.curselection())
            self.module.download_file(file_name)
        except Exception as err:
            print("file invalid")

    def insert_list(self):
        self.lv.lb.delete(0, END)

        if self.cb.get() == "files":
            self.module.get_file_list()
        else:
            self.module.get_names_list()

    def listen(self):
        while True:
            pkt = self.module.receive()

            self.handle_pkt(pkt)

    def handle_pkt(self, pkt: str):
        layers = pkt.split(',')
        if layers[0] == MSG_TYPE:
            if layers[1] == self.user_name:
                ans = '\n' + 'ME: ' + layers[3]
            else:
                ans = layers[1] + ':' + layers[3]
            self.cf.push(label=ans)
        if layers[0] == RESP_TYPE:
            if layers[1] == 'True':
                ans = "files:,"
            else:
                ans = "names:," + "broadcast"
            list_content = layers[2].split('|')
            first = True
            for s in list_content:
                if first:
                    ans += s
                    ans += ','
                    first = False
                else:
                    ans += s
                    ans += ','
            li = ans.split(',')
            for item in li:
                self.lv.lb.insert(END, item)

    def on_closing(self):
        if not self.safe_closing:
            self.module.exit()
        else:
            self.safe_closing = False

    # def size_alert(self):
    #     ms = tkinter.messagebox.askyesno(title="download", message="size limit exceded do u wish to continue?")
    #     if ms == 0:
    #         self.module.alert_ans("no")
    #     if ms == 1:
    #         self.module.alert_ans("yes")

    def send_message(self):
        if self.cb.get() != "users":
            pass
        self.target = self.lv.lb.get(self.lv.lb.curselection())
        msg = str(self.me.read())
        self.module.send_msg(msg, self.target)


class List_view:
    def __init__(self, window: Tk):
        self.module = user_module
        self.lb = Listbox(window)

    def pack(self):
        self.lb.grid(row=1, column=2)
