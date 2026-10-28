const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
for(const file of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
 const c={};vm.createContext(c);vm.runInContext(fs.readFileSync(file,'utf8'),c);
 const task={id:'t',title:'Prepare',date:'',time:'',minutes:60,allDay:false,task:true,done:false,repeat:'none',until:'',category:0,location:'',notes:'',reminder:-1,priority:3,project:'Launch',checklist:[{id:'s',title:'Check package',done:false}]};
 assert(c.valid(task));
 const unicode={...task,id:'🚀'.repeat(150),title:'🚀'.repeat(200),project:'🚀'.repeat(80),location:'🚀'.repeat(500),notes:'🚀'.repeat(10000),checklist:[{id:'🚀'.repeat(150),title:'🚀'.repeat(200),done:false}]};
 assert(c.valid(unicode));
 for(const [field,limit] of [['id',150],['title',200],['project',80],['location',500],['notes',10000]])assert(!c.valid({...unicode,[field]:'🚀'.repeat(limit+1)}),field);
 assert.equal(JSON.stringify(c.restore(c.backup([unicode]))[0]),JSON.stringify(unicode));
 for(const [field,values] of Object.entries({priority:[-1,4,true,'high'],project:[null,'*','x'.repeat(81)],checklist:[null,{},[{}],[{id:'s',title:'',done:false}],[{id:'s',title:'ok',done:1}],task.checklist.concat(task.checklist)]})) {
  for(const value of values)assert(!c.valid({...task,[field]:value}),field+JSON.stringify(value));
 }
 assert.equal(JSON.stringify(c.restore(c.backup([task]))[0]),JSON.stringify(task));
 assert(c.matches(task,'lau'));assert(c.matches(task,'pack'));
 const updated={...task,title:'Prepare final'};
 assert.equal(JSON.stringify(c.mergeEvents([task],[updated],[task])[0].checklist),JSON.stringify(task.checklist));
 const recurring={...task,date:'2032-01-05',time:'09:00',repeat:'weekly'};
 const completed=c.toggleTaskOccurrence([recurring],'t','2032-01-12');
 assert(completed.every(c.valid));assert.equal(completed.find(e=>e.id!=='t').priority,3);
 assert.equal(JSON.stringify(completed.find(e=>e.id!=='t').checklist),JSON.stringify(task.checklist));
}
console.log('Task detail validation, JSON backup, search and occurrence metadata preservation passed in app and widget.');
