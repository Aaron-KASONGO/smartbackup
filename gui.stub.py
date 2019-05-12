from tkinter import Tk, Entry, Label, IntVar, Checkbutton, Button, W, E
from threading import Thread
from datetime import datetime


class Gui:
    args = {}
    verbosity = 1

    def __init__(self, master):
        self.current_date = datetime.now()
        self.master = master
        master.title("Smart Backup")
        # master.geometry("640x480")
        master.resizable(True, True)
        master.configure(background='white')
        # Interface variables
        self.heading = Label(master, text="Smart Backup", background="white")
        self.sourceLabel = Label(master, text="Source:", background="white")
        self.source = Entry(master)
        self.destinationLabel = Label(master, text="Destination:", background="white")
        self.destination = Entry(master)
        self.optionLabel = Label(master, text="Options", background="white")
        # Runtime Options
        self.vrs = []
        self.av = IntVar()
        self.qv = IntVar()
        self.vv = IntVar()
        self.a = Checkbutton(master, text="Copy ALL files", variable=self.av, background="white")
        self.q = Checkbutton(master, text="Run Quietly", variable=self.qv, background="white")
        self.v = Checkbutton(master, text="Run Verbosely", variable=self.vv, background="white")
        self.logLabel = Label(master, text="Log to File:", background="white")
        self.log = Entry(master)
        self.hashtypeLabel = Label(master, text="Specify Hash Type:", background="white")
        self.hashtype = Entry(master)

        # Start button
        self.startButton = Button(master, text="Start", command=self.newthread)

        # Place widgets on grid
        self.heading.grid(row=0, column=0, columnspan=2)
        self.sourceLabel.grid(row=2, column=0, sticky=W)
        self.source.grid(row=3, column=0, columnspan=2, sticky=W+E)
        self.destinationLabel.grid(row=5, column=0, sticky=W)
        self.destination.grid(row=6, column=0, columnspan=2, sticky=W+E)
        self.optionLabel.grid(row=8, column=0, columnspan=2)
        self.a.grid(row=9, column=0)
        self.q.grid(row=9, column=1)
        self.v.grid(row=10, column=0)
        self.logLabel.grid(row=11, column=0, sticky=W)
        self.log.grid(row=12, column=0, columnspan=2, sticky=W+E)
        self.hashtypeLabel.grid(row=13, column=0, sticky=W)
        self.hashtype.grid(row=14, column=0, columnspan=2, sticky=W+E)
        self.startButton.grid(row=18, column=0, columnspan=2)

    def newthread(self):
        t = Thread(name='child procs', target=self.start)
        t.start()

    def start(self):
        source = self.source.get()
        if len(source) > 0:
            if slash not in list(source)[-1]:
                self.args['source'] = f"{source}{slash}"
            else:
                self.args['source'] = source
        else:
            return
        dest = self.destination.get()
        if len(dest) > 0:
            if slash not in list(dest)[-1]:
                self.args['dest'] = f"{dest}{slash}"
            else:
                self.args['dest'] = dest
            self.args['copy_dest'] = f'{dest}{str(cli.current_date.year)}-{str(cli.current_date.month)}-{str(cli.current_date.day)}.1'