#!/usr/bin/env python3
"""Liquid Calendar: a local desktop planner for the existing Plasma calendar."""
from __future__ import annotations
import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import sys

from PySide6.QtCore import QObject,Signal,Slot,Property,QTimer,QUrl,QLocale,QSaveFile,QIODevice,QCoreApplication,QEvent
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication,QSystemTrayIcon,QMenu,QMessageBox
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtNetwork import QLocalServer,QLocalSocket
from PySide6.QtQuick import QQuickWindow
from logic import (
    MONTHS,
    WEEKDAYS,
    date_hints,
    event_from_template,
    export_ics,
    fingerprint,
    free_slots,
    instances,
    merge_events,
    occurrence_draft,
    occurs,
    parse,
    quick_entry,
    representative,
    search,
    slot_available,
    template_from_event,
    validate,
)
from store import Store,ConflictError
from desktop_portals import DesktopPortals

BASE=Path(__file__).resolve().parent
APP_VERSION=(BASE/'VERSION').read_text(encoding='utf-8').strip()
DATA=Path(os.environ.get('XDG_DATA_HOME',str(Path.home()/'.local/share')))/'liquid-glass-planner'
FLATPAK=bool(os.environ.get('FLATPAK_ID'))
LEGACY_DB=Path.home()/'.local/share/plasmashell/QML/OfflineStorage/Databases/dd9450f249be1bf7e7f3854d39b8b74b.sqlite'
DEFAULT_DB=DATA/'calendar.sqlite' if FLATPAK else LEGACY_DB

class Bridge(QObject):
    changed=Signal(); errorChanged=Signal(); editRequested=Signal('QVariantMap'); noticeChanged=Signal()
    createRequested=Signal('QVariantMap')
    appearanceChanged=Signal()
    def __init__(self,store,smoke=False):
        super().__init__()
        self.store=store
        self._events=store.read()
        self._selected=dt.date.today()
        self._view='today'
        self._query=''
        self._kind='all'
        self._category=-1
        self._agenda_days=14
        self._task_order='default'
        self._planning_filter='all'
        self._error=''
        self._notice=''
        self._undo=None
        self._settings=store.settings()
        self.smoke=smoke
        self._need_widget=FLATPAK and store.path==LEGACY_DB
        self._pending_notifications=set()
        self._portals=DesktopPortals(self) if FLATPAK and not smoke else None
        if self._portals:
            self._portals.notificationFinished.connect(self.notification_finished)
            self._portals.backgroundFinished.connect(self.background_finished)
        self._project_filter='*';self._priority_filter=-1;self._undo_project_filter=None
        self._templates=store.templates()
        if not smoke and not FLATPAK:
            try:
                result=subprocess.run(['/usr/lib64/qt6/bin/qdbus','org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript','var active=false; desktops().forEach(function(d){d.widgets().forEach(function(w){if(w.type==="org.jonas.liquidglass.calendar")active=true;});}); print(active);'],capture_output=True,text=True,timeout=3)
                value=result.stdout.strip().lower()
                if result.returncode!=0 or value not in ['true','false']:raise RuntimeError("Could not reliably determine the widget status.")
                self._need_widget=value=='true'
            except Exception:self._need_widget=(Path.home()/'.local/share/plasma/plasmoids/org.jonas.liquidglass.calendar').exists()
        self._compatible=self.check_compatibility()
        self.reload_timer=QTimer(self);self.reload_timer.timeout.connect(self.reload);self.reload_timer.start(2500)
        self.reminder_timer=QTimer(self);self.reminder_timer.timeout.connect(self.remind)
        if not smoke:self.reminder_timer.start(15000)
    @Property(bool,constant=True)
    def sandboxed(self):return FLATPAK
    @Property(bool,constant=True)
    def sharedStorage(self):return self.store.path==LEGACY_DB
    @Property(str,constant=True)
    def version(self):return APP_VERSION
    @Property('QVariantList',notify=changed)
    def templates(self):return copy.deepcopy(self._templates)
    @Slot(str,result='QVariantMap')
    def quickPreview(self,text):
        try:
            event=quick_entry(text,dt.date.today(),self._selected)
            return {'event':event,'summary':event['date']+' · '+('All day' if event['allDay'] else event['time'])+' · '+str(event['minutes'])+' min','error':''}
        except Exception as e:return {'error':str(e),'summary':''}
    @Slot(str,str,result=bool)
    def saveTemplate(self,name,snapshot):
        try:
            template=template_from_event(name,json.loads(snapshot))
            self._templates=self.store.write_template(template);self.changed.emit();self.note('Event template saved');return True
        except Exception as e:self.fail(e);return False
    @Slot(str)
    def useTemplate(self,ident):
        try:
            self._templates=self.store.templates()
            template=next(t for t in self._templates if t['id']==ident)
            self.createRequested.emit(event_from_template(template,self._selected))
        except Exception as e:self.fail(e)
    @Slot(str,str,str,result=bool)
    def renameTemplate(self,ident,name,snapshot):
        try:
            base=json.loads(snapshot)
            if base['id']!=ident:raise ValueError('Invalid template identity.')
            new=copy.deepcopy(base);new['name']=name.strip()
            self._templates=self.store.write_template(new,base);self.changed.emit();return True
        except Exception as e:self.fail(e);return False
    @Slot(str,str,result=bool)
    def deleteTemplate(self,ident,snapshot):
        try:
            base=json.loads(snapshot)
            if base['id']!=ident:raise ValueError('Invalid template identity.')
            self._templates=self.store.write_template(None,base);self.changed.emit();self.note('Template deleted; events kept');return True
        except Exception as e:self.fail(e);return False
    def fail(self,error):self._error=str(error);self.errorChanged.emit();return ''
    def note(self,text):self._notice=text;self.noticeChanged.emit()
    def check_compatibility(self):
        if not self._need_widget:return True
        try:
            with self.store.connect() as c:row=c.execute('SELECT value FROM state WHERE key=?',('planner-protocol',)).fetchone()
            return bool(row and json.loads(row[0]).get('version')==3)
        except Exception:return False
    @Property(bool,notify=changed)
    def widgetCompatible(self):return self._compatible
    @Slot()
    def refreshWidget(self):
        if self.smoke:return
        if FLATPAK:self.fail("Reload the Plasma widget from the desktop, then reopen the calendar. Flatpak cannot replace the desktop shell.");return
        try:
            env={k:v for k,v in os.environ.items() if k not in ['PYTHONPATH','QT_PLUGIN_PATH','QML_IMPORT_PATH','QML2_IMPORT_PATH','QT_QPA_PLATFORM_PLUGIN_PATH','QT_QUICK_CONTROLS_STYLE','LD_LIBRARY_PATH','LD_PRELOAD']}
            log=DATA/'plasma-reload.log';log.parent.mkdir(parents=True,exist_ok=True)
            with log.open('ab') as output:subprocess.Popen(['plasmashell','--replace'],env=env,stdout=output,stderr=output,start_new_session=True)
            self.note("Reloading desktop calendar …")
        except Exception as e:self.fail(e)
    @Property('QVariantList',notify=changed)
    def events(self):return copy.deepcopy(self._events)
    @Property(str,notify=errorChanged)
    def error(self):return self._error
    @Property(str,notify=noticeChanged)
    def notice(self):return self._notice
    @Property(bool,notify=changed)
    def canUndo(self):return bool(self._undo)
    @Property(str,notify=changed)
    def selected(self):return self._selected.isoformat()
    @Property(str,notify=changed)
    def title(self):return f'{MONTHS[self._selected.month-1]} {self._selected.year}'
    @Property(str,notify=changed)
    def dayTitle(self):return f'{WEEKDAYS[self._selected.weekday()]}, {self._selected.day} {MONTHS[self._selected.month-1]}'
    @Property(str,notify=changed)
    def view(self):return self._view
    @Property(str,notify=changed)
    def query(self):return self._query
    @Property(str,notify=changed)
    def kind(self):return self._kind
    @Property(int,notify=changed)
    def category(self):return self._category
    @Property(int,notify=changed)
    def agendaDays(self):return self._agenda_days
    @Property(str,notify=changed)
    def taskOrder(self):return self._task_order
    @Slot(str)
    def setTaskOrder(self,value):
        if value in ['default','title','duration','planned','priority','project']:
            self._task_order=value;self.changed.emit()
    @Property(str,notify=changed)
    def projectFilter(self):return self._project_filter
    @Property(int,notify=changed)
    def priorityFilter(self):return self._priority_filter
    @Slot(str,int)
    def setTaskFilters(self,project,priority):
        if len(project)<=80 and -1<=priority<=3:
            self._project_filter=project;self._priority_filter=priority;self.changed.emit()
    @Property('QVariantList',notify=changed)
    def projects(self):
        counts={}
        for e in self._events:
            name=e.get('project','')
            if not e['task'] or not name:continue
            count=counts.setdefault(name,dict(name=name,total=0,done=0))
            count['total']+=1;count['done']+=int(e['done'])
        return [counts[name] for name in sorted(counts,key=str.casefold)]
    @Slot(str,str)
    def renameProject(self,name,new_name):
        try:
            new_name=new_name.strip()
            if not name or name=='*' or len(new_name)>80 or new_name=='*':raise ValueError('Enter a project name of up to 80 characters. “*” is reserved.')
            desired=copy.deepcopy(self._events)
            found=False
            for e in desired:
                if e['task'] and e.get('project','')==name:e['project']=new_name;found=True
            if not found:raise ValueError('This project no longer exists.')
            previous_filter=self._project_filter
            if self.commit(desired,label='Project updated',project_name=name) is not None:
                if name!=new_name:self._undo_project_filter=(previous_filter,new_name)
                self._project_filter=new_name;self.changed.emit()
        except Exception as e:self.fail(e)
    @Property(str,notify=changed)
    def planningFilter(self):return self._planning_filter
    @Slot(str)
    def setPlanningFilter(self,value):
        if value in ['all','undated','planned']:
            self._planning_filter=value;self.changed.emit()
    @Slot(str,result='QVariantMap')
    def resolveDate(self,text):
        options=date_hints(text,dt.date.today())
        if len(options)==1:return {'date':options[0]['date'],'error':''}
        return {'date':'','error':"Several dates match. Be more specific." if options else "Enter a valid date, e.g. 2026-11-15, 15.11.2026 or tomorrow."}
    @Slot(int)
    def setAgendaDays(self,days):
        if days in [7,14,30]:self._agenda_days=days;self.changed.emit()
    @Property('QVariantList',notify=changed)
    def agendaItems(self):
        return [v for v in instances(self._events,self._selected,self._agenda_days,'all',self._category) if not(v['task'] and v['done'])]
    @Property('QVariantList',notify=changed)
    def dateHints(self):return date_hints(self._query,dt.date.today())
    @Property(bool,notify=changed)
    def animationsEnabled(self):return bool(self._settings.get('animations',True))
    @Slot(bool)
    def setAnimations(self,enabled):
        try:
            settings=dict(self._settings,animations=enabled)
            self.store.set_settings(settings)
            self._settings=settings
            self.changed.emit()
        except Exception as e:self.fail(e)
    @Property(str,notify=appearanceChanged)
    def accentColor(self):return self._settings.get('accent','#7ceafa')
    @Property(float,notify=appearanceChanged)
    def glassOpacity(self):return float(self._settings.get('glassOpacity',.60))
    @Slot(str,float)
    def setAppearance(self,accent,opacity):
        try:
            if accent not in ['#7ceafa','#8cbcff','#72ebce','#c2adff','#ffa8cf'] or not .60<=opacity<=.96:
                raise ValueError('Choose a supported accent and opacity between 60% and 96%.')
            settings=dict(self._settings,accent=accent,glassOpacity=opacity)
            if settings==self._settings:return
            self.store.set_settings(settings)
            self._settings=settings
            self.appearanceChanged.emit()
        except Exception as e:self.fail(e)
    @Property(str,notify=changed)
    def theme(self):return self._settings.get('theme','dark')
    @Property(bool,notify=changed)
    def remindersEnabled(self):return bool(self._settings.get('reminders',True))
    def autostart_path(self):
        return self.store.path.parent/'autostart-test.desktop' if self.smoke else Path.home()/'.config/autostart/org.jonas.liquidcalendar.desktop'
    @Property(bool,notify=changed)
    def autoStart(self):return bool(self._settings.get('flatpakAutostart',False)) if FLATPAK and not self.smoke else self.autostart_path().exists()
    @Slot(bool)
    def setAutoStart(self,enabled):
        if self._portals:self._portals.set_autostart(enabled);return
        try:
            path=self.autostart_path()
            if enabled:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text('[Desktop Entry]\nType=Application\nName=Liquid Calendar\nExec="'+str(BASE/'launch.sh')+'" --background\nIcon='+str(BASE/'icons/calendar.svg')+'\nTerminal=false\n',encoding='utf-8')
            else:path.unlink(missing_ok=True)
            self.changed.emit()
        except Exception as e:self.fail(e)
    @Property(str,notify=changed)
    def databasePath(self):return str(self.store.path)
    @Property('QVariantList',notify=changed)
    def weekDays(self):
        start=self._selected-dt.timedelta(days=self._selected.weekday())
        rows=[]
        for n in range(7):
            ordinal=start.toordinal()+n
            day=dt.date.fromordinal(ordinal) if dt.date(1000,1,1).toordinal()<=ordinal<=dt.date.max.toordinal() else None
            rows.append({'date':day.isoformat() if day else '', 'name':WEEKDAYS[n][:2].upper(),'number':day.day if day else '—','today':day==dt.date.today()})
        return rows
    @Property('QVariantList',notify=changed)
    def weekItems(self):
        start=self._selected-dt.timedelta(days=self._selected.weekday())
        result=[v for v in instances(self._events,start,7,self._kind,self._category) if not(v['task'] and v['done'])]
        for v in result:v['dayIndex']=(parse(v['date'])-start).days
        return result
    @Property('QVariantList',notify=changed)
    def dayItems(self):return instances(self._events,self._selected,1,self._kind,self._category)
    @Property('QVariantList',notify=changed)
    def tasks(self):return search(self._events,'',self._selected,'open',self._category)
    @Property('QVariantList',notify=changed)
    def results(self):
        rows=search(self._events,self._query,dt.date.today(),self._kind,self._category)
        if self._view=='tasks':
            rows=[v for v in rows if v['task'] and (self._planning_filter=='all' or (self._planning_filter=='undated')==v['unscheduled']) and (self._project_filter=='*' or v['project']==self._project_filter) and (self._priority_filter<0 or v['priority']==self._priority_filter)]
        if self._view=='tasks' and self._task_order!='default':
            rows.sort(key=lambda v:(-v['priority'],v['done'],v['title'].casefold()) if self._task_order=='priority' else (v['project'].casefold(),-v['priority'],v['title'].casefold()) if self._task_order=='project' else (v['minutes'],v['title'].casefold()) if self._task_order=='duration' else (v['unscheduled'],v['date'],v['time'],v['title'].casefold()) if self._task_order=='planned' else (v['title'].casefold(),v['id']))
        return rows
    @Property(int,notify=changed)
    def conflictCount(self):return sum(v['conflict'] for v in instances(self._events,self._selected,1))
    @Slot()
    def reload(self):
        try:
            current=self.store.read();compatible=self.check_compatibility();templates=self.store.templates()
            if current!=self._events or compatible!=self._compatible or templates!=self._templates:self._events=current;self._compatible=compatible;self._templates=templates;self.changed.emit()
        except Exception as e:self.fail(e)
    def commit(self,desired,base=None,label="Saved",allow_occurrences=False,project_name=None,planning_slot=None,unchanged_sources=None):
        if not self._compatible:
            self.fail("Update the desktop calendar using “Connect” first. The app is read-only until connected.");return None
        try:
            before,after=self.store.merge(desired,self._events if base is None else base,allow_occurrences=allow_occurrences,project_name=project_name,planning_slot=planning_slot,unchanged_sources=unchanged_sources)
            self._undo=(before,after) if before!=after else self._undo
            if before!=after:self._undo_project_filter=None
            self._events=after;self._error='';self.errorChanged.emit();self.changed.emit();self.note(label);return after
        except Exception as e:self.fail(e);return None
    @Slot(str,str,result=str)
    def storeJson(self,desired,base):
        try:result=self.commit(json.loads(desired),json.loads(base),allow_occurrences=True)
        except Exception as e:return self.fail(e)
        return json.dumps(result,ensure_ascii=False) if result is not None else ''
    @Slot(float,str)
    def savePreferences(self,opacity,accent):
        try:self.store.preferences(opacity,accent)
        except Exception as e:self.fail(e)
    @Slot(str)
    def setView(self,view):
        if view in ['today','week','month','agenda','tasks','search','settings']:
            if view!=self._view:self._query='';self._kind='tasks' if view=='tasks' else 'all';self._category=-1;self._project_filter='*';self._priority_filter=-1
            self._view=view;self.changed.emit()
    @Slot(str)
    def selectDate(self,date):
        try:self._selected=parse(date);self.changed.emit()
        except Exception as e:self.fail(e)
    @Slot(int)
    def navigate(self,n):
        ordinal=self._selected.toordinal()+n*(7 if self._view=='week' else 1)
        self._selected=dt.date.fromordinal(max(dt.date(1000,1,1).toordinal(),min(dt.date.max.toordinal(),ordinal)));self.changed.emit()
    @Slot()
    def today(self):self._selected=dt.date.today();self.changed.emit()
    @Slot(str)
    def setQuery(self,text):
        if text[:200]!=self._query:self._query=text[:200];self.changed.emit()
    @Slot(str,int)
    def setFilter(self,kind,category):
        if kind in ['all','events','tasks','open','done'] and -1<=category<=3:self._kind=kind;self._category=category;self.changed.emit()
    def merge_source(self,snapshot,base):
        validate([snapshot])
        if snapshot.get('occurrenceOf'):
            parent=next((e for e in base if e['id']==snapshot['occurrenceOf']),None)
            if not parent or snapshot['id'] in {e['id'] for e in base} or fingerprint(parent)!=snapshot.get('originHash'):
                raise ConflictError("The series has changed. Reopen this occurrence.")
            expected=occurrence_draft(parent,snapshot.get('occurrenceDate',''),snapshot['id'])
            if expected!=snapshot:raise ConflictError("This occurrence has changed. Reopen it before merging.")
        else:
            if next((e for e in base if e['id']==snapshot['id']),None)!=snapshot:
                raise ConflictError("An event has changed. Reopen both events before merging.")
            if any(e.get('seriesId')==snapshot['id'] for e in base):
                raise ValueError("Events linked to series occurrences cannot be merged.")
        return snapshot
    def merge_editor_draft(self,source,draft_snapshot):
        if source['task'] or source['repeat']!='none' or source.get('seriesId'):
            raise ValueError("Choose independent events or individual occurrences, not entire series or tasks.")
        if not draft_snapshot:return source
        draft=json.loads(draft_snapshot)
        validate([draft])
        editable={'title','date','time','minutes','allDay','category','location','notes','reminder','repeat','until'}
        identity=lambda entry:{k:v for k,v in entry.items() if k not in editable}
        if identity(draft)!=identity(source):
            raise ValueError("The event identity or series metadata cannot be changed by merging.")
        if draft['task'] or draft['repeat']!='none' or draft.get('seriesId'):
            raise ValueError("Merge individual non-repeating events or occurrences. Keep Repeat set to Once.")
        return draft
    @Slot(str,result='QVariantList')
    @Slot(str,str,result='QVariantList')
    def mergeChoices(self,first_snapshot,draft_snapshot=''):
        try:
            first=self.merge_editor_draft(self.merge_source(json.loads(first_snapshot),self._events),draft_snapshot)
            choices=[]
            for e in self._events:
                if e['task'] or e.get('groupId') or e.get('seriesId') or e['allDay']!=first['allDay'] or not occurs(e,parse(first['date'])):continue
                if e['repeat']!='none':
                    if e['id']==first.get('occurrenceOf') and first['date']==first.get('occurrenceDate'):continue
                    candidate=occurrence_draft(e,first['date'])
                else:
                    if e['id']==first['id'] or any(child.get('seriesId')==e['id'] for child in self._events):continue
                    candidate=copy.deepcopy(e)
                choices.append(candidate)
            return sorted(choices,key=lambda e:(e['time'],e['title'].casefold(),e['id']))
        except Exception as e:self.fail(e);return []
    @Slot(str,str,result='QVariantMap')
    @Slot(str,str,str,result='QVariantMap')
    def mergePreview(self,first_snapshot,second_snapshot,draft_snapshot=''):
        try:
            first=self.merge_editor_draft(self.merge_source(json.loads(first_snapshot),self._events),draft_snapshot)
            second=self.merge_source(json.loads(second_snapshot),self._events)
            return {'events':merge_events(first,second),'error':''}
        except Exception as e:return {'error':str(e)}
    @Slot(str,str,result=bool)
    @Slot(str,str,str,result=bool)
    def mergeEvents(self,first_snapshot,second_snapshot,draft_snapshot=""):
        try:
            base=copy.deepcopy(self._events)
            first=self.merge_source(json.loads(first_snapshot),base)
            second=self.merge_source(json.loads(second_snapshot),base)
            draft=self.merge_editor_draft(first,draft_snapshot)
            merged=merge_events(draft,second)
            replacements={e['id']:e for e in merged}
            desired=[copy.deepcopy(e) for e in base if e['id'] not in replacements]
            for item in merged:
                if item.get('occurrenceOf'):
                    parent=next(e for e in desired if e['id']==item['occurrenceOf'])
                    parent.setdefault('exceptions',{})[item['occurrenceDate']]={'cancelled':True}
                    item['seriesId']=item.pop('occurrenceOf')
                    item['originalDate']=item.pop('occurrenceDate')
                    item.pop('originHash',None)
                desired.append(item)
            source_ids={source.get('occurrenceOf',source['id']) for source in (first,second)}
            originals={event['id']:event for event in base if event['id'] in source_ids}
            return self.commit(desired,base,label="Events linked · Both remain individually editable",allow_occurrences=True,unchanged_sources=originals) is not None
        except Exception as e:self.fail(e);return False
    @Slot(str,result=bool)
    @Slot(str,str,result=bool)
    def unlinkEvents(self,snapshot,draft_snapshot=''):
        try:
            source=json.loads(snapshot)
            base=copy.deepcopy(self._events)
            if next((e for e in base if e['id']==source['id']),None)!=source:
                raise ConflictError("This event has changed. Reopen it before unlinking.")
            draft=json.loads(draft_snapshot) if draft_snapshot else source
            validate([draft])
            editable={'title','date','time','minutes','allDay','category','location','notes','reminder','repeat','until','task','priority','project','checklist','weekdays'}
            if {k:v for k,v in source.items() if k not in editable}!={k:v for k,v in draft.items() if k not in editable}:
                raise ValueError("The event identity cannot be changed by unlinking.")
            group=source.get('groupId')
            if not group:raise ValueError("This event is not linked.")
            originals={e['id']:e for e in base if e.get('groupId')==group}
            desired=[copy.deepcopy(draft if e['id']==source['id'] else e) for e in base]
            for e in desired:
                if e.get('groupId')==group:e.pop('groupId',None)
            return self.commit(desired,base,label="Group unlinked · Both events kept",unchanged_sources=originals) is not None
        except Exception as e:self.fail(e);return False
    @Slot(str,str,bool)
    def edit(self,ident,date,single=True):
        try:
            self.reload();e=next(copy.deepcopy(e) for e in self._events if e['id']==ident)
            if single and e['repeat']!='none':
                draft=occurrence_draft(e,date)
            else:draft=e
            if draft['repeat']=='none':draft.pop('weekdays',None)
            self.editRequested.emit(draft)
        except Exception as e:self.fail(e)
    @Slot(str,str,str,result=bool)
    def deleteOccurrence(self,ident,date,expected):
        try:
            e=next(e for e in self._events if e['id']==ident)
            if fingerprint(e)!=expected:raise ConflictError("The series has changed. Reopen this occurrence.")
            desired=copy.deepcopy(self._events)
            for item in desired:
                if item['id']==ident:item.setdefault('exceptions',{})[date]={'cancelled':True}
            return self.commit(desired,label="Occurrence deleted") is not None
        except Exception as e:self.fail(e);return False
    @Slot(str,str,str)
    def toggleTaskSnapshot(self,ident,date,snapshot):
        try:self.toggleTask(ident,date,fingerprint(json.loads(snapshot)))
        except Exception as e:self.fail(e)
    @Slot(str)
    @Slot(str,str)
    @Slot(str,str,str)
    def toggleTask(self,ident,date='',expected=''):
        try:
            event=next(copy.deepcopy(e) for e in self._events if e['id']==ident)
            if not event['task']:raise ValueError('This entry is not a task.')
            if expected and fingerprint(event)!=expected:
                raise ConflictError('The task has changed. Reopen it.')
            desired=copy.deepcopy(self._events)
            # Old versions could mark the entire parent series done. An explicit
            # reopen of that legacy record reactivates the series without migration.
            if event['repeat']=='none' or event['done']:
                for e in desired:
                    if e['id']==ident:e['done']=not e['done'];break
            else:
                day=parse(date) if date else representative(event,self._selected)
                if day is None or not occurs(event,day):
                    raise ConflictError('This task occurrence no longer exists.')
                child=occurrence_draft(event,day.isoformat())
                child['done']=True
                desired.append(child)
            self.commit(desired,label='Task updated',allow_occurrences=True)
        except Exception as e:self.fail(e)
    @Slot(str,str,str,str)
    def toggleChecklist(self,ident,date,step_id,expected):
        try:
            event=next(copy.deepcopy(e) for e in self._events if e['id']==ident)
            if not event['task'] or fingerprint(event)!=expected:raise ConflictError('The task has changed. Reopen it.')
            desired=copy.deepcopy(self._events)
            target=occurrence_draft(event,date) if event['repeat']!='none' else event
            step=next(item for item in target.get('checklist',[]) if item['id']==step_id)
            step['done']=not step['done']
            if event['repeat']!='none':
                desired.append(target)
            else:
                desired=[target if e['id']==ident else e for e in desired]
            self.commit(desired,label='Checklist updated',allow_occurrences=True)
        except Exception as e:self.fail(e)
    @Slot(str,str,str,int,str)
    def move(self,ident,original,target,minute,expected,as_task=False,planning_slot=None):
        try:
            if not 0<=minute<=1439:raise ValueError("Invalid time.")
            parse(target);e=next(copy.deepcopy(e) for e in self._events if e['id']==ident)
            if fingerprint(e)!=expected:raise ConflictError("The event has changed. Try moving it again.")
            desired=copy.deepcopy(self._events);time=f'{minute//60:02d}:{minute%60:02d}'
            if e['repeat']=='none':
                for item in desired:
                    if item['id']==ident:item.update(date=target,time=time,allDay=False if as_task else item['allDay'])
            else:
                child=occurrence_draft(e,original)
                child.update(date=target,time=time,allDay=False if as_task else e['allDay'])
                desired.append(child)
            self.commit(desired,label="Event rescheduled · overlaps are highlighted in red",allow_occurrences=True,planning_slot=planning_slot)
        except Exception as e:self.fail(e)
    @Slot(str,str,result='QVariantList')
    def slotsFor(self,ident,original):
        try:
            e=next(e for e in self._events if e['id']==ident)
            return free_slots(self._events,self._selected,e['minutes'],ident,original)
        except Exception as e:self.fail(e);return []
    @Slot(str,str,str,result='QVariantList')
    def slotsOn(self,ident,original,date):
        try:
            self.reload()
            e=next(e for e in self._events if e['id']==ident)
            if not e['task'] or e['done']:raise ValueError("Choose an open task.")
            day=parse(date)
            if day<dt.date.today():raise ValueError("Choose today or a future date.")
            return free_slots(self._events,day,e['minutes'],ident,original)
        except Exception as e:self.fail(e);return []
    @Slot(str,str,str,int,str,result=bool)
    def scheduleTask(self,ident,original,date,minute,expected):
        try:
            self.reload()
            e=next(e for e in self._events if e['id']==ident)
            if not e['task'] or e['done']:raise ValueError("The task is no longer open.")
            if fingerprint(e)!=expected:raise ConflictError("The task has changed. Reopen it.")
            if parse(date)<dt.date.today():raise ValueError("Choose today or a future date.")
            if not slot_available(self._events,parse(date),e['minutes'],minute,ident,original):
                raise ConflictError("This time slot is no longer available. Search again.")
            self.move(ident,original,date,minute,expected,True,planning_slot=(parse(date),e['minutes'],minute,ident,original))
            return not bool(self._error)
        except Exception as e:self.fail(e);return False
    @Slot()
    def undo(self):
        if not self._compatible:self.fail("Connect the desktop calendar first.");return
        if not self._undo:return
        try:
            _,after=self.store.patch(*self._undo);self._events=after;self._undo=None
            if self._undo_project_filter and self._project_filter==self._undo_project_filter[1]:self._project_filter=self._undo_project_filter[0]
            self._undo_project_filter=None;self.changed.emit();self.note("Last change undone")
        except Exception as e:self.fail(e)
    @Slot(str)
    def setTheme(self,value):
        if value in ['dark','light','auto']:
            try:
                settings=dict(self._settings,theme=value)
                self.store.set_settings(settings)
                self._settings=settings
                self.changed.emit()
            except Exception as e:self.fail(e);self.changed.emit()
    @Slot(bool)
    def setReminders(self,value):
        try:
            settings=dict(self._settings,reminders=value)
            self.store.set_settings(settings)
            self._settings=settings
            self.changed.emit()
        except Exception as e:self.fail(e)
    @Slot()
    def clearError(self):self._error='';self.errorChanged.emit()
    @Slot(str,str)
    def exportFile(self,url,kind):
        try:
            target=QUrl(url).toLocalFile()
            if not target:raise ValueError("Choose a local file.")
            path=Path(target)
            events=self.store.read()
            text=export_ics(events) if kind=='ics' else json.dumps({'format':'liquid-glass-calendar','version':1,'events':events},ensure_ascii=False,indent=2)
            # QSaveFile keeps an existing export intact until the complete write commits.
            output=QSaveFile(str(path))
            if not output.open(QIODevice.WriteOnly):raise OSError(output.errorString())
            try:
                encoded=text.encode('utf-8')
                if output.write(encoded)!=len(encoded):raise OSError(output.errorString())
                if not output.commit():raise OSError(output.errorString())
            finally:
                if output.isOpen():output.cancelWriting();output.commit()
            self.note("Export saved: "+path.name)
        except Exception as e:self.fail(e)
    @Slot(str)
    def importFile(self,url):
        try:
            path=Path(QUrl(url).toLocalFile())
            if path.stat().st_size>20_000_000:raise ValueError("The backup is too large.")
            data=json.loads(path.read_text(encoding='utf-8'))
            if data.get('format')!='liquid-glass-calendar' or data.get('version')!=1:raise ValueError("Not a compatible JSON backup.")
            imported=validate(data['events'])
            if any(any(k in e for k in ['occurrenceOf','occurrenceDate','originHash']) for e in imported):raise ValueError("A backup must not contain pending series edit commands.")
            ids={e['id'] for e in self._events};new=[e for e in imported if e['id'] not in ids]
            self.commit(self._events+new,label=f'{len(new)} new entries imported; existing IDs preserved')
        except Exception as e:self.fail(e)
    def background_finished(self,ok,autostart,error):
        if not ok:self.fail(error);return
        try:
            settings=dict(self._settings,flatpakAutostart=autostart)
            self.store.set_settings(settings);self._settings=settings;self.changed.emit()
            self.note("Autostart enabled" if autostart else "Autostart disabled")
        except Exception as e:self.fail(e)
    def notification_finished(self,key,ok,error):
        self._pending_notifications.discard(key)
        if ok:
            try:self.store.mark_notified(key)
            except Exception as e:self.fail(e)
        else:self.fail("Could not deliver reminder: "+error)
    def remind(self):
        if not self.remindersEnabled:return
        try:
            self.reload();now=dt.datetime.now()
            for v in instances(self._events,now.date(),2):
                if v['carry'] or v['task'] and v['done']:continue
                lead=v['event'].get('reminder',10)
                if lead<0:continue
                start=dt.datetime.combine(parse(v['date']),dt.time(9) if v['allDay'] else dt.time.fromisoformat(v['time']))
                trigger=start-dt.timedelta(minutes=lead)
                if trigger<=now<=start+dt.timedelta(minutes=5):
                    key=f'{v["id"]}|{v["date"]}|{v["time"]}|{lead}'
                    if key in self._pending_notifications:continue
                    if not self.store.notified(key):
                        if self._portals:
                            body=(("All day today" if start.date()==now.date() else "All day tomorrow") if v['allDay'] else v['time'])+(' · '+v['location'] if v['location'] else '')
                            self._pending_notifications.add(key);self._portals.notify(key,v['title'],body);continue
                        result=subprocess.run(['notify-send','--app-name=Liquid Calendar','--icon='+str(BASE/'icons/calendar.svg'),v['title'],(("All day today" if start.date()==now.date() else "All day tomorrow" if start.date()==now.date()+dt.timedelta(days=1) else "All day on "+v["date"]) if v["allDay"] else v["time"])+(' · '+v['location'] if v['location'] else '')],capture_output=True,timeout=8)
                        if result.returncode==0:self.store.mark_notified(key)
        except Exception as e:self.fail("Could not deliver reminder: "+str(e))

def main():
    parser=argparse.ArgumentParser(prog='liquid-calendar');parser.add_argument('--version',action='version',version='Liquid Calendar '+APP_VERSION);parser.add_argument('--database',type=Path,default=DEFAULT_DB);parser.add_argument('--background',action='store_true');parser.add_argument('--smoke-test',action='store_true');parser.add_argument('--screenshot',type=Path);args=parser.parse_args()
    if args.smoke_test and args.database==DEFAULT_DB:
        import tempfile
        args.database=Path(tempfile.mkdtemp(prefix="liquid-calendar-smoke-"))/"calendar.sqlite"
    QLocale.setDefault(QLocale('en_GB'))
    app=QApplication(sys.argv);app.setApplicationName('Liquid Calendar');app.setApplicationVersion(APP_VERSION);app.setOrganizationName('Jonas');app.setDesktopFileName('io.github.jonas101201.LiquidCalendar' if FLATPAK else 'org.jonas.liquidcalendar');app.setApplicationDisplayName('Liquid Calendar Beta');app.setWindowIcon(QIcon(str(BASE/'icons/calendar.svg')))
    if not args.smoke_test:
        server_name=('liquid-calendar-flatpak-' if FLATPAK else 'liquid-calendar-')+str(os.getuid())
        socket=QLocalSocket();socket.connectToServer(server_name)
        if socket.waitForConnected(250):socket.write(b'show');socket.flush();socket.waitForBytesWritten(200);return 0
        server=QLocalServer();server.setSocketOptions(QLocalServer.UserAccessOption);QLocalServer.removeServer(server_name)
        if not server.listen(server_name):raise RuntimeError("The app could not open its local session.")
    try:store=Store(args.database,(args.database.parent/'backups') if args.smoke_test else DATA/'backups')
    except Exception as e:
        if args.smoke_test:raise
        QMessageBox.critical(None,"Could not open calendar data",str(e)+"\n\nExisting events have not been overwritten.");return 1
    bridge=Bridge(store,args.smoke_test)
    engine=QQmlApplicationEngine();engine.rootContext().setContextProperty('planner',bridge);engine.load(QUrl.fromLocalFile(str(BASE/'qml/App.qml')))
    if not engine.rootObjects():return 1
    window=engine.rootObjects()[0]
    tray=QSystemTrayIcon(QIcon(str(BASE/'icons/calendar.svg')),app);tray.setToolTip("Liquid Calendar · Reminders")
    menu=QMenu();show=menu.addAction("Open calendar");quit_action=menu.addAction("Quit app and reminders");tray.setContextMenu(menu)
    def activate():window.show();window.raise_();window.requestActivate()
    show.triggered.connect(activate);quit_action.triggered.connect(app.quit);tray.activated.connect(lambda reason:activate() if reason in [QSystemTrayIcon.Trigger,QSystemTrayIcon.DoubleClick] else None)
    tray_available=QSystemTrayIcon.isSystemTrayAvailable() and not args.smoke_test
    if tray_available:tray.show();app.setQuitOnLastWindowClosed(False)
    window.setProperty('trayAvailable',tray_available)
    if not args.smoke_test:
        def receive():
            client=server.nextPendingConnection()
            if client:client.waitForReadyRead(100);client.readAll();client.disconnectFromServer();activate()
        server.newConnection.connect(receive)
    if args.background and tray_available:window.hide()
    if args.smoke_test:
        def finish():
            if args.screenshot:QQuickWindow.grabWindow(window).save(str(args.screenshot))
            app.quit()
        QTimer.singleShot(700,finish)
    exit_code=app.exec()
    bridge.reload_timer.stop();bridge.reminder_timer.stop()
    engine.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
    return exit_code
if __name__=='__main__':raise SystemExit(main())
