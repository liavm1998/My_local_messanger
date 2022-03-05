from tkinter import *
from user.module import user_module


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
        self.module.connect(('192.168.56.1', 50000), self.user_name)
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

    def push(self, label: str):
        message = Label(master=self.cf, text=label)
        message.pack()
        self.cf.pack()


class send_button:
    def __init__(self, window: Tk, f):
        self.sb = Button(master=window, text="send", command=f)

    def pack(self):
        self.sb.grid(row=2, column=3)

    def on_click(self):
        pass


class refresh_button:
    def __init__(self, window: Tk):
        self.rb = Button(master=window, text="refresh", command=self.on_click())

    def pack(self):
        self.rb.grid(row=2, column=2)

    def on_click(self):
        pass
