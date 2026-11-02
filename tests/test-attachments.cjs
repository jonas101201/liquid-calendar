const fs=require('fs'),vm=require('vm'),assert=require('assert');
for(const source of ['qml/Calendar.js','companion-widget/contents/ui/Calendar.js']) {
 const c={};vm.createContext(c);vm.runInContext(fs.readFileSync(source,'utf8'),c);
 const file={id:'a'.repeat(64),name:'Lernzettel 日本語.pdf',size:123};
 const task={id:'task',title:'Study',date:'',time:'',minutes:60,allDay:false,task:true,done:false,repeat:'none',until:'',category:0,location:'',notes:'',reminder:-1,attachments:[file]};
 assert(c.valid(task));assert(c.matches(task,'lernzettel'));assert(c.matches(task,'日本語'));
 assert(!c.valid({...task,attachments:[file,file]}));
 for(const invalid of [{...file,name:'../escape'},{...file,name:'a\\b'},{...file,size:true},{...file,name:'bad\nname'},{...file,id:'X'.repeat(64)}])assert(!c.valid({...task,attachments:[invalid]}));
 assert.throws(()=>c.backup([task]),/desktop app/);
 assert.throws(()=>c.restore(JSON.stringify({format:'liquid-glass-calendar',version:1,events:[task]})),/references alone/);
 assert.throws(()=>c.restore(JSON.stringify({format:'liquid-glass-calendar',version:2,events:[task],files:{}})),/desktop app/);
 const changed=c.toggleTaskOccurrence([task],task.id,'');assert.equal(changed[0].attachments[0].name,file.name);
 const plain={...task,attachments:[]};assert.equal(c.restore(c.backup([plain]))[0].id,'task');
}
console.log('App/widget attachment metadata, filename search, task completion preservation and complete-backup guards passed.');
