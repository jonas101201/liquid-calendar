import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.LocalStorage as SQL

import "Calendar.js" as Cal
import "Theme.js" as Theme

Item {
    id: root
    implicitWidth: 620
    implicitHeight: 690
    clip: true
    readonly property bool compact: height < 620
    readonly property bool narrow: width < 480
    readonly property color accentInk: light ? Qt.darker(accent,2.35) : Qt.lighter(accent,1.12)
    readonly property var uiColors:Theme.palette(light,accent)
    readonly property color panel:uiColors.panel
    readonly property color field:uiColors.field
    readonly property color danger: light ? "#ae204d" : "#ffabc6"
    property var events: []
    property date today: new Date()
    property date selected: new Date()
    onSelectedChanged: {
        if(persistence&&persistence.selected!==Cal.key(selected))persistence.selectDate(Cal.key(selected));
    }
    property date page: new Date(new Date().getFullYear(), new Date().getMonth(), 1, 12)
    property int mode: 0
    property int categoryFilter: -1
    property string query: ""
    property int kindFilter: 0
    readonly property bool searching: query.trim().length>0
    readonly property bool globalMode: searching || kindFilter>=2
    readonly property var results: Cal.searchAll(events,query,categoryFilter,kindFilter,today)
    readonly property var suggestions: searching?Cal.dateSuggestions(query,today):[]
    property var deletedEntry: null
    readonly property bool modalOpen: editor.visible||transfer.visible||options.visible||filters.visible||dateJump.visible||deleteConfirm.visible||mergeDialog.visible
    property string error: ""
    property real glassOpacity: 0.80
    readonly property real minimumOpacity: light ? 0.72 : 0.60
    readonly property real renderOpacity: Math.max(minimumOpacity,glassOpacity)
    property color accent: "#7ceafa"
    readonly property var colors: [accent, "#6edfc2", "#ffbd83", "#f49ac4"]
    readonly property var categories: ["Personal", "Work", "Important", "Leisure"]
    property bool light: false
    property bool editorOnly: true
    property bool motionEnabled:true
    property var persistence: null
    onModalOpenChanged:if(!modalOpen&&persistence)events=persistence.events
    readonly property color ink:uiColors.ink
    readonly property color muted:uiColors.muted
    readonly property color line:uiColors.line
    readonly property date gridStart: Cal.monday(page)
    readonly property date weekStart: Cal.monday(selected)
    readonly property var dayItems: Cal.instances(events, selected, 1, "", categoryFilter,kindFilter)
    readonly property var agendaItems: Cal.instances(events, selected, 90, "", categoryFilter,kindFilter)
    property var db: null
    property bool dataReady: false

    function store(next) {
        if(!dataReady) { error="Saving disabled: calendar data could not be loaded safely."; return false; }
        if(persistence) {
            var result=persistence.storeJson(JSON.stringify(next),JSON.stringify(events));
            if(!result) { error=persistence.error; return false; }
            events=JSON.parse(result); error=""; return true;
        }
        try {
            db.transaction(function(tx) { tx.executeSql('INSERT OR REPLACE INTO state VALUES (?,?)', ['events', JSON.stringify(next)]); });
            events=next; error=""; return true;
        } catch(e) { error="Save failed: "+e; return false; }
    }
    function pref() {
        if(persistence) {persistence.savePreferences(glassOpacity,String(accent));return;}
        try { db.transaction(function(tx) { tx.executeSql('INSERT OR REPLACE INTO state VALUES (?,?)', ['preferences', JSON.stringify({opacity:glassOpacity,accent:String(accent)})]); }); }
        catch(e) { error="Could not save settings: "+e; }
    }
    function select(d) { if(!d||!Cal.parse(Cal.key(d)))return; selected=d; page=Cal.month(d,0); }
    function jump(d) {
        searchInput.clear(); kindBox.currentIndex=0; mode=0; select(d);
    }
    function jumpResult(entry) { jump(Cal.parse(entry.date)); }
    function undoDelete() {
        if(!deletedEntry)return;
        var next=events.slice();
        (deletedEntry.entries||[deletedEntry]).forEach(function(item){if(!next.some(function(e){return e.id===item.id;}))next.push(item);});
        if(store(next)) { deletedEntry=null; undoExpiry.stop(); }
    }
    function navigate(n) {
        if(mode===0) { var next=Cal.month(page,n);if(!Cal.parse(Cal.key(next)))return;page=next; selected=new Date(page); }
        else select(Cal.add(selected,n*(mode===1?7:30)));
    }
    function openEvent(e, date) {
        editor.selectedWeekdays=e&&e.weekdays?e.weekdays.slice():[];
        editor.checklist=JSON.parse(JSON.stringify(e&&e.checklist?e.checklist:[]));
        priorityBox.currentIndex=e&&e.priority?e.priority:0;projectField.text=e&&e.project?e.project:"";
        editor.draftOriginal=e||null;
        editor.eventId=e?e.id:"";
        var reminder=e&&e.reminder!==undefined?e.reminder:10;
        reminderBox.currentIndex=Math.max(0,[-1,0,5,10,30,60,1440].indexOf(reminder));
        titleField.text=e?e.title:""; dateField.text=e&&e.date?e.date:Cal.key(date||selected);
        timeField.text=e&&e.time?e.time:"09:00"; durationField.value=e?e.minutes:60;
        allDay.checked=e?e.allDay:false; task.checked=e?e.task:false; scheduled.checked=e?!!e.date:true;
        repeatBox.currentIndex=e?["none","daily","weekly","monthly","yearly"].indexOf(e.repeat):0;
        untilField.text=e?e.until:""; locationField.text=e?e.location:""; notesField.text=e?e.notes:"";
        categoryBox.currentIndex=e?e.category:0; editor.detailsExpanded=!!(e&&(e.category!==0||e.repeat!=="none"||e.location||e.notes||(e.reminder!==undefined&&e.reminder!==10&&e.reminder!==-1))); editor.validation=""; editor.open(); titleField.forceActiveFocus();
    }
    function openDraft(event) {openEvent(event);editor.eventId="";editor.draftOriginal=null;}
    function templateSnapshot(){
        return JSON.stringify({id:"template-draft",title:titleField.text.trim(),date:dateField.text,time:timeField.text,minutes:durationField.value,allDay:allDay.checked,task:false,done:false,repeat:"none",until:"",category:categoryBox.currentIndex,location:locationField.text,notes:notesField.text,reminder:[-1,0,5,10,30,60,1440][reminderBox.currentIndex]});
    }
    function openNewTask(date) {openEvent(null,date);task.checked=true;scheduled.checked=false;}
    function toggleTask(e,date) {
        if(persistence) {persistence.toggleTaskSnapshot(e.id,date||e.date,JSON.stringify(e));return;}
        try {store(Cal.toggleTaskOccurrence(events,e.id,date||e.date));}
        catch(problem) {error=String(problem);}
    }
    function dateText(d, format) { return d.toLocaleDateString(Qt.locale("en_GB"),format); }
    function dayCount(d) { return Cal.instances(events,d,1,"",categoryFilter,kindFilter).length; }
    Component.onCompleted: {
        if(persistence) {events=persistence.events;dataReady=true;return;}
        try {
            db=SQL.LocalStorage.openDatabaseSync('JonasLiquidCalendar','1.0',"Local Liquid Glass Calendar",4000000);
            db.transaction(function(tx) {
                tx.executeSql('CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)');
                var rows=tx.executeSql('SELECT value FROM state WHERE key=?',['events']);
                if(rows.rows.length) {
                    var loaded=JSON.parse(rows.rows.item(0).value);
                    if(!Array.isArray(loaded) || !loaded.every(Cal.valid)) throw Error("Saved events are corrupted.");
                    events=loaded;
                }
                var prefs=tx.executeSql('SELECT value FROM state WHERE key=?',['preferences']);
                if(prefs.rows.length) { var p=JSON.parse(prefs.rows.item(0).value); glassOpacity=Math.max(.2,Math.min(.98,p.opacity||.80)); accent=p.accent||'#7ceafa'; }
            });
            dataReady=true;
        } catch(e) { error="Could not load calendar data: "+e; }
    }
    Timer { id:undoExpiry; interval:60000; onTriggered:root.deletedEntry=null }
    Shortcut { enabled:!root.persistence&&!root.editorOnly&&!root.modalOpen; sequence:"Ctrl+F"; onActivated: { searchInput.forceActiveFocus(); searchInput.selectAll(); } }
    Shortcut { enabled:!root.persistence&&!root.editorOnly&&!root.modalOpen; sequence:"Ctrl+N"; onActivated: { if(!editor.visible&&!transfer.visible) root.openEvent(null); } }
    Shortcut { enabled:!root.persistence&&!root.editorOnly&&!root.modalOpen; sequence:"Ctrl+L"; onActivated: { dateJump.error=""; jumpInput.text=Cal.key(root.selected); dateJump.open(); jumpInput.forceActiveFocus(); } }
    Timer { interval:60000; running:true; repeat:true; onTriggered:root.today=new Date() }

    component GlassButton: Button {
        id: control
        property color tint: root.ink
        scale:control.down&&root.motionEnabled?.97:1
        Behavior on scale {enabled:root.motionEnabled;NumberAnimation {duration:180;easing.type:Easing.OutCubic}}
        leftPadding: 10
        rightPadding: 10
        topPadding: 6
        bottomPadding: 6
        implicitHeight: Math.max(34, contentItem.implicitHeight+topPadding+bottomPadding)
        implicitWidth: Math.max(34, contentItem.implicitWidth+leftPadding+rightPadding)
        contentItem: Text { textFormat:Text.PlainText; clip:true; text:control.text; opacity:control.enabled?1:.5; color:control.tint; font.pixelSize:12; font.weight:Font.Medium; horizontalAlignment:Text.AlignHCenter; verticalAlignment:Text.AlignVCenter; elide:Text.ElideRight }
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:9;shadowStrength:0;highlight:control.hovered?1:0;glassOpacity:root.light?(control.hovered?.9:.6):(control.hovered?.45:.2);border.color:control.activeFocus||control.highlighted?root.accent:root.line}
    }
    component GlassField: GlassTextField { inkColor:root.ink; accentColor:root.accent; fieldColor:root.field; lineColor:root.line; mutedColor:root.muted }
    component GlassCheck: GlassCheckBox { inkColor:root.ink; accentColor:root.accent; fieldColor:root.field; lineColor:root.line }
    component GlassSpin: GlassSpinBox { inkColor:root.ink; accentColor:root.accent; fieldColor:root.field; lineColor:root.line }
    component GlassArea: TextArea {
        color:root.ink; placeholderTextColor:root.muted; textFormat:TextEdit.PlainText
        selectionColor:root.accent; selectedTextColor:"#111a2b"
        padding:10; font.pixelSize:12
        background:Rectangle { radius:10; color:root.field; border.color:parent.activeFocus?root.accent:root.line }
    }
    component GlassCombo: ComboBox {
        id: combo
        font.pixelSize: 12
        leftPadding: 10; rightPadding: 28
        implicitHeight: 36
        contentItem: Text { text:combo.displayText; textFormat:Text.PlainText; font:combo.font; color:root.ink; elide:Text.ElideRight; verticalAlignment:Text.AlignVCenter }
        indicator: Text { x:combo.width-width-10; anchors.verticalCenter:parent.verticalCenter; text:"⌄"; font.pixelSize:16; color:root.muted }
        background: Rectangle { radius:10; color:root.field; border.color:combo.activeFocus?root.accent:root.line }
        delegate: ItemDelegate {
            required property int index
            required property var modelData
            width: combo.width
            height: 38
            highlighted: combo.highlightedIndex===index
            contentItem: Text { text:modelData; textFormat:Text.PlainText; font:combo.font; color:root.ink; elide:Text.ElideRight; verticalAlignment:Text.AlignVCenter }
            background: Rectangle { radius:7; color:parent.highlighted?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.24):"transparent" }
        }
        popup: Popup {
            enter:GlassTransition {motionEnabled:root.motionEnabled}
            exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
            y:combo.height+4
            width:combo.width
            padding:4
            implicitHeight:Math.min(contentItem.implicitHeight+8,root.height-40)
            background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:16;glassOpacity:1;shadowStrength:.2}
            contentItem:ListView { clip:true; implicitHeight:contentHeight; model:combo.popup.visible?combo.delegateModel:null; currentIndex:combo.highlightedIndex; ScrollIndicator.vertical:ScrollIndicator {} }
        }
    }
    component EventCard: Rectangle {
        id: card
        required property var entry
        property bool showDate: false
        implicitHeight: root.compact ? 62 : 72
        radius: 13
        color: root.light ? "#80ffffff" : "#16ffffff"
        border.color: root.line
        RowLayout {
            anchors.fill:parent; anchors.margins:10; spacing:10
            Rectangle { Layout.preferredWidth:3; Layout.fillHeight:true; radius:2; color:root.colors[card.entry.event.category] }
            GlassCheck { visible:card.entry.event.task; checked:card.entry.event.done; onClicked:root.toggleTask(card.entry.event,card.entry.date); Accessible.name:card.entry.event.repeat!=="none"&&card.entry.event.done?"Reopen completed series":"Task completed" }
            ColumnLayout {
                Layout.fillWidth:true; Layout.minimumWidth:0; spacing:4
                Label { Layout.fillWidth:true; textFormat:Text.PlainText; text:card.entry.event.title; color:root.ink; font.pixelSize:13; font.weight:Font.DemiBold; font.strikeout:card.entry.event.task&&card.entry.event.done; elide:Text.ElideRight }
                Label { Layout.fillWidth:true; textFormat:Text.PlainText; text:Cal.isUndated(card.entry.event)?"Undated · "+card.entry.event.minutes+" min":(card.showDate?root.dateText(Cal.parse(card.entry.date),root.globalMode?"dd.MM.yyyy":"ddd, dd MMM")+" · ":"")+(card.entry.event.allDay?"All day":card.entry.event.time+" · "+card.entry.event.minutes+" min")+(card.entry.event.location?" · "+card.entry.event.location:"")+(card.entry.event.repeat!=="none"?" · Series":""); color:root.muted; font.pixelSize:11; elide:Text.ElideRight }
            }
            GlassButton { text:root.globalMode&&!Cal.isUndated(card.entry.event)?"Go to day":"Open"; onClicked:root.globalMode&&!Cal.isUndated(card.entry.event)?root.jumpResult(card.entry):root.openEvent(card.entry.event); Accessible.name:(root.globalMode&&!Cal.isUndated(card.entry.event)?"Jump to day: ":"Edit entry: ")+card.entry.event.title }
        }
    }

    LiquidSurface {id:calendarGlass;visible:!root.editorOnly;anchors.fill:parent;light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;glassOpacity:root.renderOpacity;radius:28}
    ColumnLayout {
        id: calendarLayout
        visible:!root.editorOnly
        anchors.fill: parent
        anchors.margins: root.compact ? 14 : 18
        spacing: root.compact ? 5 : 8
        RowLayout {
            visible:!root.persistence;Layout.fillWidth:true
            ColumnLayout {
                Layout.fillWidth:true; Layout.minimumWidth:0; spacing:3
                Label { text:"YOUR CALENDAR"; color:root.accentInk; font.pixelSize:10; font.letterSpacing:2; font.weight:Font.DemiBold }
                Label { Layout.fillWidth:true; Layout.minimumWidth:0; text:root.searching?"Search":root.kindFilter>=2?"Tasks":(root.mode===0?root.page:root.selected).toLocaleDateString(Qt.locale("en_GB"),"MMMM yyyy"); color:root.ink; font.pixelSize:root.narrow?20:26; font.weight:Font.DemiBold; elide:Text.ElideRight }
            }
            GlassButton { text:"Today"; onClicked:root.jump(new Date()); Accessible.name:"Go to today" }
            GlassButton { text:root.narrow?"+":"+ Event"; tint:root.accentInk; highlighted:true; onClicked:root.openEvent(null); Accessible.name:"Create event"; ToolTip.visible:hovered; ToolTip.text:"Create event" }
            GlassButton { text:"⋯"; onClicked:options.open(); Accessible.name:"Settings and backup" }
        }
        RowLayout {
            visible:!root.persistence;Layout.fillWidth:true
            Repeater {
                model:["Month","Week","Agenda"]
                delegate:GlassButton { required property int index; required property string modelData; text:modelData; highlighted:root.mode===index; tint:root.mode===index?root.accentInk:root.muted; onClicked: { searchInput.clear(); kindBox.currentIndex=0; root.mode=index; } }
            }
            Item { Layout.fillWidth:true }
            GlassButton { text:"‹"; enabled:!root.globalMode; onClicked:root.navigate(-1); Accessible.name:"Previous period" }
            GlassButton { text:"›"; enabled:!root.globalMode; onClicked:root.navigate(1); Accessible.name:"Next period" }
        }
        RowLayout {
            Layout.fillWidth:true
            GlassField {
                id:searchInput
                maximumLength:400
                Layout.fillWidth:true; Layout.minimumWidth:0; rightPadding:34
                placeholderText:"Search all months …"
                onTextChanged:root.query=text
                selectByMouse:true
                Accessible.name:"Search all events and dates"
                Keys.onEscapePressed:clear()
                onAccepted: {
                    if(root.results.length)root.jumpResult(root.results[0]);
                    else if(root.suggestions.length)root.jump(root.suggestions[0].date);
                }
                GlassButton { visible:searchInput.text.length>0; width:26; height:26; leftPadding:0; rightPadding:0; topPadding:0; bottomPadding:0; anchors.right:parent.right; anchors.rightMargin:5; anchors.verticalCenter:parent.verticalCenter; text:"×"; onClicked:searchInput.clear(); Accessible.name:"Clear search" }
            }
            GlassButton { text:"Filter"+(root.categoryFilter>=0||root.kindFilter>0?" ●":""); highlighted:root.categoryFilter>=0||root.kindFilter>0; onClicked:filters.open(); Accessible.name:"Filter categories and tasks" }
        }
        RowLayout {
            visible:root.suggestions.length>0
            Layout.fillWidth:true
            Repeater {
                model:root.suggestions
                delegate:GlassButton {
                    required property var modelData
                    Layout.fillWidth:true; Layout.preferredWidth:1; Layout.minimumWidth:0
                    text:modelData.label+" · "+root.dateText(modelData.date,"dd.MM.yy")
                    ToolTip.visible:hovered; ToolTip.text:root.dateText(modelData.date,"dddd, dd MMMM yyyy")
                    tint:root.accentInk
                    onClicked:root.jump(modelData.date)
                    Accessible.name:"Go to date "+root.dateText(modelData.date,"dd MMMM yyyy")
                }
            }
        }
        Label { visible:root.globalMode; Layout.fillWidth:true; text:"All years · one matching occurrence per series"; color:root.muted; font.pixelSize:10; wrapMode:Text.Wrap }
        Label { Layout.maximumHeight:root.compact?42:70; maximumLineCount:3; elide:Text.ElideRight; visible:root.error!==""; textFormat:Text.PlainText; text:root.error; color:root.danger; wrapMode:Text.Wrap; Layout.fillWidth:true }
        ColumnLayout {
            visible:root.mode===0&&!root.globalMode; Layout.fillWidth:true; spacing:root.compact?2:4
            RowLayout {
                Layout.fillWidth:true; spacing:4
                Label { text:"Wk"; color:root.muted; font.pixelSize:10; Layout.preferredWidth:20 }
                Repeater { model:["MO","TU","WE","TH","FR","SA","SU"]; delegate:Label { required property string modelData; text:modelData; color:root.muted; horizontalAlignment:Text.AlignHCenter; font.pixelSize:10; Layout.fillWidth:true; Layout.preferredWidth:1 } }
            }
            Repeater {
                model:6
                delegate:RowLayout {
                    id:weekRow
                    required property int index
                    Layout.fillWidth:true; spacing:4
                    Label { text:Cal.weekNumber(Cal.add(root.gridStart,weekRow.index*7)); color:root.muted; font.pixelSize:10; Layout.preferredWidth:20 }
                    Repeater {
                        model:7
                        delegate:Rectangle {
                            id:cell
                            required property int index
                            readonly property date day:Cal.add(root.gridStart,weekRow.index*7+index)
                            readonly property bool chosen:Cal.key(day)===Cal.key(root.selected)
                            readonly property bool now:Cal.key(day)===Cal.key(root.today)
                            readonly property var entries:Cal.instances(root.events,day,1,"",root.categoryFilter,root.kindFilter)
                            readonly property int count:entries.length
                            readonly property color eventColor:count>0?root.colors[entries[0].event.category]:root.accent
                            Layout.fillWidth:true; Layout.preferredWidth:1; implicitHeight:Math.max(24,Math.min(44,(root.height-400)/6))
                            radius:11
                            color:chosen?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.38):count>0?Qt.rgba(eventColor.r,eventColor.g,eventColor.b,root.light?.20:.23):hover.hovered?(root.light?"#130e254e":"#14ffffff"):"transparent"
                            border.width:activeFocus||now||chosen||count>0?1:0
                            border.color:activeFocus||now||chosen?root.accent:Qt.rgba(eventColor.r,eventColor.g,eventColor.b,.60)
                            Label {
                                anchors.centerIn:parent; anchors.verticalCenterOffset:-2; anchors.horizontalCenterOffset:root.compact&&cell.count>0?-3:0
                                text:cell.day.getDate()
                                color:cell.count>0||cell.day.getMonth()===root.page.getMonth()?root.ink:root.muted
                                opacity:cell.count>0||cell.day.getMonth()===root.page.getMonth()?1:.70
                                font.pixelSize:root.compact?12:cell.count>0?15:13
                                font.weight:cell.now||cell.count>0?Font.Bold:Font.Normal
                            }
                            Rectangle {
                                visible:cell.count>0
                                anchors.top:parent.top; anchors.right:parent.right; anchors.margins:2
                                width:root.compact?(cell.count>9?16:11):(cell.count>9?20:14); height:root.compact?11:14; radius:7
                                color:cell.eventColor
                                Label { anchors.centerIn:parent; text:cell.count>9?"9+":cell.count; color:"#111a2b"; font.pixelSize:root.compact?8:9; font.bold:true }
                            }
                            Row {
                                anchors.horizontalCenter:parent.horizontalCenter; anchors.bottom:parent.bottom; anchors.bottomMargin:4; spacing:3
                                Repeater {
                                    model:Math.min(3,cell.count)
                                    delegate:Rectangle {
                                        required property int index
                                        width:9; height:3; radius:2
                                        color:root.colors[cell.entries[index].event.category]
                                    }
                                }
                            }
                            ToolTip.visible:hover.hovered&&count>0
                            ToolTip.delay:350
                            ToolTip.text:entries.slice(0,5).map(function(item){return (item.event.allDay?"All day":item.event.time)+" · "+item.event.title;}).join("\n")+(count>5?"\n+ "+(count-5)+" more":"")
                            activeFocusOnTab:true
                            Keys.onReturnPressed:root.openEvent(null,cell.day)
                            Keys.onSpacePressed:root.select(cell.day)
                            HoverHandler { id:hover }
                            TapHandler { onTapped: { cell.forceActiveFocus(); root.select(cell.day); } onDoubleTapped:root.openEvent(null,cell.day) }
                            Accessible.role:Accessible.Button
                            Accessible.name:root.dateText(day,"dddd, dd MMMM yyyy")+", "+count+(count===1?" event":" events")
                        }
                    }
                }
            }
        }
        RowLayout {
            visible:root.mode===1&&!root.globalMode; Layout.fillWidth:true; spacing:4
            Repeater {
                model:7
                delegate:GlassButton {
                    id:weekDay
                    required property int index
                    readonly property date day:Cal.add(root.weekStart,index)
                    readonly property int count:root.dayCount(day)
                    readonly property bool chosen:Cal.key(day)===Cal.key(root.selected)
                    Layout.fillWidth:true; Layout.preferredWidth:1; implicitHeight:60
                    text:root.dateText(day,"ddd")+"\n"+day.getDate()
                    tint:count>0?root.accentInk:root.ink
                    background:Rectangle {
                        radius:11
                        color:weekDay.chosen?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.38):weekDay.count>0?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.20):weekDay.hovered?"#18ffffff":"transparent"
                        border.width:1
                        border.color:weekDay.chosen||weekDay.count>0?root.accent:root.line
                    }
                    Rectangle {
                        visible:weekDay.count>0
                        anchors.top:parent.top; anchors.right:parent.right; anchors.margins:2
                        width:weekDay.count>9?20:14; height:14; radius:7; color:root.accent
                        Label { anchors.centerIn:parent; text:weekDay.count>9?"9+":weekDay.count; color:"#111a2b"; font.pixelSize:9; font.bold:true }
                    }
                    onClicked:root.select(day)
                    Accessible.name:root.dateText(day,"dddd, dd MMMM yyyy")+", "+count+(count===1?" entry":" entries")
                }
            }
        }
        RowLayout {
            Layout.fillWidth:true
            Label { Layout.fillWidth:true; text:root.globalMode?(root.searching?"SEARCH RESULTS · ALL MONTHS":"TASKS · ALL MONTHS"):root.mode===2?"FROM "+root.dateText(root.selected,"dd MMMM").toUpperCase():root.mode===1?root.dateText(root.weekStart,"dd MMM")+" – "+root.dateText(Cal.add(root.weekStart,6),"dd MMM"):root.dateText(root.selected,"dddd, dd MMMM"); color:root.muted; font.pixelSize:11; font.weight:Font.DemiBold; elide:Text.ElideRight }
            Label { text:agenda.count+(agenda.count===1?" entry":" entries"); color:root.muted; font.pixelSize:10 }
        }
        ListView {
            id:agenda
            Layout.fillWidth:true; Layout.fillHeight:true; Layout.minimumHeight:60; Layout.preferredHeight:root.compact?60:140; clip:true; spacing:7
            model:root.globalMode?root.results:root.mode===2?root.agendaItems:root.mode===1?Cal.instances(root.events,root.weekStart,7,"",root.categoryFilter,root.kindFilter):root.dayItems
            delegate:EventCard { required property var modelData; width:agenda.width; entry:modelData; showDate:root.globalMode||root.mode!==0 }
            ScrollBar.vertical:GlassScrollBar {light:root.light;accent:root.accentInk;motionEnabled:root.motionEnabled}
            Label { visible:agenda.count===0; anchors.centerIn:parent; width:Math.max(0,parent.width-20); text:root.globalMode?"No matching entries.\nTry a different search or filter.":"Room for your plans.\nStart with + Event."; color:root.muted; horizontalAlignment:Text.AlignHCenter; font.pixelSize:root.compact?11:13; lineHeight:1.3; wrapMode:Text.Wrap; textFormat:Text.PlainText }
        }
        RowLayout {
            visible:root.deletedEntry!==null&&!root.persistence
            Layout.fillWidth:true
            Label { Layout.fillWidth:true; Layout.minimumWidth:0; text:"Entry deleted"; color:root.muted; font.pixelSize:11; elide:Text.ElideRight }
            GlassButton { text:"Undo"; tint:root.accentInk; onClicked:root.undoDelete() }
        }
        Rectangle { Layout.fillWidth:true; height:1; color:root.line }
        RowLayout {
            Label { Layout.fillWidth:true; Layout.minimumWidth:0; text:root.error?"Save error":root.dataReady?(root.narrow?"●  Saved locally":"●  Saved locally · no cloud"):"Loading calendar …"; color:root.error?root.danger:root.muted; font.pixelSize:10; elide:Text.ElideRight }
            Label { text:root.events.length+(root.events.length===1?" entry":" entries"); color:root.muted; font.pixelSize:10 }
        }
    }

    Popup {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:filters
        parent:root; anchors.centerIn:parent; width:Math.min(root.width-24,360); modal:true; focus:true
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        contentItem:ColumnLayout {
            spacing:10
            Label { text:"Your view"; color:root.ink; font.pixelSize:18; font.weight:Font.DemiBold }
            Label { text:"Category"; color:root.muted }
            GlassCombo { id:categoryFilterBox; Layout.fillWidth:true; model:["All categories"].concat(root.categories); onCurrentIndexChanged:root.categoryFilter=currentIndex-1; Accessible.name:"Filter category" }
            Label { text:"Entries"; color:root.muted }
            GlassCombo { id:kindBox; Layout.fillWidth:true; model:["All entries","Events only","All tasks","Open tasks","Completed tasks"]; onCurrentIndexChanged:root.kindFilter=currentIndex; Accessible.name:"Entry type and task status" }
            RowLayout {
                GlassButton { text:"Reset"; onClicked: { categoryFilterBox.currentIndex=0; kindBox.currentIndex=0; } }
                Item { Layout.fillWidth:true }
                GlassButton { text:"Done"; tint:root.accentInk; onClicked:filters.close() }
            }
        }
    }
    Popup {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:dateJump
        property string error:""
        parent:root; anchors.centerIn:parent; width:Math.min(root.width-24,380); modal:true; focus:true
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        function go() {
            var dates=Cal.dateSuggestions(jumpInput.text,root.today);
            if(!dates.length) { error="Try 2027-03-15, 15.03.2027 or tomorrow."; return; }
            if(dates.length>1) { error="Several dates match. Enter a more specific name or date."; return; }
            root.jump(dates[0].date); close();
        }
        contentItem:ColumnLayout {
            spacing:10
            Label { text:"Jump to date"; color:root.ink; font.pixelSize:18; font.weight:Font.DemiBold }
            GlassField { id:jumpInput; Layout.fillWidth:true; placeholderText:"Date, tomorrow or November"; selectByMouse:true; onAccepted:dateJump.go(); Accessible.name:"Date or day name" }
            Label { Layout.fillWidth:true; text:dateJump.error; visible:text!==""; wrapMode:Text.Wrap; color:root.danger }
            RowLayout {
                GlassButton { text:"Cancel"; onClicked:dateJump.close() }
                Item { Layout.fillWidth:true }
                GlassButton { text:"Open"; tint:root.accentInk; onClicked:dateJump.go() }
            }
        }
    }
    Popup {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:editor
        Popup {
            enter:GlassTransition {motionEnabled:root.motionEnabled}
            exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
            id:templateNamePopup;parent:editor.contentItem;anchors.centerIn:parent;width:Math.min(parent.width-8,420);modal:true;focus:true;padding:16
            property string error:""
            background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:16;glassOpacity:1}
            contentItem:ColumnLayout {
                spacing:10
                Label {text:"Save event template";color:root.ink;font.pixelSize:18}
                Label {text:"Keeps title, time, duration, category, reminder, location and notes. Dates and repeats are not copied.";color:root.muted;Layout.fillWidth:true;wrapMode:Text.Wrap}
                GlassField {id:templateNameField;Layout.fillWidth:true;maximumLength:160;Accessible.name:"Template name";placeholderText:"e.g. Team meeting"}
                Label {visible:templateNamePopup.error!=="";text:templateNamePopup.error;textFormat:Text.PlainText;color:root.danger;Layout.fillWidth:true;wrapMode:Text.Wrap}
                RowLayout {
                    GlassButton {text:"Cancel";onClicked:templateNamePopup.close()}
                    Item {Layout.fillWidth:true}
                    GlassButton {id:saveTemplateButton;text:"Save template";highlighted:true;enabled:templateNameField.text.trim().length>0;onClicked:{if(root.persistence.saveTemplate(templateNameField.text,root.templateSnapshot()))templateNamePopup.close();else templateNamePopup.error=root.persistence.error;}}
                }
            }
        }
        DatePicker {id:untilPicker;parent:editor.contentItem;anchors.centerIn:parent;light:root.light;ink:root.ink;accent:root.accentInk;panel:root.panel;field:root.field;line:root.line;onPicked:function(value){untilField.text=value;}}
        DatePicker {id:datePicker;parent:editor.contentItem;anchors.centerIn:parent;light:root.light;ink:root.ink;accent:root.accentInk;panel:root.panel;field:root.field;line:root.line;onPicked:function(value){dateField.text=value;}}
        TimePicker {id:timePicker;parent:editor.contentItem;anchors.centerIn:parent;light:root.light;ink:root.ink;accent:root.accentInk;panel:root.panel;field:root.field;line:root.line;onPicked:function(value){timeField.text=value;}}
        property var selectedWeekdays:[]
        function weeklyDays(){var date=Cal.parse(dateField.text);return selectedWeekdays.length?selectedWeekdays:[Cal.isoWeekday(date||new Date())];}
        function toggleWeekday(day){
            var days=weeklyDays().slice();var index=days.indexOf(day);
            if(index>=0){if(days.length===1){validation="Choose at least one weekday.";return;}days.splice(index,1);}else days.push(day);
            selectedWeekdays=days.sort(function(a,b){return a-b;});validation="";
        }
        property string eventId:""
        property var draftOriginal:null
        property string validation:""
        property bool detailsExpanded:false
        property var checklist:[]
        parent:root; anchors.centerIn:parent; width:Math.min(root.width-16,520); height:Math.min(root.height-16,660)
        modal:true; focus:true; closePolicy:Popup.CloseOnEscape
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        contentItem:ColumnLayout {
            spacing:9
            RowLayout {
                Label { Layout.fillWidth:true; Layout.minimumWidth:0; text:editor.draftOriginal&&editor.draftOriginal.occurrenceOf?"Edit this occurrence":editor.eventId&&root.events.some(function(e){return e.id===editor.eventId;})?(task.checked?"Edit task":"Edit event"):(task.checked?"New task":"New event"); font.pixelSize:root.narrow?17:20; font.weight:Font.DemiBold; color:root.ink; elide:Text.ElideRight }
                GlassButton { text:"Close"; onClicked:editor.close() }
            }
            ScrollView {
                id:editorScroll; Layout.fillWidth:true; Layout.fillHeight:true; contentWidth:availableWidth; clip:true
                ColumnLayout {
                    width:editorScroll.availableWidth; spacing:8
                    Label { text:"Title"; color:root.muted }
                    GlassField { id:titleField; Accessible.name:"Title"; Layout.fillWidth:true; maximumLength:400; placeholderText:"What are you planning?"; selectByMouse:true }
                    RowLayout {
                        visible:!task.checked||scheduled.checked
                        Layout.fillWidth:true
                        ColumnLayout { Layout.fillWidth:true; RowLayout {Layout.fillWidth:true;Label {text:"Date";color:root.muted;Layout.fillWidth:true} GlassButton {text:"Pick…";Accessible.name:"Choose event date";onClicked:datePicker.openFor(dateField.text)}} GlassField { id:dateField; Accessible.name:"Date in year-month-day format"; Layout.fillWidth:true; placeholderText:"2026-10-28"; maximumLength:10; selectByMouse:true } }
                        ColumnLayout { RowLayout {Label {text:"Time";color:root.muted} GlassButton {text:"Pick…";enabled:!allDay.checked;Accessible.name:"Choose start time";onClicked:timePicker.openFor(timeField.text)}} GlassField { id:timeField; Accessible.name:"Time in hours and minutes"; Layout.preferredWidth:100; enabled:!allDay.checked; maximumLength:5; selectByMouse:true } }
                    }
                    RowLayout {
                        GlassCheck { id:allDay; visible:!task.checked||scheduled.checked; text:"All day" }
                        GlassCheck { id:task; text:"Task"; onClicked:{if(checked&&!editor.draftOriginal)scheduled.checked=false;else if(!checked)scheduled.checked=true;} }
                    }
                    GlassCheck {id:scheduled;visible:task.checked;text:"Schedule in calendar";enabled:repeatBox.currentIndex===0;Accessible.name:"Schedule task with a date"}
                    Label {visible:task.checked&&!scheduled.checked;Layout.fillWidth:true;text:"Undated · stays in your task list. You can schedule it later.";color:root.muted;font.pixelSize:11;wrapMode:Text.Wrap}
                    Label {visible:task.checked&&repeatBox.currentIndex>0;Layout.fillWidth:true;text:"Repeating tasks require a date.";color:root.muted;font.pixelSize:11;wrapMode:Text.Wrap}
                    ColumnLayout {
                        visible:task.checked;Layout.fillWidth:true;spacing:8
                        RowLayout {
                            Layout.fillWidth:true
                            ColumnLayout {
                                Layout.fillWidth:true
                                Label {text:"Priority";color:root.muted}
                                GlassCombo {id:priorityBox;objectName:"taskPriority";Layout.fillWidth:true;model:["No priority","Low","Medium","High"];Accessible.name:"Task priority"}
                            }
                            ColumnLayout {
                                Layout.fillWidth:true;Layout.minimumWidth:0
                                Label {text:"Project · optional";color:root.muted}
                                GlassField {id:projectField;objectName:"taskProject";Layout.fillWidth:true;maximumLength:160;placeholderText:"e.g. Website launch";Accessible.name:"Task project";selectByMouse:true}
                            }
                        }
                        GlassButton {text:"Choose existing project ▾";visible:root.events.some(function(e){return e.task&&e.project;});onClicked:projectChoices.open()
                            ActionMenu {light:root.light;accent:root.accentInk;id:projectChoices
                                Repeater {model:root.events.filter(function(e){return e.task&&e.project;}).map(function(e){return e.project;}).filter(function(v,i,a){return a.indexOf(v)===i;}).sort()
                                    delegate:ActionMenuItem {light:root.light;accent:root.accentInk;required property string modelData;text:modelData;onTriggered:projectField.text=modelData}
                                }
                            }
                        }
                        RowLayout {
                            Layout.fillWidth:true
                            Label {text:"Checklist · "+editor.checklist.filter(function(c){return c.done;}).length+" / "+editor.checklist.length;color:root.muted;Layout.fillWidth:true}
                            GlassButton {id:addChecklistStep;objectName:"addChecklistStep";text:"+ Step";enabled:editor.checklist.length<100;onClicked:editor.checklist=editor.checklist.concat([{id:Date.now().toString(36)+'-'+Math.random().toString(36).slice(2),title:"",done:false}])}
                        }
                        Repeater {id:checklistRows;model:editor.checklist
                            delegate:RowLayout {
                                required property int index
                                required property var modelData
                                Layout.fillWidth:true
                                GlassCheck {checked:modelData.done;Accessible.name:"Complete checklist step";onClicked:{editor.checklist[index].done=checked;editor.checklist=editor.checklist.slice();}}
                                GlassField {Layout.fillWidth:true;text:modelData.title;maximumLength:400;placeholderText:"Describe this step";Accessible.name:"Checklist step title";onTextEdited:{editor.checklist[index].title=text;editor.validation="";} selectByMouse:true}
                                GlassButton {text:"−";Accessible.name:"Remove checklist step";onClicked:{var items=editor.checklist.slice();items.splice(index,1);editor.checklist=items;}}
                            }
                        }
                        Label {visible:repeatBox.currentIndex>0;text:"Checklist changes in this editor apply to the selected entry or series. Open a single occurrence for independent progress.";color:root.muted;font.pixelSize:10;Layout.fillWidth:true;wrapMode:Text.Wrap}
                    }
                    RowLayout {
                        Label { text:"Duration (minutes)"; color:root.muted }
                        GlassSpin { id:durationField; Accessible.name:"Duration in minutes"; from:5; to:1440; stepSize:5; editable:true; enabled:(task.checked&&!scheduled.checked)||!allDay.checked }
                    }
                    GlassButton {Layout.fillWidth:true;text:editor.detailsExpanded?"Fewer options ▴":"More options ▾";onClicked:editor.detailsExpanded=!editor.detailsExpanded;Accessible.name:"Show category, repeat, reminder, location and notes"}
                    ColumnLayout {
                        visible:editor.detailsExpanded;Layout.fillWidth:true;spacing:8
                    Label { text:"Category"; color:root.muted }
                    GlassCombo { id:categoryBox; Accessible.name:"Category"; Layout.fillWidth:true; model:root.categories }
                    Label { visible:!task.checked||scheduled.checked; text:"Repeat"; color:root.muted }
                    GlassCombo { visible:!task.checked||scheduled.checked; id:repeatBox; Accessible.name:"Repeat"; Layout.fillWidth:true; model:["Once","Daily","Weekly","Monthly","Yearly"] }
                    ColumnLayout {
                        visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex===2;Layout.fillWidth:true;spacing:6
                        Label {text:"Repeats on";color:root.muted}
                        Flow {Layout.fillWidth:true;Layout.preferredHeight:childrenRect.height;spacing:4
                            Repeater {id:repeatDays;model:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
                                delegate:GlassButton {required property int index;required property string modelData;text:modelData;highlighted:editor.weeklyDays().indexOf(index)>=0;tint:highlighted?root.accentInk:root.ink;Accessible.name:"Repeat on "+modelData;onClicked:editor.toggleWeekday(index)}
                            }
                        }
                        Label {text:"Every week from the start date, on the selected days.";color:root.muted;font.pixelSize:10;Layout.fillWidth:true;wrapMode:Text.Wrap}
                    }
                    Label { visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0; text:"Repeat until · YYYY-MM-DD (blank = no end)"; color:root.muted; font.pixelSize:11 }
                    GlassField { id:untilField; Accessible.name:"Repeat end date"; visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0; Layout.fillWidth:true; maximumLength:10; selectByMouse:true }
                    GlassButton {visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0;text:"Choose repeat end…";onClicked:untilPicker.openFor(untilField.text||dateField.text)}
                    Label { visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>=3; Layout.fillWidth:true; text:"Dates that do not exist are skipped (e.g. February 31). Changes apply to the entire series."; color:root.muted; font.pixelSize:10; wrapMode:Text.Wrap }
                    Label { visible:!task.checked||scheduled.checked; text:"Reminder"; color:root.muted }
                    GlassCombo { visible:!task.checked||scheduled.checked; id:reminderBox; Layout.fillWidth:true; model:["No reminder","At start","5 minutes before","10 minutes before","30 minutes before","1 hour before","1 day before"]; Accessible.name:"Reminder time" }
                    Label { text:"Location"; color:root.muted }
                    GlassField { id:locationField; Accessible.name:"Location"; Layout.fillWidth:true; maximumLength:1000; placeholderText:"Location or video link"; selectByMouse:true }
                    Label { text:"Notes"; color:root.muted }
                    GlassArea { id:notesField; Accessible.name:"Notes"; Layout.fillWidth:true; Layout.preferredHeight:90; placeholderText:"Details, ideas, preparation …"; wrapMode:TextEdit.Wrap; selectByMouse:true }
                    }
                }
            }
            Label { textFormat:Text.PlainText; text:editor.validation; visible:text!==""; color:root.danger; Layout.fillWidth:true; wrapMode:Text.Wrap }
            Label { visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0; text:"Editing and deleting applies to the entire series."; font.pixelSize:10; color:root.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
            RowLayout {
                GlassButton { visible:editor.eventId!==""; text:"Delete …"; tint:root.danger; onClicked:deleteConfirm.open() }
                GlassButton {id:editorToolsButton;visible:editor.eventId!==""|| (!!root.persistence&&!task.checked);text:"More ▾";Accessible.name:"Entry actions";onClicked:editorActions.open()
                    ActionMenu {accent:root.accentInk;id:editorActions;parent:editorToolsButton;light:root.light;y:editorToolsButton.height+4
                        ActionMenuItem {accent:root.accentInk;id:duplicateButton;light:root.light;visible:editor.eventId!=="";text:"Duplicate";onTriggered:{editor.eventId="";editor.draftOriginal=null;titleField.text=Array.from(titleField.text+" – Copy").slice(0,200).join("");}}
                        ActionMenuItem {accent:root.accentInk;id:mergeButton;objectName:"mergeEventsAction";light:root.light;text:"Merge with another event…";visible:!!root.persistence&&!!editor.draftOriginal&&!editor.draftOriginal.task&&editor.draftOriginal.repeat==="none"&&!editor.draftOriginal.seriesId&&!root.events.some(function(child){return child.seriesId===editor.eventId;});onTriggered:root.openMerge()}
                        ActionMenuItem {accent:root.accentInk;id:templateButton;light:root.light;visible:!!root.persistence&&!task.checked;text:"Save template…";onTriggered:{templateNameField.text=titleField.text;templateNamePopup.error="";templateNamePopup.open();}}
                    }
                }
                Item { Layout.fillWidth:true }
                GlassButton {
                    id:saveButton
                    text:"Save"; highlighted:true; tint:root.accentInk
                    onClicked: {
                        var e=root.currentDraft();if(!e)return;
                        var next=root.events.filter(function(v){return v.id!==e.id;}); next.push(e);
                        if(root.store(next)) { if(e.date)root.select(Cal.parse(e.date));else{searchInput.clear();kindBox.currentIndex=3;} editor.close(); } else editor.validation=root.error;
                    }
                }
            }
        }
    }
    function currentDraft() {
        var previous=editor.draftOriginal||root.events.filter(function(e){return e.id===editor.eventId;})[0];
        var undated=task.checked&&!scheduled.checked;
        var e=Object.assign({},previous||{},{id:editor.eventId||Date.now().toString(36)+'-'+Math.random().toString(36).slice(2),title:titleField.text.trim(),date:undated?"":dateField.text,time:undated?"":timeField.text,minutes:durationField.value,allDay:undated?false:allDay.checked,task:task.checked,done:previous?previous.done:false,repeat:undated?"none":["none","daily","weekly","monthly","yearly"][repeatBox.currentIndex],until:!undated&&repeatBox.currentIndex>0?untilField.text:"",category:categoryBox.currentIndex,location:locationField.text,notes:notesField.text,reminder:undated?-1:[-1,0,5,10,30,60,1440][reminderBox.currentIndex]});
        if(e.repeat==="weekly")e.weekdays=editor.weeklyDays().slice();else delete e.weekdays;
        if(e.repeat==="weekly"&&e.until&&Cal.valid(e)&&!Cal.unskippedNext(e,Cal.parse(e.date))){editor.validation="No selected weekdays fall within this date range.";return;}
        if(undated){e.exceptions={};e.reminder=-1;}
        if(task.checked) {
            if(priorityBox.currentIndex||(previous&&previous.priority!==undefined))e.priority=priorityBox.currentIndex;
            if(projectField.text.trim()||(previous&&previous.project!==undefined))e.project=projectField.text.trim();
            if(editor.checklist.length||(previous&&previous.checklist!==undefined))e.checklist=JSON.parse(JSON.stringify(editor.checklist));
        } else {delete e.priority;delete e.project;delete e.checklist;}
        if(task.checked&&e.project==="*"){editor.validation="Choose a different project name; * is reserved.";return;}
        if(task.checked&&!Cal.validTaskDetails(e)){editor.validation="Every checklist step needs a title of 1–200 characters. Fill in or remove empty steps.";return;}
        if(!Cal.valid(e)) { editor.validation="Check the title and, for scheduled entries, the date, time and repeat end date. Notes can contain up to 10,000 characters."; return; }
        return e;
    }
    function openMerge() {
        var draft=currentDraft();if(!draft)return;
        if(draft.task||draft.repeat!=="none") {editor.validation="Merge individual events or occurrences. Keep Repeat set to Once.";return;}
        editor.validation="";
        mergeDialog.draft=JSON.stringify(draft);
        mergeDialog.first=JSON.stringify(editor.draftOriginal);
        mergeDialog.choices=persistence.mergeChoices(mergeDialog.first,mergeDialog.draft);
        mergeChoice.currentIndex=mergeDialog.choices.length?0:-1;
        mergeDialog.message="";mergeDialog.open();
    }
    Dialog {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:mergeDialog;objectName:"mergeEventsDialog";parent:root;anchors.centerIn:parent;modal:true
        width:Math.max(280,Math.min(root.width-20,500));height:Math.min(root.height-20,520)
        property string first:""
        property string draft:""
        property var choices:[]
        property string message:""
        readonly property string second:mergeChoice.currentIndex>=0&&mergeChoice.currentIndex<choices.length?JSON.stringify(choices[mergeChoice.currentIndex]):""
        readonly property var preview:second&&root.persistence?root.persistence.mergePreview(first,second,draft):({error:"No compatible events on this day. Choose an event or an individual occurrence."})
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        contentItem:ColumnLayout {
            spacing:12
            Label {text:"Merge events";color:root.ink;font.pixelSize:20}
            Label {text:"Includes your current editor changes. Choose a second event on the edited date. Only selected occurrences are combined; future repeats stay unchanged.";color:root.muted;Layout.fillWidth:true;wrapMode:Text.Wrap}
            GlassCombo {id:mergeChoice;objectName:"mergeEventChoice";Layout.fillWidth:true;model:mergeDialog.choices.map(function(e){return (e.allDay?"All day":e.time)+" · "+e.title+(e.occurrenceOf?" · This occurrence":"");});Accessible.name:"Event to merge"}
            ScrollView {
                Layout.fillWidth:true;Layout.fillHeight:true;contentWidth:availableWidth;clip:true
                Label {width:parent.width;textFormat:Text.PlainText;wrapMode:Text.Wrap;color:root.ink;text:mergeDialog.preview.event?mergeDialog.preview.event.title+"\n\n"+mergeDialog.preview.event.date+" · "+(mergeDialog.preview.event.allDay?"All day":mergeDialog.preview.event.time+" · "+mergeDialog.preview.event.minutes+" min")+"\n\n"+mergeDialog.preview.event.location+"\n"+mergeDialog.preview.event.notes:mergeDialog.preview.error}
            }
            Label {text:"Keeps this event's category. Combines titles, locations and notes; covers both time ranges (including gaps). Uses the earliest enabled reminder. Undo restores both entries.";color:root.muted;Layout.fillWidth:true;wrapMode:Text.Wrap;font.pixelSize:11}
            Label {text:mergeDialog.message;color:root.danger;visible:text!=="";Layout.fillWidth:true;wrapMode:Text.Wrap}
            RowLayout {
                GlassButton {text:"Cancel";onClicked:mergeDialog.close()}
                Item {Layout.fillWidth:true}
                GlassButton {id:confirmMerge;objectName:"confirmMerge";text:"Merge two events";highlighted:true;enabled:!!mergeDialog.preview.event;onClicked:{var targetDate=mergeDialog.preview.event.date;if(root.persistence.mergeEvents(mergeDialog.first,mergeDialog.second,mergeDialog.draft)){root.select(Cal.parse(targetDate));mergeDialog.close();editor.close();}else mergeDialog.message=root.persistence.error;}}
            }
        }
    }
    Dialog {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:deleteConfirm; parent:root; anchors.centerIn:parent; modal:true; title:"Delete entry"
        width:Math.max(300,Math.min(root.width-20,420))
        height:header.implicitHeight+contentItem.implicitHeight+footer.implicitHeight+topPadding+bottomPadding
        contentItem:Label { text:repeatBox.currentIndex>0?"The entire series will be deleted. You can undo the last change in the app.":"This entry will be deleted. You can undo the last change in the app."; color:root.ink; wrapMode:Text.Wrap }
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        header:Label { text:deleteConfirm.title; color:root.ink; font.pixelSize:18; font.weight:Font.DemiBold; padding:14; wrapMode:Text.Wrap }
        footer:DialogButtonBox {
            background:Rectangle { color:root.panel; radius:16 }
            GlassButton { text:"Cancel"; DialogButtonBox.buttonRole:DialogButtonBox.RejectRole }
            GlassButton { text:"Delete"; tint:root.danger; DialogButtonBox.buttonRole:DialogButtonBox.AcceptRole }
        }
        onAccepted: {
            if(editor.draftOriginal&&editor.draftOriginal.occurrenceOf) {
                var draft=editor.draftOriginal;
                if(persistence.deleteOccurrence(draft.occurrenceOf,draft.occurrenceDate,draft.originHash))editor.close();
                else editor.validation=persistence.error;
                return;
            }
            var removed=root.events.filter(function(e){return e.id===editor.eventId||e.seriesId===editor.eventId;});
            if(root.store(root.events.filter(function(e){return e.id!==editor.eventId&&e.seriesId!==editor.eventId;}))) {
                root.deletedEntry=removed.length?{entries:removed}:null; undoExpiry.restart(); editor.close();
            } else editor.validation=root.error;
        }
    }
    Popup {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:options; parent:root; anchors.centerIn:parent; width:Math.min(root.width-20,430); modal:true; focus:true
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        height:Math.min(root.height-24,540)
        contentItem:ColumnLayout {
            spacing:10
            Label { Layout.fillWidth:true; text:"Your glass, your calendar"; color:root.ink; font.pixelSize:19; font.weight:Font.DemiBold; wrapMode:Text.Wrap }
            ScrollView {
                id:optionsScroll
                Layout.fillWidth:true; Layout.fillHeight:true
                contentWidth:availableWidth; clip:true
                ColumnLayout {
                    width:optionsScroll.availableWidth; spacing:12
                    GlassButton { Layout.fillWidth:true; text:"Jump to date …"; onClicked: { options.close(); jumpInput.text=Cal.key(root.selected); dateJump.error=""; dateJump.open(); } }
                    Label { text:"Ctrl+F · Search    Ctrl+N · New event\nCtrl+L · Jump to date"; color:root.muted; font.pixelSize:11; wrapMode:Text.Wrap; Layout.fillWidth:true }
                    Label { text:"Opacity"; color:root.muted }
                    Slider { Layout.fillWidth:true; from:root.minimumOpacity; to:.98; value:root.renderOpacity; Accessible.name:"Glass opacity"; onMoved: { root.glassOpacity=value; root.pref(); } }
                    Label { text:"Accent color"; color:root.muted }
                    RowLayout {
                        Layout.fillWidth:true
                        Repeater {
                            model:["#7ceafa","#8cbcff","#72ebce","#c2adff","#ffa8cf"]
                            delegate:Button {
                                required property int index
                                required property string modelData
                                Layout.fillWidth:true; Layout.preferredWidth:1; implicitHeight:36
                                Accessible.name:["Purple","Blue","Mint","Pink","Apricot"][index]
                                background:Rectangle { radius:10; color:modelData; border.width:root.accent.toString()===modelData||parent.activeFocus?3:0; border.color:root.ink }
                                onClicked: { root.accent=modelData; root.pref(); }
                            }
                        }
                    }
                    Label { text:"Your events stay on this computer."; color:root.muted; font.pixelSize:12; wrapMode:Text.Wrap; Layout.fillWidth:true }
                    GlassButton { Layout.fillWidth:true; text:"Export backup"; onClicked: { transfer.importing=false; transfer.title="Copy JSON backup"; transfer.message=""; transferText.text=Cal.backup(root.events); options.close(); transfer.open(); } }
                    GlassButton { Layout.fillWidth:true; text:"Import backup …"; onClicked: { transfer.importing=true; transfer.title="Merge backup"; transferText.text=""; transfer.message=""; options.close(); transfer.open(); } }
                    GlassButton { Layout.fillWidth:true; text:"Export events as ICS"; onClicked: { transfer.importing=false; transfer.title="Copy ICS"; transfer.message=""; transferText.text=Cal.ics(root.events); options.close(); transfer.open(); } }
                }
            }
            GlassButton { Layout.fillWidth:true; text:"Done"; onClicked:options.close() }
        }
    }

    Popup {
        enter:GlassTransition {motionEnabled:root.motionEnabled}
        exit:GlassTransition {entering:false;motionEnabled:root.motionEnabled}
        id:transfer; parent:root; anchors.centerIn:parent; width:root.width-20; height:root.height-30; modal:true; focus:true
        property bool importing:false
        property string title:""
        property string message:""
        background:LiquidSurface {light:root.light;tint:root.accent;motionEnabled:root.motionEnabled;radius:18;glassOpacity:1}
        contentItem:ColumnLayout {
            Label { Layout.fillWidth:true; text:transfer.title; color:root.ink; font.pixelSize:18; wrapMode:Text.Wrap }
            Label { Layout.fillWidth:true; text:transfer.importing?"Paste JSON. New IDs are added; existing IDs remain unchanged.":"Select all (Ctrl+A), copy (Ctrl+C) and save to a .json or .ics file."; color:root.muted; font.pixelSize:11; wrapMode:Text.Wrap }
            ScrollView { Layout.fillWidth:true; Layout.fillHeight:true; GlassArea { id:transferText; Accessible.name:"Calendar backup"; readOnly:!transfer.importing; selectByMouse:true; wrapMode:TextEdit.Wrap; textFormat:TextEdit.PlainText; font.family:"monospace"; font.pixelSize:11 } }
            Label { Layout.fillWidth:true; textFormat:Text.PlainText; text:transfer.message; visible:text!==""; color:root.accentInk; wrapMode:Text.Wrap }
            RowLayout {
                GlassButton { text:"Close"; onClicked:transfer.close() }
                Item { Layout.fillWidth:true }
                GlassButton { visible:!transfer.importing; text:"Select all"; onClicked: { transferText.forceActiveFocus(); transferText.selectAll(); } }
                GlassButton { visible:transfer.importing; text:"Import"; highlighted:true; onClicked: {
                    try {
                        var imported=Cal.restore(transferText.text), ids=Object.create(null); root.events.forEach(function(e){ids[e.id]=true;});
                        var added=imported.filter(function(e){return !ids[e.id];});
                        if(root.store(root.events.concat(added))) transfer.message=added.length+(added.length===1?" entry added.":" entries added.");
                    } catch(e) { transfer.message="Import cancelled: "+e; }
                } }
            }
        }
    }
}
