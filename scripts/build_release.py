#!/usr/bin/env python3
"""Build source archives from a strict allowlist; never package user data or Qt binaries."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zipfile

from sync_widget_sources import check_shared

ROOT=Path(__file__).resolve().parents[1]
TOP=['VERSION','app.py','logic.py','store.py','launch.sh','installieren.py','requirements.txt','README.md','ROADMAP.md','LICENSE','NOTICE','THIRD_PARTY.md','CHANGELOG.md','RELEASE_NOTES.md','KNOWN_ISSUES.md','TESTING.md','CONTRIBUTING.md','PUBLISHING.md','.gitignore','.github','qml','icons','companion-widget','tests','scripts','docs']
EPOCH=1793145600  # 2026-10-28 UTC; normalized archive metadata, not file creation times.

def build():
 check_shared(ROOT)
 version=(ROOT/'VERSION').read_text().strip()
 if not version or any(c not in '0123456789abcdefghijklmnopqrstuvwxyz.-' for c in version):raise ValueError('Invalid version')
 stem='liquid-calendar-'+version
 files={}
 for name in TOP:
  path=ROOT/name
  if not path.exists():raise FileNotFoundError(path)
  for file in sorted(path.rglob('*')) if path.is_dir() else [path]:
   relative=file.relative_to(ROOT)
   if '__pycache__' in relative.parts or file.suffix in ['.pyc','.pyo']:continue
   if file.is_symlink():raise ValueError('Symlinks are not allowed: '+str(relative))
   if not file.is_file():continue
   if file.suffix in ['.sqlite','.db','.log'] or any(p in relative.parts for p in ['backups','runtime','.venv','.venvs','.git']):raise ValueError('Private/runtime content: '+str(relative))
   data=file.read_bytes()
   if any(marker in data for marker in [str(ROOT.parent.parent).encode()+b'/', b'sk-'+b'proj-', b'gh'+b'p_']):raise ValueError('Unexpected local path or credential marker: '+str(relative))
   files[relative.as_posix()]=data
 manifest=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items()))
 files['MANIFEST.sha256']=manifest.encode()
 out=ROOT/'dist';out.mkdir(exist_ok=True)
 with (out/(stem+'.tar.gz')).open('wb') as raw:
  with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=EPOCH) as gz:
   with tarfile.open(fileobj=gz,mode='w') as tar:
    for name,data in sorted(files.items()):
     info=tarfile.TarInfo(stem+'/'+name);info.size=len(data);info.mtime=EPOCH;info.uid=info.gid=0;info.uname=info.gname='';info.mode=0o755 if name.endswith('.sh') else 0o644
     tar.addfile(info,io.BytesIO(data))
 with zipfile.ZipFile(out/(stem+'.zip'),'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(stem+'/'+name,date_time=(2026,10,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=((0o100755 if name.endswith('.sh') else 0o100644)<<16)
   archive.writestr(info,data)
 sums=''.join(hashlib.sha256((out/(stem+ext)).read_bytes()).hexdigest()+'  '+stem+ext+'\n' for ext in ['.tar.gz','.zip'])
 (out/'SHA256SUMS').write_text(sums)
 (out/'release.json').write_text(json.dumps({'version':version,'tag':'v'+version,'title':'Liquid Calendar '+version.replace('-beta.',' Beta '),'prerelease':True,'assets':[stem+'.tar.gz',stem+'.zip','SHA256SUMS'],'fresh_account_installation_test':'skipped at user request'},indent=2)+'\n')
 print('Built',len(files),'source files in',out)
 print(sums,end='')

if __name__=='__main__':build()
