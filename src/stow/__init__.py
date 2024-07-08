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

raw_patterns=config.get("raw_patterns", [])

gitignore=config.get("gitignore", {})

gitignore_enable=gitignore.get("enable", False)

if gitignore_enable:
    gitignore_prepend=gitignore.get("prepend", [])
    gitignore_append=config.get("append", [])

    raw_patterns.extend(gitignore_prepend+open(os.path.join(config["localDir"],".gitignore"),"r").read().splitlines()+gitignore_append)


if raw_patterns:
    command.extend([f"--{'include' if _[0]=='!' else 'exclude'}={_}{'*' if _.endswith(os.path.sep) else ''}" for _ in raw_patterns])

exclude=config.get("exclude",[])
command.extend([f"--exclude={_}" for _ in exclude])

include=config.get("include",["*"]) #By default, get everything

parent_dirs=[]

for path in include:
    curr=Path(path).parent
    while True:
        if str(curr)==".":
            break
            
        parent_dirs.append(str(curr))
        
        curr=curr.parent

command.extend([f"--include={_+os.path.sep}" for _ in parent_dirs])
command.extend([f"--include={_}" for _ in include])
command.append("--exclude=*")

remoteDir=config.get("remoteDir",config["localDir"])

if args.dry_run:
    command.append("-n")
    
command.append(f'{config["remoteHost"]}:{remoteDir+os.path.sep}')
command.append(".")

def main():
    subprocess.run(command,cwd=os.path.expanduser(config["localDir"]))
    print(command)
