# smartbackup  
  
Create a differential or full backup of a source directory to a destination directory. Tested in Windows but should work in Linux and MacOS as well.
  
## Requirements  
  
Python 3.6 or greater  
  
## Usage  
  
`py smartbackup.py -s [Path to Source] -d [Path to Destination] [Options]` 
  
Options  
`-s`  Source of the directory you want to backup (REQUIRED)  
`-d`  Destination of the directory you want to copy to (REQUIRED)  
`-h`  Specify hash type to use for file validation. Defaults to SHA1. Available algorithms is dependent on python installation  
`-a`  Skip hash comparison, creates a full backup  
`-q`  Run silently, least output mode, faster runtime  
`-v`  Run in verbose mode, output more to console (slower)  
`-l`  Log output to a file. Specify the directory immediately after option. Use with -v to get all output written to file

Note: Directories or files with spaces must use quotations around the entire path.  
  
## Output  
  
A folder will be created in the `destination folder`, named in the format `[currentDate].[iteration]`, where `currentDate` is `yyyy-mm-dd` and `iteration` is the number of times a backup has run in the same day. Iteration will automatically increment with each successive backup in a day.  
  
The whole `source folder` folder tree will be recreated in the destination folder, even if there are no files to copy into them. This is done as a safeguard if subfolders have contents while superfolders have none.
