"""Calendar calculations. Local floating dates, compatible with the Plasma widget."""
from __future__ import annotations
import calendar
import copy
import datetime as dt
import hashlib
import json
import unicodedata
import uuid

CATEGORIES = ["Personal", "Work", "Important", "Leisure"]
COLORS = ['#a498ff', '#6edfc2', '#ffbd83', '#f49ac4']
WEEKDAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
GERMAN_WEEKDAYS = ['Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag','Sonntag']
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
GERMAN_MONTHS = ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember']

def parse(value):
    import re
    if not isinstance(value,str) or not re.fullmatch(r'[1-9]\d{3}-\d{2}-\d{2}',value):raise ValueError("Enter the date as YYYY-MM-DD.")
    return dt.date.fromisoformat(value)

def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD', str(s).casefold()) if not unicodedata.combining(c))

def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()

def is_undated(e):
    return e.get("task") is True and e.get("date")=="" and e.get("time")==""

def validate(events):
    if not isinstance(events,list) or len(events)>10000:
        raise ValueError("The calendar file contains too many or invalid entries.")
    ids=set()
    for e in events:
        if not isinstance(e,dict):raise ValueError("Invalid entry.")
        if not isinstance(e.get('id'),str) or not e['id'] or len(e['id'])>150 or e['id'] in ids:raise ValueError("Invalid or duplicate event ID.")
        ids.add(e['id'])
        if not isinstance(e.get('title'),str) or not e['title'].strip() or len(e['title'])>200:raise ValueError("Enter a title of up to 200 characters.")
        undated=is_undated(e)
        if undated:
            if e.get('repeat')!='none' or e.get('until')!='' or e.get('allDay') is not False or e.get('reminder',-1)!=-1 or e.get('exceptions',{}):raise ValueError("Undated tasks cannot repeat or have timed reminders.")
        else:
            if not isinstance(e.get('date'),str) or len(e['date'])!=10 or parse(e['date']).isoformat()!=e['date']:raise ValueError("Invalid date.")
            if not isinstance(e.get('time'),str) or len(e['time'])!=5 or dt.time.fromisoformat(e['time']).isoformat(timespec='minutes')!=e['time']:raise ValueError("Invalid time.")
        if type(e.get('minutes')) is not int or not 5<=e['minutes']<=1440:raise ValueError('Duration must be between 5 and 1440 minutes.')
        if e.get('repeat') not in ['none','daily','weekly','monthly','yearly']:raise ValueError("Invalid repeat setting.")
        if not isinstance(e.get('until'),str) or (e['until'] and (len(e['until'])!=10 or parse(e['until']).isoformat()!=e['until'] or parse(e['until'])<parse(e['date']))):raise ValueError("Invalid repeat end date.")
        if any(type(e.get(k)) is not bool for k in ('allDay','task','done')):raise ValueError("Invalid event status.")
        if type(e.get('category')) is not int or not 0<=e['category']<4:raise ValueError("Invalid category.")
        if any(not isinstance(e.get(k),str) or len(e[k])>limit for k,limit in [('location',500),('notes',10000)]):raise ValueError('Location or notes are invalid or too long.')
        if 'reminder' in e and (type(e['reminder']) is not int or e['reminder'] not in [-1,0,5,10,30,60,1440]):raise ValueError("Invalid reminder.")
        exceptions=e.get('exceptions',{})
        if not isinstance(exceptions,dict):raise ValueError("Invalid repeat exceptions.")
        for date,v in exceptions.items():
            if parse(date).isoformat()!=date:raise ValueError("Invalid exception date.")
            if not isinstance(v,dict) or v.get('cancelled') is not True:raise ValueError("Invalid repeat exception.")
    return events

def occurs(e,day):
    if is_undated(e):return False
    s=day.isoformat(); start=parse(e['date'])
    if s<e['date'] or e['until'] and s>e['until'] or e.get('exceptions',{}).get(s,{}).get('cancelled'):return False
    repeat=e['repeat']
    return (s==e['date'] if repeat=='none' else True if repeat=='daily' else day.weekday()==start.weekday() if repeat=='weekly' else day.day==start.day if repeat=='monthly' else (day.month,day.day)==(start.month,start.day))

def next_occurrence(e,day):
    if is_undated(e):return None
    start=max(day,parse(e['date']))
    # At most eight years to the next possible leap-day recurrence; skip finite exceptions too.
    limit=366*9+len(e.get('exceptions',{}))*366
    if e['repeat']=='none':return parse(e['date']) if occurs(e,parse(e['date'])) and e['date']>=day.isoformat() else None
    for n in range(limit):
        candidate=start+dt.timedelta(days=n)
        if e['until'] and candidate.isoformat()>e['until']:return None
        if occurs(e,candidate):return candidate
    return None

def representative(e,today):
    if is_undated(e):return None
    found=next_occurrence(e,today)
    if found:return found
    end=min(today,parse(e['until'])) if e['until'] else today
    if e['repeat']=='none':return parse(e['date']) if occurs(e,parse(e['date'])) else None
    # For ended series, the last occurrence is close to the end (except yearly leap dates).
    for n in range(366*9+len(e.get('exceptions',{}))*366):
        candidate=end-dt.timedelta(days=n)
        if candidate.isoformat()<e['date']:return None
        if occurs(e,candidate):return candidate
    return None

def kind_matches(e,kind):
    return kind=='all' or kind=='events' and not e['task'] or kind=='tasks' and e['task'] or kind=='open' and e['task'] and not e['done'] or kind=='done' and e['task'] and e['done']

def occurrence(e,day):
    minute=0 if is_undated(e) else int(e['time'][:2])*60+int(e['time'][3:])
    return dict(event=copy.deepcopy(e),id=e['id'],date=day.isoformat() if day else '',unscheduled=is_undated(e),title=e['title'],time=e['time'],minutes=e['minutes'],start=minute,end=minute+e['minutes'],allDay=e['allDay'],task=e['task'],done=e['done'],color=COLORS[e['category']],location=e['location'],repeated=e['repeat']!='none',fingerprint=fingerprint(e),conflict=False,lane=0,lanes=1,occurrenceDate=day.isoformat() if day else '',carry=False,segmentMinutes=e['minutes'])

def instances(events,start,days,kind='all',category=-1):
    result=[]
    # Split timed occurrences at midnight; include carry-in from the preceding day.
    for n in range(-1,days):
        day=start+dt.timedelta(days=n)
        for e in events:
            if not ((category<0 or e['category']==category) and kind_matches(e,kind) and occurs(e,day)):continue
            v=occurrence(e,day)
            if n>=0:
                v['segmentMinutes']=min(e['minutes'],1440-v['start'])
                v['end']=v['start']+v['segmentMinutes']
                result.append(v)
            if not e['allDay'] and v['start']+e['minutes']>1440 and n+1<days:
                carry=occurrence(e,day)
                carry.update(date=(day+dt.timedelta(days=1)).isoformat(),time='00:00',start=0,end=v['start']+e['minutes']-1440,carry=True,segmentMinutes=v['start']+e['minutes']-1440)
                result.append(carry)
    result.sort(key=lambda v:(v['date'],not v['allDay'],v['start'],v['title'].casefold()))
    # Conflict intervals include events that cross midnight.
    timed=[v for v in result if not v['allDay'] and not (v['task'] and v['done'])]
    for i,a in enumerate(timed):
        a0=dt.datetime.combine(parse(a['date']),dt.time())+dt.timedelta(minutes=a['start']); a1=a0+dt.timedelta(minutes=a['segmentMinutes'])
        for b in timed[i+1:]:
            b0=dt.datetime.combine(parse(b['date']),dt.time())+dt.timedelta(minutes=b['start']); b1=b0+dt.timedelta(minutes=b['segmentMinutes'])
            if a0<b1 and b0<a1:a['conflict']=b['conflict']=True
    for n in range(days):
        daily=[v for v in timed if v['date']==(start+dt.timedelta(days=n)).isoformat()]
        group=[];group_end=-1
        def assign(group):
            ends=[]
            for v in group:
                lane=next((i for i,end in enumerate(ends) if end<=v['start']),len(ends))
                if lane==len(ends):ends.append(v['end'])
                else:ends[lane]=v['end']
                v['lane']=lane
            for v in group:v['lanes']=max(1,len(ends))
        for v in daily:
            if group and v['start']>=group_end:assign(group);group=[];group_end=-1
            group.append(v);group_end=max(group_end,v['end'])
        assign(group)
    return result

def date_hints(text,today):
    import re
    q=normalize(text).strip();result=[]
    if not q:return result
    def put(day,label,kind='day'):
        if all(v['date']!=day.isoformat() for v in result):result.append({'date':day.isoformat(),'label':label,'kind':kind})
    for name,offset in [('today',0),('tomorrow',1),('day after tomorrow',2),('heute',0),('morgen',1),('ubermorgen',2)]:
        if name.startswith(q):put(today+dt.timedelta(days=offset),['Today','Tomorrow','Day after tomorrow'][offset])
    try:
        if len(q)==10:put(parse(q),"Go to date")
    except ValueError:pass
    m=re.fullmatch(r'(\d{1,2})\.(\d{1,2})(?:\.(\d{4})?)?',q)
    if m:
        try:put(dt.date(int(m[3] or today.year),int(m[2]),int(m[1])),"Go to date")
        except ValueError:pass
    if len(q)>=2:
        for names in [WEEKDAYS,GERMAN_WEEKDAYS]:
            for i,name in enumerate(names):
                if normalize(name).startswith(q):put(today+dt.timedelta(days=(i-today.weekday())%7),WEEKDAYS[i])
        for names in [MONTHS,GERMAN_MONTHS]:
            for i,name in enumerate(names,1):
                if normalize(name).startswith(q):put(dt.date(today.year+(i<today.month),i,1),MONTHS[i-1],'month')
    return result[:3]

def search(events,text,today,kind='all',category=-1):
    tokens=normalize(text).split(); out=[];hints=[h for token in tokens for h in date_hints(token,today)]
    relative_offsets={'today':0,'heute':0,'tomorrow':1,'morgen':1,'day after tomorrow':2,'ubermorgen':2}
    offset=relative_offsets.get(normalize(text).strip())
    relative_target=today+dt.timedelta(days=offset) if offset is not None else None
    for e in events:
        if (category>=0 and e['category']!=category) or not kind_matches(e,kind):continue
        if is_undated(e):
            if all(t in normalize(e['title']+' '+e['location']+' '+e['notes']) for t in tokens):out.append(occurrence(e,None))
            continue
        if relative_target and not occurs(e,relative_target):continue
        day=relative_target or representative(e,today)
        for hint in hints:
            target=next_occurrence(e,parse(hint['date'])) if hint['kind']=='month' else parse(hint['date']) if occurs(e,parse(hint['date'])) else None
            if target and (hint['kind']!='month' or target.strftime('%Y-%m')==hint['date'][:7]):day=target;break
        if not day:continue
        relative='today heute' if day==today else 'tomorrow morgen' if day==today+dt.timedelta(days=1) else 'day after tomorrow übermorgen' if day==today+dt.timedelta(days=2) else ''
        words=' '.join([relative,e['title'],e['location'],e['notes'],day.isoformat(),parse(e['date']).isoformat(),WEEKDAYS[day.weekday()],MONTHS[day.month-1],GERMAN_WEEKDAYS[day.weekday()],GERMAN_MONTHS[day.month-1],day.strftime('%d.%m.%Y')])
        if not all(t in normalize(words) for t in tokens):continue
        out.append(occurrence(e,day))
    q=normalize(text)
    out.sort(key=lambda v:(0 if normalize(v['title'])==q else 1 if normalize(v['title']).startswith(q) else 2, not v['unscheduled'], bool(v['date']) and v['date']<today.isoformat(), abs((parse(v['date'])-today).days) if v['date'] else 0,v['time']))
    return out

def free_slots(events,day,minutes,exclude_id='',exclude_date='',limit=3):
    if not 5<=minutes<=1440:return []
    # Include yesterday's carry-over and all-day busy entries.
    busy=[]
    day0=dt.datetime.combine(day,dt.time())
    planning=copy.deepcopy(events)
    for e in planning:
        if e['id']==exclude_id and e['date']:e.setdefault('exceptions',{})[exclude_date or e['date']]={'cancelled':True}
    for v in instances([e for e in planning if not (e['task'] and e['done'])],day-dt.timedelta(days=1),2):
        start=dt.datetime.combine(parse(v['date']),dt.time())+dt.timedelta(minutes=0 if v['allDay'] else v['start'])
        end=start+dt.timedelta(minutes=1440 if v['allDay'] else v['segmentMinutes'])
        left=(start-day0).total_seconds()/60;right=(end-day0).total_seconds()/60
        if left<18*60 and right>9*60:busy.append((left,right))
    slots=[]; now=dt.datetime.now(); lower=9*60
    if day==now.date():lower=max(lower,((now.hour*60+now.minute+14)//15)*15)
    minute=lower
    while minute+minutes<=18*60 and len(slots)<limit:
        if all(not(minute<right and left<minute+minutes) for left,right in busy):
            slots.append({'date':day.isoformat(),'time':f'{minute//60:02d}:{minute%60:02d}','minute':minute,'minutes':minutes});minute+=max(minutes,15)
        else:minute+=15
    return slots

def slot_available(events,day,minutes,minute,exclude_id='',exclude_date=''):
    """Validate an exact proposed interval, independently of suggestion spacing."""
    now=dt.datetime.now()
    if day<now.date() or not 5<=minutes<=1440 or minute<9*60 or minute+minutes>18*60:return False
    if day==now.date() and minute<((now.hour*60+now.minute+14)//15)*15:return False
    planning=copy.deepcopy(events)
    for e in planning:
        if e['id']==exclude_id and e['date']:e.setdefault('exceptions',{})[exclude_date or e['date']]={'cancelled':True}
    for v in instances([e for e in planning if not(e['task'] and e['done'])],day,1):
        start=0 if v['allDay'] else v['start']
        end=1440 if v['allDay'] else start+v['segmentMinutes']
        if minute<end and start<minute+minutes:return False
    return True

def escape_ics(s):return str(s).replace('\\','\\\\').replace('\n','\\n').replace(';','\\;').replace(',','\\,').replace('\r','')
def export_ics(events):
    lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Liquid Calendar//EN','CALSCALE:GREGORIAN']
    for e in events:
        if e['task']:continue
        start=dt.datetime.combine(parse(e['date']),dt.time.fromisoformat(e['time']));end=start+dt.timedelta(minutes=e['minutes'])
        lines+=['BEGIN:VEVENT','UID:'+e['id']+'@liquid-glass-calendar','DTSTAMP:'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')]
        if e['allDay']:lines+=['DTSTART;VALUE=DATE:'+start.strftime('%Y%m%d'),'DTEND;VALUE=DATE:'+(start+dt.timedelta(days=1)).strftime('%Y%m%d')]
        else:lines+=['DTSTART:'+start.strftime('%Y%m%dT%H%M%S'),'DTEND:'+end.strftime('%Y%m%dT%H%M%S')]
        if e['repeat']!='none':lines+=['RRULE:FREQ='+e['repeat'].upper()+(';UNTIL='+e['until'].replace('-','')+('' if e['allDay'] else 'T235959') if e['until'] else '')]
        for date in e.get('exceptions',{}):
            lines.append(('EXDATE;VALUE=DATE:'+date.replace('-','')) if e['allDay'] else 'EXDATE:'+date.replace('-','')+'T'+e['time'].replace(':','')+'00')
        lines+=['SUMMARY:'+escape_ics(e['title']),'LOCATION:'+escape_ics(e['location']),'DESCRIPTION:'+escape_ics(e['notes']),'END:VEVENT']
    lines+=['END:VCALENDAR']
    # RFC 5545 physical lines: at most 75 UTF-8 octets, continuation starts with a space.
    folded=[]
    for line in lines:
        chunk=''
        for char in line:
            if len((chunk+char).encode())>75:folded.append(chunk);chunk=' '
            chunk+=char
        folded.append(chunk)
    return '\r\n'.join(folded)+'\r\n'
