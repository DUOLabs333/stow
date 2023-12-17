#rsync -aP --delete --include="bottom/*" --include="bottom/" --include="kitty/*" --exclude="*" system.ssh:~/Repos/dotfiles/.config/ .
#Include will get all parent directories and add them as seperate include+'/' (the host directory must also have the end slash). Exclude will always go before include (but the --exclude="*" will go at the end)

import subprocess
import json
import argparse
import os
from pathlib import Path

parser=argparse.ArgumentParser(description="Copy files from a source to a target using FILE.")
parser.add_argument("file",metavar="FILE",nargs="?",help="Configuration file.")
parser.add_argument("-d","--dry-run",help="Don't change filesystem, only print what will happen",action="store_true")
args=parser.parse_args()

config=json.load(open(os.path.abspath(args.file),"r"))

command=["rsync","-aP","--delete"]

exclude=config.get("exclude",[])
command.extend([f"--exclude={_}" for _ in exclude])

include=config.get("include",["*"]) #By default, get everything

parent_dirs=[]

for path in include:
    curr=Path(path)
    while True:
        if os.path.sep not in str(curr):
            break
        
        curr=curr.parent
        
        parent_dirs.append(str(curr))

command.extend([f"--include={_+os.path.sep}" for _ in parent_dirs])
command.extend([f"--include={_}" for _ in include])
command.append("--exclude=*")

remoteDir=config.get("remoteDir",config["localDir"])

if args.dry_run:
    command.append("-n")
    
command.append(f'{config["remoteHost"]}:{remoteDir+os.path.sep}')
command.append(".")

print(command)
def main():
    subprocess.run(command,cwd=os.path.expanduser(config["localDir"]))