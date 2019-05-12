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
from os import mkdir, walk
from shutil import copy2
from datetime import datetime
from platform import system
from sys import argv
# from tkinter import Tk, Entry, Label, IntVar, Checkbutton, Button, W, E
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


class Cli:

    def __init__(self):
        self.helptxt = """
            Usage: smartbackup.py -s [source] -d [destination] [options]

            Options:
                -s          Source of the directory you want to backup  (REQUIRED)
                -d          Destination of the directory you want to copy to (REQUIRED)
                -h          Specify hash type to use for file validation
                                Supported hash types: MD5, SHA1, SHA224, SHA256, SHA384, SHA512
                -a          Skip "smart" detection, copy all files regardless of changes
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
        self.current_date = datetime.now()
        self.verbosity = 1
        self.log_error = False

    # Get all the switches used in the command line
    def check_switches(self):
        # The minimum arguments needed is 5. If there are less than 5, print the help text
        if len(argv) < 5:
            print(self.helptxt)
            raise SystemExit
        # Else if 5 or more args are provided, get the values of the args and continue
        # Max number of args is 17, since q and v cannot be used together
        elif len(argv) < 18:
            # Dictionary assigned with all args and their values
            count = 0
            for i in range(1, len(argv)):
                if "-" in argv[i] and len(argv[i]) == 2:
                    if any(x in argv[i] for x in self.switches):
                        if argv[i] == "-a":
                            self.args[argv[i]] = True
                            count += 1
                        elif argv[i] == "-q":
                            self.args[argv[i]] = True
                            self.verbosity = 0
                            count += 1
                        elif argv[i] == "-v":
                            self.args[argv[i]] = True
                            count += 1
                            self.verbosity = 2
                        else:
                            self.args[argv[i]] = argv[i + 1]
                    else:
                        print(f"Bad option {argv[i]}. Quitting")
                        raise SystemExit
            # check if the args dictionary matches what was given in the command
            # Minus 1 because we don't count the name of the program, add the count value back for correct number
            if len(self.args) * 2 != len(argv) - 1 + count:
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
                # Else, if the source directory does not include a forward slash at the end of the directory
                if "/" not in list(self.args["-s"])[-1] and '\\' not in list(self.args["-s"])[-1]:
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
                # If the destination directory does not include a forward slash at the end of the directory
                if "/" not in list(self.args["-d"])[-1] and "\\" not in list(self.args["-d"])[-1]:
                    # Print error, but continue
                    verbose_print("Missing slash at the end of destination directory. "
                                  "Please add a slash at the end of the destination directory next time", 1)
                    # Append a slash to the destination directory
                    self.args["-d"] = self.args["-d"] + slash
        else:
            print("Too many arguments. Quitting")
            raise SystemExit


def write_log(msg, path):
    now = datetime.now()
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
    # try:
    #     if gui.verbosity >= level:
    #         print(msg)
    #         return
    # except NameError:
    #     pass


# Get baseline of all contents in folder
def get_baseline(folder):
    temp_baseline = {}
    dir_list = []
    for (dirpath, dirnames, filenames) in walk(folder):
        temp = []
        for dirs in dirnames:
            # Don't need to append dirs to the list since the recursive get already does that
            dir_list.append(dirs)
        for file in filenames:
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


def get_len(array):
    length = 0
    for item in array:
        length += len(array[item])
    return length


def get_hashes(contents, algorithm="sha1"):
    hashes = []
    ln = get_len(contents)
    progress = 0
    printprogressbar(0, ln, prefix='Progress:', suffix='Complete', length=50)
    for key in contents:
        for thing in contents[key]:
            file = key + slash + thing
            verbose_print("Hashing " + file, 2)
            hsh = get_hash_type(algorithm)
            try:
                with open(file, "rb") as f:
                    while True:
                        data = f.read(65536)
                        if not data:
                            break
                        hsh.update(data)
                digest = hsh.hexdigest()
                if digest not in hashes:
                    hashes.append(digest)
            except UnicodeDecodeError:
                verbose_print(f"Cannot decode {file}: skipping", 1)
            except PermissionError:
                verbose_print(f"Permission Error for file {file}: skipping", 1)
            except OSError:
                verbose_print(f"OS Error for {file}: skipping", 1)
            printprogressbar(progress + 1, ln, prefix='Progress:', suffix='Complete', length=50)
            progress += 1
    return frozenset(hashes)


def compare_hashes(folder, baseline_hashes, algorithm="sha1"):
    num_dirs = []
    contents = {}
    for (dirpath, dirnames, filenames) in walk(folder):
        temp = []
        for dirs in dirnames:
            num_dirs.append(dirs)
        for file in filenames:
            rf = folder + slash + file
            hsh = get_hash_type(algorithm)
            try:
                with open(rf, "rb") as f:
                    while True:
                        data = f.read(65536)
                        if not data:
                            break
                        hsh.update(data)
                if hsh.hexdigest() not in baseline_hashes:
                    verbose_print(f"New Hash found for file {str(file)}", 1)
                    temp.append(file)
            except UnicodeDecodeError:
                verbose_print(f"Cannot decode {rf}: skipping", 1)
            except PermissionError:
                verbose_print(f"Permission error for {rf}: skipping", 1)
            except OSError:
                verbose_print(f"OS Error for {rf}: skipping", 1)
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
    length = get_len(contents)
    progress = 0
    try:
        # Create the main backup folder
        verbose_print(f"Creating folder {destination}", 1)
        mkdir(destination)
    except FileNotFoundError:
        print(f"Error, could not make directory {destination}. "
              f"Path may be wrong. Make sure your destination already exists")
        raise SystemExit
    except FileExistsError:
        verbose_print("Backup for today found. Creating new backup", 1)
        dest_n = str(int(destination.split(".")[-1]) + 1)
        copyfiles(contents, source, destination.split(".")[0]+"."+dest_n)
        return
    printprogressbar(0, length, prefix='Progress:', suffix='Complete', length=50)
    for key in contents:
        source_replaced = key.replace(source, "")
        try:
            verbose_print(f"Creating folder {destination}{slash}{source_replaced}", 1)
            mkdir(destination + slash + source_replaced)
        except FileNotFoundError:
            pass
            verbose_print(f"Error, could not make directory {destination}{slash}{source_replaced}", 1)
        except FileExistsError:
            pass
            verbose_print(f"Error: Folder already exists: {destination}{slash}{source_replaced}", 1)
        for file in contents[key]:
            try:
                verbose_print(f"Copying {file}", 2)
                copy2(key + slash + file, destination + slash + source_replaced)
            except PermissionError:
                verbose_print(f"Permission Error copying {file}", 1)
            except OSError:
                verbose_print(f"Invalid argument: {destination}{slash}{source_replaced}, "
                              f"possibly file of zero size. Skipping.", 1)
            printprogressbar(progress+1, length, prefix='Progress:', suffix='Complete', length=50)
            progress += 1


# Get the OS type (Windows, Mac, Linux)
platf = system()
if platf is "Windows":
    slash = "\\"
else:
    slash = "/"
if __name__ == '__main__':
    # If the program is run with no arguments, run as GUI application
    if len(argv) == 1:
        cli = Cli()
        print(cli.helptxt)
        raise SystemExit
        # root = Tk()
        # gui = Gui(root)
        # root.mainloop()
    # If there are arguments provided, run as CLI program
    elif len(argv) > 1:
        cli = Cli()
        # Check that the program was run with valid switches and arguments
        # This also maps the arguments to a dictionary
        cli.check_switches()
        cli.src = cli.args["-s"]
        cli.dst = f'{cli.args["-d"]}{str(cli.current_date.year)}-{str(cli.current_date.month)}-' \
            f'{str(cli.current_date.day)}.1'
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
                if get_len(cli.source_contents) > 0:
                    verbose_print("Copying contents to destination", 1)
                    copyfiles(cli.source_contents, cli.src, cli.dst)
                    verbose_print("Done", 1)
                    raise SystemExit
                else:
                    verbose_print("No files have been changed. Exiting.", 0)
                    raise SystemExit
            else:
                verbose_print("No Baseline Contents. Exiting", 0)
                raise SystemExit
    else:
        print("Fatal Error: No arguments provided.")
