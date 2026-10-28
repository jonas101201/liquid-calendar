const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
for(const file of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
 const c={};vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);
 const task={id:'series',title:'Synthetic weekly task',date:'2032-01-05',time:'23:30',minutes:90,allDay:false,task:true,done:false,repeat:'weekly',until:'',category:0,location:'',notes:'',reminder:10};
 const original=JSON.stringify(task);const next=c.toggleTaskOccurrence([task],'series','2032-01-05');
 assert.equal(JSON.stringify(task),original);assert.equal(next.length,2);assert(next.every(c.valid));
 const parent=next.find(e=>e.id==='series'),child=next.find(e=>e.id!=='series');
 assert.equal(parent.done,false);assert.equal(child.done,true);assert.equal(child.originalDate,'2032-01-05');assert.equal(child.seriesId,'series');assert.equal(child.date,'2032-01-05');
 assert.equal(c.occurs(parent,c.parse('2032-01-05')),false);assert.equal(c.occurs(parent,c.parse('2032-01-12')),true);
 const reopened=c.toggleTaskOccurrence(next,child.id,child.date);assert.equal(reopened.length,2);assert.equal(reopened.find(e=>e.id===child.id).done,false);
 assert.throws(()=>c.toggleTaskOccurrence([task],'series','2032-01-06'));
 const competing=c.toggleTaskOccurrence([task],'series','2032-01-05');assert.throws(()=>c.mergeEvents([task],competing,next));assert.equal(c.mergeEvents([task],next,next).length,2);
 const legacy=c.toggleTaskOccurrence([{...task,done:true}],'series','2032-01-05');assert.equal(legacy.length,1);assert.equal(legacy[0].done,false);
 const merged=c.mergeEvents([task],next,[task]);assert.equal(merged.length,2);
}
console.log('App/widget occurrence completion, stale concurrent merge, legacy reopening and valid shared records passed.');
