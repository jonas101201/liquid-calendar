#!/usr/bin/env python3
"""Per-user source installer. Does not open or modify the calendar database."""
from pathlib import Path
import argparse
import datetime
import os
import shutil
import subprocess
import sys
import venv

SOURCE=Path(__file__).resolve().parent
FILES=['app.py','logic.py','store.py','launch.sh','README.md','VERSION','requirements.txt','LICENSE','NOTICE','THIRD_PARTY.md','CHANGELOG.md','KNOWN_ISSUES.md','qml','icons','companion-widget']

def desktop_quote(value):
    # Desktop Entry Exec quoting is distinct from shell quoting.
    return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'

def install(with_widget=False):
    if not (3,10)<=sys.version_info[:2]<(3,15):
        raise SystemExit('Python 3.10–3.14 is required for this beta.')
    home=Path.home()
    data=home/'.local/share'
    target=data/'liquid-glass-planner'
    widget=data/'plasma/plasmoids/org.jonas.liquidglass.calendar'
    version=(SOURCE/'VERSION').read_text(encoding='utf-8').strip()
    for name in FILES:
        if not (SOURCE/name).exists():raise SystemExit('Missing release file: '+name)
    if SOURCE==target:raise SystemExit('Run this installer from the extracted release folder, not the installed app directory.')
    # Prepare dependencies before replacing any existing app or widget files.
    environment=target/'.venvs'/version
    venv.EnvBuilder(with_pip=True).create(environment)
    python=environment/'bin/python'
    subprocess.run([str(python),'-m','pip','install','--disable-pip-version-check','-r',str(SOURCE/'requirements.txt')],check=True)
    subprocess.run([str(python),'-c','from PySide6.QtCore import __version__; from PySide6.QtQuick import QQuickWindow; print("Qt runtime:", __version__)'],check=True)
    backup=target/'backups'/('before-'+version+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    existing=[name for name in FILES if (target/name).exists()]
    applications=data/'applications'
    entry=applications/'org.jonas.liquidcalendar.desktop'
    if existing or widget.exists() or entry.exists():
        backup.mkdir(parents=True,exist_ok=True)
        for name in existing:
            p=target/name
            if p.is_dir():shutil.copytree(p,backup/name)
            else:shutil.copy2(p,backup/name)
        if widget.exists():shutil.copytree(widget,backup/'widget')
        if entry.exists():shutil.copy2(entry,backup/entry.name)
    target.mkdir(parents=True,exist_ok=True)
    for name in FILES:
        p=SOURCE/name
        if p.is_dir():shutil.copytree(p,target/name,dirs_exist_ok=True)
        else:shutil.copy2(p,target/name)
    (target/'launch.sh').chmod(0o755)
    if with_widget or widget.exists():
        shutil.copytree(SOURCE/'companion-widget',widget,dirs_exist_ok=True)
    applications.mkdir(parents=True,exist_ok=True)
    entry.write_text('[Desktop Entry]\nType=Application\nName=Liquid Calendar Beta\nComment=Local calendar, tasks and reminders — '+version+'\nExec='+desktop_quote(target/'launch.sh')+'\nIcon='+str(target/'icons/calendar.svg')+'\nTerminal=false\nCategories=Office;Calendar;\nStartupNotify=true\n',encoding='utf-8')
    (environment/'.ready').write_text(version+'\n',encoding='utf-8')
    print('Installed Liquid Calendar '+version+'. Search for Liquid Calendar Beta in the application menu.')
    print('Your calendar database has not been opened or modified by this installer.')
    if with_widget or widget.exists():print('Add Liquid Glass Calendar (Beta) in Plasma, or reload an existing widget when convenient. Use Connect in the app if prompted.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--with-widget',action='store_true',help='also install the optional Plasma widget; existing widgets are updated automatically')
    args=parser.parse_args()
    try:install(args.with_widget)
    except (OSError,subprocess.CalledProcessError) as error:raise SystemExit('Installation failed: '+str(error)) from error

if __name__=='__main__':main()
