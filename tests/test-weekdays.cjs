const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
for(const file of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
 const c={};vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);
 const e={id:'weekly',title:'Lesson',date:'2026-10-27',time:'09:00',minutes:60,allDay:false,task:false,done:false,repeat:'weekly',until:'',category:0,location:'',notes:'',reminder:10,weekdays:[0,2,4]};
 assert(c.valid(e));assert(!c.occurs(e,c.parse('2026-10-27')));assert(c.occurs(e,c.parse('2026-10-28')));
 for(let mask=1;mask<128;mask++) {
  const weekdays=Array.from({length:7},(_,i)=>i).filter(i=>mask&(1<<i)),entry={...e,date:'2026-10-26',weekdays};
  for(let n=0;n<14;n++)assert.equal(c.occurs(entry,c.add(c.parse(entry.date),n)),weekdays.includes(n%7));
 }
 assert.equal(c.key(c.nextOccurrence(e,c.parse(e.date))),'2026-10-28');
 const ended={...e,until:'2026-11-03',exceptions:{'2026-10-28':{cancelled:true}}};
 assert.equal(c.key(c.nextOccurrence(ended,c.parse(e.date))),'2026-10-30');assert.equal(c.key(c.lastOccurrence(ended,c.parse('2026-12-01'))),'2026-11-02');
 assert.equal(c.lastOccurrence({...e,until:e.date},c.parse('2026-12-01')),null);
 for(const weekdays of [[],null,{},[true],[7],[-1],[1,1],['1'],[0.5]])assert(!c.valid({...e,weekdays}));
 assert(!c.valid({...e,repeat:'none'}));assert.equal(c.searchAll([e],'Tuesday',-1,0,c.parse('2026-10-28')).length,0);
 assert(c.ics([e]).includes('RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR'));assert(c.ics([e]).includes('DTSTART:20261028T090000'));
 assert(c.ics([{...e,allDay:true}]).includes('DTSTART;VALUE=DATE:20261028'));assert(!c.ics([{...e,until:e.date}]).includes('BEGIN:VEVENT'));
 assert.equal(JSON.stringify(c.restore(c.backup([e]))[0]),JSON.stringify(e));
 const legacy={...e};delete legacy.weekdays;assert(c.occurs(legacy,c.parse(e.date)));
 const completed=c.toggleTaskOccurrence([{...e,task:true}],'weekly','2026-10-28');assert(completed.every(c.valid));assert(!('weekdays' in completed.find(v=>v.id!=='weekly')));assert.equal(completed.find(v=>v.id==='weekly').weekdays.length,3);
}
console.log('App/widget weekday subsets, bounds, search, exceptions, export, backup and completion passed.');
