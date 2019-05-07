"""
MIT License

Copyright (c) 2019 Nathan Horiuchi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import hashlib
import os
import shutil
import datetime
import threading
import platform
import tkinter
from tkinter import *
from pathlib import Path


# Print iterations progress
def printprogressbar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Author: Greenstick on StackOverflow
    Source: https://stackoverflow.com/a/34325723
    Edited to use f-strings
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    # percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    percent = f"{100 * (iteration / float(total)):.{decimals}f}"
    filledlength = int(length * iteration // total)
    bar = fill * filledlength + '-' * (length - filledlength)
    # print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end="\r")
    # Print New Line on Complete
    if iteration == total:
        print()


class Gui:
    args = {}
    verbosity = 1

    def __init__(self, master):
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
        self.beginningLabel = Label(master, text="Specify Beginning Date:", background="white")
        self.beginning = Entry(master)

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
        self.beginningLabel.grid(row=15, column=0, sticky=W)
        self.beginning.grid(row=16, column=0, columnspan=2, sticky=W+E)
        self.startButton.grid(row=18, column=0, columnspan=2)

    def newthread(self):
        t = threading.Thread(name='child procs', target=self.start)
        t.start()

    def start(self):
        pass


class Cli:

    def __init__(self):
        self.helptxt = """
            Usage: smartbackup.py -s [source] -d [destination] [options]

            Options:
                -s          Source of the directory you want to backup  (REQUIRED)
                -d          Destination of the directory you want to copy to (REQUIRED)
                -h          Specify hash type to use for file validation
                                Supported hash types: MD5, SHA1, SHA224, SHA256, SHA384, SHA512
                -b          Specify the beginning date you want to check backups from (yyyy-mm-dd) -- not implemented
                -a          Skip "smart" detection, copy all files regardless of changes
                -u          Specify username for network shares -- not implemented
                -p          Specify password for network shares -- not implemented
                -q          Run silently, no output, faster runtime
                -v          Run verbose, output everything to console (very slow)
                -l          Log output to a file, specify the directory. Use with -v to get all output written to file

            Notes
                Directories or files with spaces must use quotations around the entire path.
            """
        self.switches = ["s", "d", "h", "b", "a", "u", "p", "q", "v", "l"]
        # Stores the args that were provided
        self.args = {}
        self.baseline_contents = {}
        self.source_contents = {}
        self.baseline_hashes = {}
        self.src = ""
        self.dst = ""
        self.current_date = datetime.datetime.now()
        self.verbosity = 1
        self.log_error = False

    # Get all the switches used in the command line
    def check_switches(self):
        # The minimum arguments needed is 5. If there are less than 5, print the help text
        if len(sys.argv) < 5:
            print(self.helptxt)
            raise SystemExit
        # Else if 5 or more args are provided, get the values of the args and continue
        # Max number of args is 17, since q and v cannot be used together
        elif len(sys.argv) < 18:
            # Dictionary assigned with all args and their values
            count = 0
            for i in range(1, len(sys.argv)):
                if "-" in sys.argv[i] and len(sys.argv[i]) == 2:
                    if any(x in sys.argv[i] for x in self.switches):
                        if sys.argv[i] == "-a":
                            self.args[sys.argv[i]] = True
                            count += 1
                        elif sys.argv[i] == "-q":
                            self.args[sys.argv[i]] = True
                            self.verbosity = 0
                            count += 1
                        elif sys.argv[i] == "-v":
                            self.args[sys.argv[i]] = True
                            count += 1
                            self.verbosity = 2
                        else:
                            self.args[sys.argv[i]] = sys.argv[i + 1]
                    else:
                        print(f"Bad option {sys.argv[i]}. Quitting")
                        raise SystemExit
            # check if the args dictionary matches what was given in the command
            # Minus 1 because we don't count the name of the program, add the count value back for correct number
            if len(self.args) * 2 != len(sys.argv) - 1 + count:
                print("Malformed command. Possible spaces in source or destination paths. Use quotations around paths"
                      " if there are spaces.")
                raise SystemExit
            # Check for required switches
            # If a source directory is not specified
            if "-s" not in self.args:
                # Print error and quit the program
                print("Missing -s argument. Please use -s [source] in your command")
                raise SystemExit
            # Else, a source directory is specified
            else:
                # If the source directory uses backslashes
                # if "\\" in self.args["-s"]:
                    # Print error and quit the program
                    # verbose_print("Please do not use '\\', use '/' instead", 1)
                    # self.args["-s"] = self.args["-s"].replace("\\", "/")
                # Else, if the source directory does not include a forward slash at the end of the directory
                if "/" not in list(self.args["-s"][-1]) or '\\' not in list(self.args["-s"][-1]):
                    # Print error, but continue
                    verbose_print("Missing slash at end of source directory. "
                                  "Please add a slash at the end of the source directory next time", 1)
                    # Append a slash to the source directory
                    self.args["-s"] = self.args["-s"] + slash
            # If a destination directory is not specified
            if "-d" not in self.args:
                # Print error and quit the program
                print("Missing -d argument. Please use -s [destination] in your command")
                raise SystemExit
            # Else, a destination directory is specified
            else:
                # If the destination directory uses backslashes
                # if "\\" in self.args["-d"]:
                    # Print error and quit
                    # verbose_print("Please do not use '\\', use '/' instead", 1)
                    # self.args["-d"] = self.args["-d"].replace("\\", "/")
                # If the destination directory does not include a forward slash at the end of the directory
                if "/" not in list(self.args["-d"][-1]) or "\\" not in list(self.args["-d"][-1]):
                    # Print error, but continue
                    verbose_print("Missing slash at the end of destination directory. "
                                  "Please add a slash at the end of the destination directory next time", 1)
                    # Append a slash to the destination directory
                    self.args["-d"] = self.args["-d"] + slash
        else:
            print("Too many arguments. Quitting")
            raise SystemExit


def write_log(msg, path):
    now = datetime.datetime.now()
    write_now = f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}"
    outfile = open(path, "a")
    outfile.write(f"{write_now} - {msg}\n")
    outfile.close()


def verbose_print(msg, level):
    # Determine if cli or gui is running
    try:
        if cli.verbosity >= level:
            print(msg)
            if "-l" in cli.args:
                # Check if a file is specified or a directory is specified
                path = cli.args["-l"]
                pth = Path(path)
                # If a file is specified, write directly
                if pth.is_file():
                    write_log(msg, path)
                # If a directory is specified, write to a default file "smartbackup.log"
                elif pth.is_dir():
                    if "\\" not in list(path)[-1] or "/" not in list(path)[-1]:
                        path = path + slash
                    write_log(msg, f"{path}smartbackup.log")
                # Path is not a directory nor a file, so it must not exist
                else:
                    if not cli.log_error:
                        print("Error: Log path doesn't exist. Writing to script origin directory")
                        write_log("Error: Log path doesn't exist. "
                                  "Writing to script origin directory", "smartbackup.log")
                        cli.log_error = True
                    write_log(msg, "smartbackup.log")
            return
    except NameError:
        pass
    try:
        if gui.verbosity >= level:
            print(msg)
            return
    except NameError:
        pass


# Get baseline of all contents in folder
def get_baseline(folder):
    temp_baseline = {}
    dir_list = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        temp = []
        for dirs in dirnames:
            # print(dirs)
            # Don't need to append dirs to the list since the recursive get already does that
            dir_list.append(dirs)
        for file in filenames:
            # print(file)
            temp.append(file)
        temp_baseline[folder] = temp
        break
    # Recursion
    if len(dir_list) > 0:
        for d in dir_list:
            temp_baseline.update(get_baseline(folder + slash + d))
    return temp_baseline


def get_hash_type(algorithm="sha1"):
    algorithm = algorithm.strip().lower()
    for alg in hashlib.algorithms_guaranteed:
        if algorithm == alg:
            algorithm = eval(compile(f"hashlib.{algorithm}()", '<string>', 'eval'))
            return algorithm
    else:
        verbose_print(f"Error: Invalid hash algorithm type: {algorithm}. Defaulting to sha1", 1)
        algorithm = hashlib.sha1()
        return algorithm


def get_hashes(contents, algorithm="sha1"):
    algorithm = get_hash_type(algorithm)
    verbose_print("Hashing all baseline contents", 1)
    hashes = []
    ln = len(contents)
    printprogressbar(0, ln, prefix='Progress:', suffix='Complete', length=50)
    for i, key in enumerate(contents):
        for thing in contents[key]:
            file = key + slash + thing
            verbose_print("Hashing " + file, 2)
            hsh = algorithm
            try:
                with open(file, "rb") as f:
                    while True:
                        data = f.read(65536)
                        if not data:
                            break
                        hsh.update(data)
                hashes.append(hsh.hexdigest())
            except UnicodeDecodeError:
                verbose_print(f"Cannot decode {file}: skipping", 1)
            except PermissionError:
                verbose_print(f"Permission Error for file {file}: skipping", 1)
            except OSError:
                verbose_print(f"OS Error for {file}: skipping", 1)
        printprogressbar(i + 1, ln, prefix='Progress:', suffix='Complete', length=50)
    return frozenset(hashes)


def compare_hashes(folder, baseline_hashes, algorithm="sha1"):
    algorithm = get_hash_type(algorithm)
    num_dirs = []
    contents = {}
    for (dirpath, dirnames, filenames) in os.walk(folder):
        temp = []
        for dirs in dirnames:
            num_dirs.append(dirs)
        for file in filenames:
            rf = folder + slash + file
            hsh = algorithm
            try:
                with open(rf, "rb") as f:
                    while True:
                        data = f.read(65536)
                        if not data:
                            break
                        hsh.update(data)
                    # for bb in iter(lambda: f.read(4096).encode("utf-8"), b""):
                    #    sha256.update(bb)
                if hsh.hexdigest() not in baseline_hashes:
                    verbose_print("New Hash found for file " + str(file), 1)
                    temp.append(file)
            except UnicodeDecodeError:
                verbose_print("Cannot decode " + rf + ": skipping", 1)
            except PermissionError:
                verbose_print("Permission error for " + rf + ": skipping", 1)
            except OSError:
                verbose_print("OS Error for " + rf + ": skipping", 1)
        # Hiding this part because it needs to create all the dirs and not just dirs that have contents
        # if len(temp) > 0:
        #    contents[folder] = temp
        contents[folder] = temp
        break
    if len(num_dirs) > 0:
        for d in num_dirs:
            contents.update(compare_hashes(folder + slash + d, baseline_hashes))
    return contents


def copyfiles(contents, source, destination):
    try:
        # Create the main backup folder
        verbose_print(f"Creating folder {destination}", 1)
        os.mkdir(destination)
    except FileNotFoundError:
        print(f"Error, could not make directory {destination}. "
              f"Path may be wrong. Make sure your destination already exists")
        raise SystemExit
    except FileExistsError:
        verbose_print("Backup for today found. Creating new backup", 1)
        dest_n = str(int(destination.split(".")[-1]) + 1)
        copyfiles(contents, source, destination+"."+dest_n)
        return
    for key in contents:
        source_replaced = key.replace(source, "")
        try:
            verbose_print(f"Creating folder {destination}{slash}{source_replaced}", 1)
            os.mkdir(destination + slash + source_replaced)
        except FileNotFoundError:
            verbose_print(f"Error, could not make directory {destination}{slash}{source_replaced}", 1)
        except FileExistsError:
            verbose_print(f"Error: Folder already exists: {destination}{slash}{source_replaced}", 1)
        for file in contents[key]:
            try:
                verbose_print(f"Copying {file}", 2)
                shutil.copy2(key + slash + file, destination + slash + source_replaced)
            except PermissionError:
                verbose_print(f"Permission Error copying {file}", 1)
            except OSError:
                verbose_print(f"Invalid argument: {destination}{slash}{source_replaced}, "
                              f"possibly file of zero size. Skipping.", 1)


# Get the OS type (Windows, Mac, Linux)
platf = platform.system()
if platf is "Windows":
    slash = "\\"
else:
    slash = "/"
if __name__ == '__main__':
    # If the program is run with no arguments, run as GUI application
    if len(sys.argv) == 1:
        root = tkinter.Tk()
        gui = Gui(root)
        root.mainloop()
    # If there are arguments provided, run as CLI program
    elif len(sys.argv) > 1:
        cli = Cli()
        # Check that the program was run with valid switches and arguments
        # This also maps the arguments to a dictionary
        cli.check_switches()
        cli.src = cli.args["-s"]
        cli.dst = f'{cli.args["-d"]}{str(cli.current_date.year)}-{str(cli.current_date.month)}-{str(cli.current_date.day)}.1'
        # If the -a switch is used
        if "-a" in cli.args:
            # Get the baseline contents
            verbose_print("Getting content to copy", 1)
            cli.source_contents = get_baseline(cli.src)
            # Copy all files from source to destination
            verbose_print("Copying contents to destination", 1)
            copyfiles(cli.source_contents, cli.src, cli.dst)
            verbose_print("Done", 1)
            raise SystemExit
        else:
            verbose_print("Getting baseline contents", 1)
            cli.baseline_contents = get_baseline(cli.args["-d"])
            if len(cli.baseline_contents) > 0:
                verbose_print("Hashing baseline contents", 1)
                if "-h" in cli.args:
                    cli.baseline_hashes = get_hashes(cli.baseline_contents, cli.args["-h"])
                    verbose_print("Getting list of changed files", 1)
                    cli.source_contents = compare_hashes(cli.src, cli.baseline_hashes, cli.args["-h"])
                else:
                    cli.baseline_hashes = get_hashes(cli.baseline_contents)
                    verbose_print("Getting list of changed files", 1)
                    cli.source_contents = compare_hashes(cli.src, cli.baseline_hashes)
                verbose_print("Copying contents to destination", 1)
                copyfiles(cli.source_contents, cli.src, cli.dst)
                verbose_print("Done", 1)
                raise SystemExit
            else:
                verbose_print("No Baseline Contents. Exiting", 0)
                raise SystemExit

    else:
        print("Fatal Error: No arguments provided.")
