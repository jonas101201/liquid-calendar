const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
for (const file of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
 const c={};vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);
 const today=c.parse('2026-10-28');
 const entry=(id,date,extra={})=>({id,title:'Meeting',date,time:'09:00',minutes:30,allDay:false,task:false,done:false,repeat:'none',until:'',category:0,location:'Büro 東京',notes:'Préparation',...extra});
 const events=[entry('today','2026-10-28'),entry('tomorrow','2026-10-29'),entry('after','2026-10-30'),entry('daily','2026-10-01',{repeat:'daily'})];
 for(const [query,id] of [['today','today'],['tomorrow','tomorrow'],['day after tomorrow','after'],['morgen','tomorrow']])assert.deepEqual(Array.from(c.searchAll(events,query,-1,0,today),v=>v.event.id).sort(),[id,'daily'].sort());
 for(const [query,date] of [['wed','2026-10-28'],['nov','2026-11-01'],['tomorrow','2026-10-29']])assert.equal(c.key(c.dateSuggestions(query,today)[0].date),date);
 assert.equal(c.dateSuggestions('morgen',today)[0].label,'Tomorrow');assert.equal(c.dateSuggestions('okt',today)[0].label,'October');
 const text=c.backup(events);assert.deepEqual(JSON.parse(text).events,events);
 assert.equal(c.weekNames[0],'Sunday');assert.equal(c.monthNames[0],'January');
}
console.log('English JS date search, exact relative dates, aliases and lossless data round-trip passed for app and widget.');
