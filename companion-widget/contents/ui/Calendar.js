// Count Unicode code points, matching Python validation rather than UTF-16 units.
function textLength(text) { return Array.from(text).length; }
function key(d) { return d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()); }
function pad(n) { return n < 10 ? '0'+n : ''+n; }
function parse(s) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) return null;
    var p=s.split('-').map(Number), d=new Date(p[0],p[1]-1,p[2],12);
    return key(d)===s ? d : null;
}
function add(d,n) { return new Date(d.getFullYear(),d.getMonth(),d.getDate()+n,12); }
function monday(d) { return add(d,-((d.getDay()+6)%7)); }
function month(d,n) { return new Date(d.getFullYear(),d.getMonth()+n,1,12); }
function isUndated(e) {return e.task===true&&e.date===''&&e.time==='';}
function valid(e) {
    return e && typeof e.id==='string' && e.id.length>0 && textLength(e.id)<=150 &&
        typeof e.title==='string' && e.title.trim().length>0 && textLength(e.title)<=200 &&
        typeof e.date==='string' && typeof e.time==='string' &&
        (isUndated(e)?e.repeat==='none'&&e.until===''&&e.allDay===false&&(e.reminder===undefined||e.reminder===-1)&&Object.keys(e.exceptions||{}).length===0:!!parse(e.date)&&/^([01]\d|2[0-3]):[0-5]\d$/.test(e.time)) &&
        Number.isInteger(e.minutes) && e.minutes>=5 && e.minutes<=1440 &&
        ['none','daily','weekly','monthly','yearly'].indexOf(e.repeat)>=0 &&
        typeof e.until==='string' && (e.until==='' || (!!parse(e.until) && e.until>=e.date)) &&
        typeof e.allDay==='boolean' && typeof e.task==='boolean' && typeof e.done==='boolean' &&
        typeof e.location==='string' && textLength(e.location)<=500 && typeof e.notes==='string' && textLength(e.notes)<=10000 &&
        Number.isInteger(e.category) && e.category>=0 && e.category<4 &&
        (e.reminder===undefined||(Number.isInteger(e.reminder)&&[-1,0,5,10,30,60,1440].indexOf(e.reminder)>=0)) &&
        (e.groupId===undefined||(typeof e.groupId==='string'&&textLength(e.groupId)>0&&textLength(e.groupId)<=150)) &&
        (e.exceptions===undefined||validExceptions(e.exceptions)) && validTaskDetails(e) && validWeekdays(e);
}
function isoWeekday(date) {return (date.getDay()+6)%7;}
function weeklyDays(e) {return e.weekdays===undefined?[isoWeekday(parse(e.date))]:e.weekdays;}
function validWeekdays(e) {
    if(e.weekdays===undefined)return true;
    return e.repeat==='weekly'&&Array.isArray(e.weekdays)&&e.weekdays.length>=1&&e.weekdays.length<=7&&e.weekdays.every(function(day,i,days){return Number.isInteger(day)&&day>=0&&day<=6&&days.indexOf(day)===i;});
}
function validTaskDetails(e) {
    if(e.priority!==undefined&&(!Number.isInteger(e.priority)||e.priority<0||e.priority>3))return false;
    if(e.project!==undefined&&(typeof e.project!=='string'||textLength(e.project)>80||e.project==='*'))return false;
    if(e.checklist===undefined)return true;
    if(!Array.isArray(e.checklist)||e.checklist.length>100)return false;
    var ids=Object.create(null);
    return e.checklist.every(function(item){
        if(!item||typeof item.id!=='string'||!item.id.length||textLength(item.id)>150||ids[item.id]||typeof item.title!=='string'||!item.title.trim()||textLength(item.title)>200||typeof item.done!=='boolean')return false;
        ids[item.id]=true;return true;
    });
}
function taskWords(e) {return (e.project||'')+' '+(e.checklist||[]).map(function(item){return item.title;}).join(' ');}
function validExceptions(value) {
    return !!value&&typeof value==='object'&&!Array.isArray(value)&&Object.keys(value).every(function(date){
        var item=value[date];return !!parse(date)&&!!item&&typeof item==='object'&&!Array.isArray(item)&&item.cancelled===true;
    });
}
function occurs(e,d) {
    if(isUndated(e)||!d||d.getFullYear()<1000||d.getFullYear()>9999)return false;
    var s=key(d), a=parse(e.date);
    if(e.exceptions&&e.exceptions[s]&&e.exceptions[s].cancelled)return false;
    if (s<e.date || (e.until && s>e.until)) return false;
    if (e.repeat==='none') return s===e.date;
    if (e.repeat==='daily') return true;
    if (e.repeat==='weekly') return weeklyDays(e).indexOf(isoWeekday(d))>=0;
    if (e.repeat==='monthly') return d.getDate()===a.getDate();
    return d.getMonth()===a.getMonth() && d.getDate()===a.getDate();
}
function instances(events,start,days,query,category,kind) {
    var out=[], q=(query||'').trim();
    for(var n=0;n<days;n++) {
        var d=add(start,n), s=key(d), previous=add(d,-1);
        events.forEach(function(e) {
            if (category>=0 && e.category!==category) return;
            if (!kindMatches(e,kind) || (q && !matches(e,q))) return;
            if (occurs(e,d)) out.push({event:e,date:s,occurrenceDate:s,carry:false,sort:s+(e.allDay?'00:00':e.time)});
            var end=!e.allDay?Number(e.time.slice(0,2))*60+Number(e.time.slice(3))+e.minutes:0;
            if(end>1440&&occurs(e,previous)) {
                out.push({event:e,date:s,occurrenceDate:key(previous),carry:true,segmentMinutes:end-1440,sort:s+'00:00'});
            }
        });
    }
    out.sort(function(a,b) { return a.sort.localeCompare(b.sort) || a.event.title.localeCompare(b.event.title); });
    return out;
}
function backup(events) { return JSON.stringify({format:'liquid-glass-calendar',version:1,events:events},null,2); }
function restore(text) {
    var data=JSON.parse(text);
    if(data.format!=='liquid-glass-calendar' || data.version!==1 || !Array.isArray(data.events) || data.events.length>10000) throw Error("Not a valid calendar backup (version 1).");
    var ids=Object.create(null);
    data.events.forEach(function(e){ if(!valid(e) || ids[e.id] || ['occurrenceOf','occurrenceDate','originHash'].some(function(k){return Object.prototype.hasOwnProperty.call(e,k);})) throw Error("Invalid or duplicate events in the backup."); ids[e.id]=true; });
    return data.events;
}
function escapeIcs(s) { return s.replace(/\\/g,'\\\\').replace(/\r/g,'').replace(/\n/g,'\\n').replace(/;/g,'\\;').replace(/,/g,'\\,'); }
function ics(events) {
    var lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Liquid Calendar//EN','CALSCALE:GREGORIAN'];
    function exportDate(date,event) {
        if(!date||!Number.isFinite(date.getTime())||date.getFullYear()<1000||date.getFullYear()>9999)
            throw Error('Cannot export "'+event.title+'": event dates, including the end, must stay within years 1000–9999.');
        return date;
    }
    events.filter(function(e){return !e.task;}).forEach(function(e){
        var first=exportDate(parse(e.date),e);
        if(e.repeat==='weekly') {
            var offset=Math.min.apply(null,weeklyDays(e).map(function(day){return (day-isoWeekday(first)+7)%7;}));
            first=exportDate(add(first,offset),e);
            if(e.until&&key(first)>e.until)return;
        }
        var date=key(first).replace(/-/g,''), start=first, end;
        lines.push('BEGIN:VEVENT','UID:'+e.id+'@liquid-glass-calendar','DTSTAMP:'+new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+Z/,'Z'));
        if(e.allDay) lines.push('DTSTART;VALUE=DATE:'+date,'DTEND;VALUE=DATE:'+key(exportDate(add(start,1),e)).replace(/-/g,''));
        else {
            var p=e.time.split(':').map(Number), finish=p[0]*60+p[1]+e.minutes;
            // Calendar records use floating wall time, including across DST changes.
            end=exportDate(add(start,Math.floor(finish/1440)),e);
            var endMinute=finish%1440;
            lines.push('DTSTART:'+date+'T'+e.time.replace(':','')+'00','DTEND:'+key(end).replace(/-/g,'')+'T'+pad(Math.floor(endMinute/60))+pad(endMinute%60)+'00');
        }
        if(e.repeat!=='none') {
            var rule='RRULE:FREQ='+e.repeat.toUpperCase();
            if(e.repeat==='weekly'&&e.weekdays!==undefined)rule+=';BYDAY='+e.weekdays.slice().sort(function(a,b){return a-b;}).map(function(day){return ['MO','TU','WE','TH','FR','SA','SU'][day];}).join(',');
            if(e.until) rule+=';UNTIL='+e.until.replace(/-/g,'')+(e.allDay?'':'T235959');
            lines.push(rule);
        }
        Object.keys(e.exceptions||{}).forEach(function(date){if(e.exceptions[date].cancelled)lines.push(e.allDay?'EXDATE;VALUE=DATE:'+date.replace(/-/g,''):'EXDATE:'+date.replace(/-/g,'')+'T'+e.time.replace(':','')+'00');});
        lines.push('SUMMARY:'+escapeIcs(e.title),'LOCATION:'+escapeIcs(e.location),'DESCRIPTION:'+escapeIcs(e.notes),'END:VEVENT');
    });
    lines.push('END:VCALENDAR');
    var folded=[];
    lines.forEach(function(line) {
        var chunk='', bytes=0;
        Array.from(line).forEach(function(character) {
            var point=character.codePointAt(0), size=point<=0x7f?1:point<=0x7ff?2:point<=0xffff?3:4;
            if(bytes+size>75) {folded.push(chunk);chunk=' ';bytes=1;}
            chunk+=character;bytes+=size;
        });
        folded.push(chunk);
    });
    return folded.join('\r\n')+'\r\n';
}

function weekNumber(d) { var t=new Date(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())); t.setUTCDate(t.getUTCDate()+4-(t.getUTCDay()||7)); return Math.ceil((((t-new Date(Date.UTC(t.getUTCFullYear(),0,1)))/86400000)+1)/7); }

function normalized(text) {
    return String(text||'').toLowerCase().replace(/ß/g,'ss').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
}
function kindMatches(e,kind) {
    return !kind || (kind===1&&!e.task) || (kind===2&&e.task) || (kind===3&&e.task&&!e.done) || (kind===4&&e.task&&e.done);
}
function matches(e,q) {
    var hay=normalized(e.title+' '+e.location+' '+e.notes+' '+taskWords(e));
    return normalized(q).trim().split(/\s+/).every(function(t){return hay.indexOf(t)>=0;});
}
function unskippedNext(e,from) {
    var start=parse(e.date), candidate;
    if(e.repeat==='weekly') {
        var cursor=key(from)<e.date?start:from;
        candidate=add(cursor,Math.min.apply(null,weeklyDays(e).map(function(day){return (day-isoWeekday(cursor)+7)%7;})));
        return candidate.getFullYear()<=9999&&(!e.until||key(candidate)<=e.until)?candidate:null;
    }
    if (key(from)<=e.date) return !e.until||e.date<=e.until?start:null;
    if (e.repeat==='none') return null;
    if (e.repeat==='daily') candidate=add(from,0);
    else if (e.repeat==='monthly') {
        for(var m=0;m<24;m++) {
            var first=month(from,m), d=new Date(first.getFullYear(),first.getMonth(),start.getDate(),12);
            if(d.getMonth()===first.getMonth()&&key(d)>=key(from)) { candidate=d; break; }
        }
    } else {
        for(var y=from.getFullYear();y<=from.getFullYear()+8;y++) {
            var d2=new Date(y,start.getMonth(),start.getDate(),12);
            if(d2.getMonth()===start.getMonth()&&d2.getDate()===start.getDate()&&key(d2)>=key(from)) {candidate=d2;break;}
        }
    }
    return candidate&&candidate.getFullYear()<=9999&&(!e.until||key(candidate)<=e.until)?candidate:null;
}
function unskippedLast(e,until) {
    var start=parse(e.date), end=key(until)<e.date?null:until;
    if(!end) return null;
    if(e.until&&e.until<key(end)) end=parse(e.until);
    if(e.repeat==='none') return start;
    if(e.repeat==='daily') return add(end,0);
    if(e.repeat==='weekly') {
        var candidate=add(end,-Math.min.apply(null,weeklyDays(e).map(function(day){return (isoWeekday(end)-day+7)%7;})));
        return candidate.getFullYear()>=1000&&key(candidate)>=e.date?candidate:null;
    }
    for(var n=0;n<(e.repeat==='monthly'?24:9);n++) {
        var year=e.repeat==='monthly'?month(end,-n).getFullYear():end.getFullYear()-n;
        var mon=e.repeat==='monthly'?month(end,-n).getMonth():start.getMonth();
        var d=new Date(year,mon,start.getDate(),12);
        if(d.getFullYear()>=1000&&d.getMonth()===mon&&key(d)<=key(end)&&key(d)>=e.date) return d;
    }
    return null;
}
var monthNames=['January','February','March','April','May','June','July','August','September','October','November','December'];
var germanMonthNames=['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'];
var weekNames=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
var germanWeekNames=['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'];
function dayWords(d,today) {
    var s=key(d), rel=s===key(today)?'today heute':s===key(add(today,1))?'tomorrow morgen':s===key(add(today,2))?'day after tomorrow übermorgen':'';
    return weekNames[d.getDay()]+' '+monthNames[d.getMonth()]+' '+d.getFullYear()+' '+pad(d.getDate())+'.'+pad(d.getMonth()+1)+'.'+d.getFullYear()+' '+s+' '+rel+' '+germanWeekNames[d.getDay()]+' '+germanMonthNames[d.getMonth()];
}
function dateSuggestions(query,today) {
    var q=normalized(query).trim(), out=[];
    if(!q) return out;
    function push(d,label,kind) { if(!d||d.getFullYear()<1000||d.getFullYear()>9999)return; if(!out.some(function(v){return key(v.date)===key(d);})) out.push({date:d,label:label,kind:kind||'day'}); }
    [['today',0],['tomorrow',1],['day after tomorrow',2],['heute',0],['morgen',1],['ubermorgen',2]].forEach(function(v){if(v[0].indexOf(q)===0) push(add(today,v[1]),['Today','Tomorrow','Day after tomorrow'][v[1]]);});
    var exact=parse(q), p=q.match(/^(\d{1,2})\.(\d{1,2})(?:\.(\d{4})?)?$/);
    if(exact) push(exact,"Go to date");
    if(p) { var d=parse((p[3]||today.getFullYear())+'-'+pad(Number(p[2]))+'-'+pad(Number(p[1]))); if(d)push(d,"Go to date"); }
    if(q.length>=2) {
        [weekNames,germanWeekNames].forEach(function(names){names.forEach(function(name,i){if(normalized(name).indexOf(q)===0)push(add(today,(i-today.getDay()+7)%7),weekNames[i]);});});
        [monthNames,germanMonthNames].forEach(function(names){names.forEach(function(name,i){if(normalized(name).indexOf(q)===0)push(new Date(today.getFullYear()+(i<today.getMonth()?1:0),i,1,12),monthNames[i],'month');});});
    }
    return out.slice(0,3);
}
function searchAll(events,query,category,kind,today) {
    var q=normalized(query).trim(), tokens=q.split(/\s+/), out=[], day=key(today), hints=[];
    tokens.forEach(function(t){if(t) hints=hints.concat(dateSuggestions(t,today));});
    var relativeOffsets={'today':0,'heute':0,'tomorrow':1,'morgen':1,'day after tomorrow':2,'ubermorgen':2};
    var relativeTarget=Object.prototype.hasOwnProperty.call(relativeOffsets,q)?add(today,relativeOffsets[q]):null;
    var explicitHints=/^(?:[1-9]\d{3}-\d{2}-\d{2}|\d{1,2}\.\d{1,2}(?:\.\d{4})?\.?)$/.test(q)?dateSuggestions(q,today):[];
    var exactTarget=relativeTarget||(explicitHints.length?explicitHints[0].date:null);
    events.forEach(function(e){
        if(category>=0&&e.category!==category||!kindMatches(e,kind))return;
        if(isUndated(e)) {
            if(exactTarget)return;
            var taskHay=normalized(e.title+' '+e.location+' '+e.notes+' '+taskWords(e));
            if(tokens.every(function(t){return taskHay.indexOf(t)>=0;})) {
                var taskTitle=normalized(e.title),taskRank=taskTitle===q?0:taskTitle.indexOf(q)===0?1:taskTitle.indexOf(q)>=0?2:3;
                out.push({event:e,date:'',sort:'',rank:taskRank,past:false,unscheduled:true});
            }
            return;
        }
        if(exactTarget&&!occurs(e,exactTarget))return;
        var d=exactTarget||nextOccurrence(e,today)||lastOccurrence(e,today);
        for(var h=0;!exactTarget&&h<hints.length;h++) {
            var hint=hints[h], target=hint.kind==='month'?nextOccurrence(e,hint.date):occurs(e,hint.date)?hint.date:null;
            if(target&&(hint.kind!=='month'||(target.getMonth()===hint.date.getMonth()&&target.getFullYear()===hint.date.getFullYear()))) {d=target;break;}
        }
        if(!d)return;
        var hay=normalized(e.title+' '+e.location+' '+e.notes+' '+taskWords(e)+' '+dayWords(d,today)+' '+(e.repeat==='weekly'&&e.weekdays!==undefined&&!occurs(e,parse(e.date))?e.date:dayWords(parse(e.date),today)));
        if(!tokens.every(function(t){return hay.indexOf(t)>=0;}))return;
        var title=normalized(e.title), rank=title===q?0:title.indexOf(q)===0?1:title.indexOf(q)>=0?2:3;
        out.push({event:e,date:key(d),sort:key(d)+(e.allDay?'00:00':e.time),rank:rank,past:key(d)<day});
    });
    out.sort(function(a,b){return a.rank-b.rank||Number(!a.unscheduled)-Number(!b.unscheduled)||Number(a.past)-Number(b.past)||(a.past?b.sort.localeCompare(a.sort):a.sort.localeCompare(b.sort))||a.event.title.localeCompare(b.event.title);});
    return out;
}

// Apply only local edits to the latest shared database snapshot.
function mergeEvents(base,desired,current) {
    var before=Object.create(null),after=Object.create(null),remote=Object.create(null),remoteBefore=Object.create(null);
    base.forEach(function(e){before[e.id]=e;});desired.forEach(function(e){after[e.id]=e;});current.forEach(function(e){remote[e.id]=e;remoteBefore[e.id]=e;});
    var ids=Object.keys(before).concat(Object.keys(after)).filter(function(id,index,all){return all.indexOf(id)===index;});
    function stable(value) {
        return JSON.stringify(value,function(k,v){
            if(v&&typeof v==='object'&&!Array.isArray(v)) {
                var sorted=Object.create(null);Object.keys(v).sort().forEach(function(name){sorted[name]=v[name];});return sorted;
            }
            return v;
        });
    }
    function equal(a,b) { return stable(a)===stable(b); }
    ids.forEach(function(id){
        if(equal(before[id],after[id]))return;
        if(!before[id]&&after[id]&&after[id].seriesId&&
           !equal(remoteBefore[after[id].seriesId],before[after[id].seriesId])&&
           !equal(remoteBefore[id],after[id]))
            throw Error('The series has changed. Reopen this occurrence.');
        if(!equal(remote[id],before[id])&&!equal(remote[id],after[id]))throw Error("This entry was changed in the app. Reopen it; your edits have not been saved.");
        if(after[id]===undefined) {
            Object.keys(remote).forEach(function(child){
                if(remote[child].seriesId===id) {
                    if(!equal(remote[child],before[child]))throw Error("An occurrence of this series has changed. Reopen the series.");
                    delete remote[child];
                }
            });
            delete remote[id];
        } else remote[id]=after[id];
    });
    return cleanGroups(Object.keys(remote).map(function(id){return remote[id];}));
}

function nextOccurrence(e,from) {
    if(isUndated(e))return null;
    var cursor=from, tries=Object.keys(e.exceptions||{}).length+1;
    for(var n=0;n<tries;n++) {
        var d=unskippedNext(e,cursor);
        if(!d)return null;
        if(occurs(e,d))return d;
        cursor=add(d,1);
    }
    return null;
}
function lastOccurrence(e,until) {
    if(isUndated(e))return null;
    var cursor=until, tries=Object.keys(e.exceptions||{}).length+1;
    for(var n=0;n<tries;n++) {
        var d=unskippedLast(e,cursor);
        if(!d)return null;
        if(occurs(e,d))return d;
        if(e.repeat==='none')return null;
        cursor=add(d,-1);
    }
    return null;
}

function toggleTaskOccurrence(events,ident,date) {
    var source=events.filter(function(e){return e.id===ident;})[0];
    if(!source||!source.task)throw Error('This task no longer exists.');
    var next=events.map(function(e){return JSON.parse(JSON.stringify(e));});
    var parent=next.filter(function(e){return e.id===ident;})[0];
    if(source.repeat==='none'||source.done) {parent.done=!parent.done;return next;}
    var day=parse(date);
    if(!day||!occurs(source,day))throw Error('This task occurrence no longer exists.');
    parent.exceptions=parent.exceptions||{};parent.exceptions[date]={cancelled:true};
    var child=JSON.parse(JSON.stringify(source));
    child.id=Date.now().toString(36)+'-'+Math.random().toString(36).slice(2);
    child.date=date;child.repeat='none';child.until='';child.exceptions={};delete child.weekdays;
    child.done=true;child.seriesId=ident;child.originalDate=date;
    next.push(child);return next;
}

function cleanGroups(events) {
    var counts=Object.create(null);
    events.forEach(function(e){if(e.groupId&&!e.task&&e.repeat==='none')counts[e.groupId]=(counts[e.groupId]||0)+1;});
    return events.map(function(e){var copy=Object.assign({},e);if(copy.groupId&&(copy.task||copy.repeat!=='none'||counts[copy.groupId]<2))delete copy.groupId;return copy;});
}
function groupIndex(events) {
    var groups=Object.create(null),number=0;
    events.forEach(function(e){
        if(!e.groupId||e.task||e.repeat!=='none')return;
        if(!groups[e.groupId])groups[e.groupId]={id:e.groupId,label:'Linked '+(++number),peers:[]};
        groups[e.groupId].peers.push(e);
    });
    return groups;
}
function groupDetails(events,event,index) {
    var group=(index||groupIndex(events))[event.groupId];
    if(!group||group.peers.length<2)return {id:'',label:'',peers:[]};
    return {id:group.id,label:group.label,peers:group.peers.filter(function(e){return e.id!==event.id;})};
}
