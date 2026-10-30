const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const c={}; vm.createContext(c); vm.runInContext(fs.readFileSync('companion-widget/contents/ui/Calendar.js','utf8'),c);
const ev={id:'test',title:'Termin',date:'2026-10-28',time:'09:00',minutes:60,allDay:false,task:false,done:false,repeat:'none',until:'',category:0,location:'',notes:''};
assert.equal(c.valid(ev),true); assert.equal(c.parse('2026-02-30'),null);
assert.equal(c.key(c.monday(c.parse('2026-11-01'))),'2026-10-26');
assert.equal(c.instances([ev],c.parse('2026-10-01'),31,'',-1).length,1);
assert.equal(c.instances([{...ev,repeat:'weekly'}],c.parse('2026-10-28'),21,'',-1).length,3);
assert.equal(c.instances([{...ev,date:'2026-01-31',repeat:'monthly'}],c.parse('2026-02-01'),28,'',-1).length,0);
assert.equal(c.instances([{...ev,date:'2024-02-29',repeat:'yearly'}],c.parse('2025-01-01'),365,'',-1).length,0);
assert.equal(c.instances([{...ev,repeat:'daily',until:'2026-10-30'}],c.parse('2026-10-28'),10,'',-1).length,3);
assert.equal(c.instances([ev],c.parse('2026-10-28'),1,'missing',-1).length,0);
assert.equal(c.instances([ev],c.parse('2026-10-28'),1,'',2).length,0);
assert.equal(c.restore(c.backup([ev]))[0].title,'Termin');
assert.throws(()=>c.restore(c.backup([ev,ev])));
assert.equal(c.valid({...ev,time:'25:12'}),false);
assert.equal(c.valid({...ev,until:'2026-01-01'}),false);
assert.match(c.ics([{...ev,time:'23:30',minutes:90}]),/DTEND:20261029T010000/);
assert.match(c.ics([{...ev,allDay:true}]),/DTEND;VALUE=DATE:20261029/);
assert.equal(c.ics([{...ev,task:true}]).includes('BEGIN:VEVENT'),false);
console.log('16 Kalenderprüfungen bestanden.');

const night={...ev,time:'23:30',minutes:120,repeat:'weekly'};
const carry=c.instances([night],c.parse('2026-10-29'),1,'',-1);
assert.equal(carry.length,1);assert.equal(carry[0].date,'2026-10-29');assert.equal(carry[0].occurrenceDate,'2026-10-28');assert.equal(carry[0].carry,true);assert.equal(carry[0].segmentMinutes,90);
assert.equal(c.instances([{...night,minutes:30}],c.parse('2026-10-29'),1,'',-1).length,0);
assert.equal(c.instances([{...night,allDay:true}],c.parse('2026-10-29'),1,'',-1).length,0);
assert.equal(c.instances([{...night,exceptions:{'2026-10-28':{cancelled:true}}}],c.parse('2026-10-29'),1,'',-1).length,0);
const daily=c.instances([{...night,repeat:'daily'}],c.parse('2026-10-29'),1,'',-1);
assert.equal(daily.length,2);assert.notEqual(daily[0].occurrenceDate,daily[1].occurrenceDate);
assert.equal(c.instances([night],c.parse('1000-01-01'),1,'',-1).length,0);
console.log('Overnight carry-in identity, midnight/all-day exclusions, cancellations and daily occurrences passed.');

// Both distributed clients must reject unrepresentable endpoints and preserve floating wall time.
const previousTZ=process.env.TZ;
try {
 process.env.TZ='Europe/Berlin';
 for (const source of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
  const api={};vm.createContext(api);vm.runInContext(fs.readFileSync(source,'utf8'),api);
  assert.equal(api.dateSuggestions('1.1.0001',api.parse('2026-10-29')).length,0);
  for (const query of ['tomorrow','day after tomorrow','Monday','January'])assert.equal(api.dateSuggestions(query,api.parse('9999-12-31')).length,0);
  assert.equal(api.key(api.dateSuggestions('1.1.1000',api.parse('2026-10-29'))[0].date),'1000-01-01');
  for (const change of [{time:'23:30',minutes:120},{allDay:true},{repeat:'weekly',weekdays:[0]}])assert.throws(()=>api.ics([{...ev,date:'9999-12-31',...change}]),/1000–9999/);
  assert.match(api.ics([{...ev,date:'9999-12-31',time:'22:00'}]),/DTEND:99991231T230000/);
  assert.match(api.ics([{...ev,date:'9999-12-30',allDay:true}]),/DTEND;VALUE=DATE:99991231/);
  assert.match(api.ics([{...ev,date:'9999-12-31',repeat:'weekly',weekdays:[4]}]),/DTSTART:99991231T090000/);
  for (const date of ['2026-10-25','2026-03-29'])assert.match(api.ics([{...ev,date,time:'01:30',minutes:120}]),new RegExp('DTEND:'+date.replace(/-/g,'')+'T033000'));
 }
} finally {if(previousTZ===undefined)delete process.env.TZ;else process.env.TZ=previousTZ;}
console.log('Date hint bounds and floating ICS endpoint/DST regressions passed for app and widget.');

for (const source of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
 const api={};vm.createContext(api);vm.runInContext(fs.readFileSync(source,'utf8'),api);
 const long={...ev,title:'🚀'.repeat(60),location:'東京'.repeat(100),notes:'first\rsecond\r\nthird\nfourth;comma,backslash\\ '+'😀é'.repeat(100)};
 const exported=api.ics([long]);
 assert.equal(exported.replace(/\r\n/g,'').includes('\r'),false);
 for (const line of exported.split('\r\n'))assert.ok(Buffer.byteLength(line,'utf8')<=75);
 const unfolded=exported.replace(/\r\n /g,'');
 assert.ok(unfolded.includes('SUMMARY:'+api.escapeIcs(long.title)+'\r\n'));
 assert.ok(unfolded.includes('LOCATION:'+api.escapeIcs(long.location)+'\r\n'));
 assert.ok(unfolded.includes('DESCRIPTION:'+api.escapeIcs(long.notes)+'\r\n'));
 assert.equal(api.escapeIcs('one\rtwo\r\nthree\nfour'),'onetwo\\nthree\\nfour');
 assert.equal(Buffer.from(exported,'utf8').toString('utf8'),exported);
}
console.log('ICS UTF-8 folding, lossless unfolding and isolated-CR normalization passed for app and widget.');

// Linked groups keep independent records and clean up after deletions/conversions.
{
 const a={...ev,id:'linked-a',groupId:'group'},b={...ev,id:'linked-b',title:'Other',groupId:'group'};
 assert.equal(c.valid(a),true);
 for(const invalid of ['',null,{},false,'x'.repeat(151)])assert.equal(c.valid({...ev,groupId:invalid}),false);
 const index=c.groupIndex([a,b]);
 assert.equal(c.groupDetails([a,b],a,index).label,'Linked 1');
 assert.equal(c.groupDetails([a,b],a,index).peers[0].id,'linked-b');
 assert.equal(c.groupDetails([a],a).id,'');
 assert.equal(c.cleanGroups([a])[0].groupId,undefined);
 assert.equal(a.groupId,'group');
 const kept=c.mergeEvents([a,b],[b],[a,b]);
 assert.equal(kept.length,1);assert.equal(kept[0].groupId,undefined);
 const converted=c.cleanGroups([{...a,task:true},b]);assert(converted.every(e=>e.groupId===undefined));
 assert.equal(c.restore(c.backup([a,b]))[1].groupId,'group');
 assert.equal(c.ics([a,b]).split('BEGIN:VEVENT').length-1,2);
}
