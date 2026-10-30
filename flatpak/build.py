#!/usr/bin/env python3
"""Build a local, offline source-only Flatpak after installing its shared BaseApp.
No compiler SDK is needed: the existing KDE runtime supplies Python and tools.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'flatpak/io.github.jonas101201.LiquidCalendar.json'
APP_ID='io.github.jonas101201.LiquidCalendar'
def run(*args,**kwargs):return subprocess.run([str(arg) for arg in args],check=True,**kwargs)
def build(build_dir,out,reuse=False):
    manifest=json.loads(MANIFEST.read_text());branch=manifest['runtime-version']
    base='io.qt.PySide.BaseApp//'+branch;runtime=manifest['runtime']+'//'+branch
    run('flatpak','info',base,stdout=subprocess.DEVNULL)
    run('flatpak','info',runtime,stdout=subprocess.DEVNULL)
    if build_dir.exists():
        metadata=build_dir/'metadata'
        if not reuse or not metadata.exists() or ('name='+APP_ID+'\n') not in metadata.read_text():
            raise SystemExit('Build directory exists. Use a new path, or --reuse-base for a matching initialized directory.')
    else:
        run('flatpak','build-init','--base='+manifest['base'],'--base-version='+branch,build_dir,APP_ID,manifest['runtime'],manifest['runtime'],branch)
    files=build_dir/'files';app=files/'share/liquid-calendar';app.mkdir(parents=True,exist_ok=True)
    for name in ['app.py','logic.py','store.py','desktop_portals.py','VERSION']:
        shutil.copy2(ROOT/name,app/name)
    for name in ['qml','icons']:
        target=app/name
        if target.exists():shutil.rmtree(target)
        shutil.copytree(ROOT/name,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    pairs=[('flatpak/liquid-calendar','bin/liquid-calendar'),('flatpak/'+APP_ID+'.desktop','share/applications/'+APP_ID+'.desktop'),('flatpak/'+APP_ID+'.metainfo.xml','share/metainfo/'+APP_ID+'.metainfo.xml'),('icons/calendar.svg','share/icons/hicolor/scalable/apps/'+APP_ID+'.svg'),('LICENSE','share/licenses/'+APP_ID+'/LICENSE')]
    for source,destination in pairs:
        target=files/destination;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/source,target)
    (files/'bin/liquid-calendar').chmod(0o755)
    if (files/'cleanup-BaseApp.sh').exists():
        run('flatpak','build','--env=BASEAPP_REMOVE_WEBENGINE=1','--env=BASEAPP_DISABLE_NUMPY=1','--env=FLATPAK_DEST=/app',build_dir,'/app/cleanup-BaseApp.sh',stdout=subprocess.DEVNULL)
    run('python3',ROOT/'flatpak/prune_runtime.py',files)
    run('flatpak','build','--env=QT_QPA_PLATFORM=offscreen','--env=QT_QUICK_BACKEND=software',build_dir,'/app/bin/liquid-calendar','--smoke-test')
    if (build_dir/'export').exists():shutil.rmtree(build_dir/'export')
    run('flatpak','build-finish','--command=liquid-calendar',*manifest['finish-args'],build_dir)
    out.mkdir(parents=True,exist_ok=True);repository=out/'repository'
    run('flatpak','build-export',repository,build_dir,'stable')
    version=(ROOT/'VERSION').read_text().strip();arch=subprocess.check_output(['flatpak','--default-arch'],text=True).strip();bundle=out/('liquid-calendar-'+version+'-'+arch+'.flatpak')
    run('flatpak','build-bundle','--runtime-repo=https://flathub.org/repo/flathub.flatpakrepo',repository,bundle,APP_ID,'stable')
    checksum=hashlib.sha256(bundle.read_bytes()).hexdigest()
    (out/'SHA256SUMS').write_text(checksum+'  '+bundle.name+'\n')
    receipt={'app_id':APP_ID,'version':version,'runtime':runtime,'base':base,'runtime_commit':subprocess.check_output(['flatpak','info','--show-commit',runtime],text=True).strip(),'base_commit':subprocess.check_output(['flatpak','info','--show-commit',base],text=True).strip(),'bundle_bytes':bundle.stat().st_size,'sha256':checksum}
    payload=[ROOT/name for name in ['app.py','logic.py','store.py','desktop_portals.py','VERSION','LICENSE','flatpak/liquid-calendar','flatpak/'+APP_ID+'.desktop','flatpak/'+APP_ID+'.metainfo.xml','flatpak/'+APP_ID+'.json']]
    payload += [p for name in ['qml','icons'] for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.pyo']]
    receipt['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(payload)}
    (out/'build-info.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));print('Bundle:',bundle)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build-dir',type=Path);parser.add_argument('--reuse-base',action='store_true');parser.add_argument('--output',type=Path,default=ROOT/'dist/flatpak');args=parser.parse_args()
    if args.build_dir:build(args.build_dir.resolve(),args.output.resolve(),args.reuse_base)
    else:
        with tempfile.TemporaryDirectory(prefix='liquid-calendar-flatpak-') as directory:build(Path(directory)/'build',args.output.resolve())
if __name__=='__main__':main()
