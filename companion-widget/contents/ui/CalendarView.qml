import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.LocalStorage as SQL
import org.kde.kirigami as Kirigami
import "Calendar.js" as Cal

Item {
    id: root
    implicitWidth: 620
    implicitHeight: 690
    clip: true
    readonly property bool compact: height < 620
    readonly property bool narrow: width < 480
    readonly property color accentInk: light ? Qt.darker(accent,1.75) : Qt.lighter(accent,1.12)
    readonly property color panel: light ? "#f2f5fc" : "#172034"
    readonly property color field: light ? "#e7edf8" : "#243047"
    readonly property color danger: light ? "#ae204d" : "#ffabc6"
    property var events: []
    property date today: new Date()
    property date selected: new Date()
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
    readonly property bool modalOpen: editor.visible||transfer.visible||options.visible||filters.visible||dateJump.visible||deleteConfirm.visible
    property string error: ""
    property real glassOpacity: 0.80
    readonly property real minimumOpacity: light ? 0.92 : 0.76
    readonly property real renderOpacity: Math.max(minimumOpacity,glassOpacity)
    property color accent: "#a498ff"
    readonly property var colors: [accent, "#6edfc2", "#ffbd83", "#f49ac4"]
    readonly property var categories: ["Personal", "Work", "Important", "Leisure"]
    readonly property bool light: Kirigami.Theme.backgroundColor.r > 0.6
    readonly property color ink: light ? "#18243a" : "#f5f7ff"
    readonly property color muted: light ? "#46546a" : "#ccd6e8"
    readonly property color line: light ? "#220e254e" : "#32dbe5ff"
    readonly property date gridStart: Cal.monday(page)
    readonly property date weekStart: Cal.monday(selected)
    readonly property var dayItems: Cal.instances(events, selected, 1, "", categoryFilter,kindFilter)
    readonly property var agendaItems: Cal.instances(events, selected, 90, "", categoryFilter,kindFilter)
    property var db: null
    property bool dataReady: false

    function store(next) {
        if(!dataReady) { error="Saving disabled: calendar data could not be loaded safely."; return false; }
        try {
            var merged;
            db.transaction(function(tx) {
                var rows=tx.executeSql('SELECT value FROM state WHERE key=?',['events']);
                var current=rows.rows.length?JSON.parse(rows.rows.item(0).value):[];
                if(!Array.isArray(current)||!current.every(Cal.valid))throw Error('The database contains invalid events.');
                merged=Cal.mergeEvents(root.events,next,current);
                tx.executeSql('INSERT OR REPLACE INTO state VALUES (?,?)',['events',JSON.stringify(merged)]);
            });
            events=merged; error=""; return true;
        } catch(e) { error="Save failed: "+e; return false; }
    }
    function syncFromDisk() {
        if(!dataReady||modalOpen||!db)return;
        try {
            db.readTransaction(function(tx){
                var rows=tx.executeSql('SELECT value FROM state WHERE key=?',['events']);
                if(!rows.rows.length)return;
                var current=JSON.parse(rows.rows.item(0).value);
                if(!Array.isArray(current)||!current.every(Cal.valid))throw Error('Invalid calendar data.');
                if(JSON.stringify(current)!==JSON.stringify(root.events))root.events=current;
            });
        } catch(e) {error='Synchronisierung fehlgeschlagen: '+e;}
    }
    Timer {interval:3000;running:true;repeat:true;onTriggered:root.syncFromDisk()}
    function pref() {
        try { db.transaction(function(tx) { tx.executeSql('INSERT OR REPLACE INTO state VALUES (?,?)', ['preferences', JSON.stringify({opacity:glassOpacity,accent:String(accent)})]); }); }
        catch(e) { error="Could not save settings: "+e; }
    }
    function select(d) { selected=d; page=Cal.month(d,0); }
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
        if(mode===0) { page=Cal.month(page,n); selected=new Date(page); }
        else select(Cal.add(selected,n*(mode===1?7:30)));
    }
    function openEvent(e, date) {
        editor.original=e||null;
        editor.eventId=e?e.id:"";
        titleField.text=e?e.title:""; dateField.text=e&&e.date?e.date:Cal.key(date||selected);
        timeField.text=e&&e.time?e.time:"09:00"; durationField.value=e?e.minutes:60;
        allDay.checked=e?e.allDay:false; task.checked=e?e.task:false; scheduled.checked=e?!!e.date:true;
        repeatBox.currentIndex=e?["none","daily","weekly","monthly","yearly"].indexOf(e.repeat):0;
        untilField.text=e?e.until:""; locationField.text=e?e.location:""; notesField.text=e?e.notes:"";
        categoryBox.currentIndex=e?e.category:0; editor.validation=""; editor.open(); titleField.forceActiveFocus();
    }
    function openNewTask(date) {openEvent(null,date);task.checked=true;scheduled.checked=false;}
    function toggleTask(e,date) {
        try {store(Cal.toggleTaskOccurrence(events,e.id,date||e.date));}
        catch(problem) {error=String(problem);}
    }
    function dateText(d, format) { return d.toLocaleDateString(Qt.locale("en_GB"),format); }
    function dayCount(d) { return Cal.instances(events,d,1,"",categoryFilter,kindFilter).length; }
    Component.onCompleted: {
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
                if(prefs.rows.length) { var p=JSON.parse(prefs.rows.item(0).value); glassOpacity=Math.max(.2,Math.min(.98,p.opacity||.80)); accent=p.accent||'#a498ff'; }
            });
            dataReady=true;
            db.transaction(function(tx){tx.executeSql('INSERT OR REPLACE INTO state VALUES (?,?)',['planner-protocol',JSON.stringify({version:2,readyAt:new Date().toISOString()})]);});
        } catch(e) { error="Could not load calendar data: "+e; }
    }
    Timer { id:undoExpiry; interval:60000; onTriggered:root.deletedEntry=null }
    Shortcut { enabled:!root.modalOpen; sequence:"Ctrl+F"; onActivated: { searchInput.forceActiveFocus(); searchInput.selectAll(); } }
    Shortcut { enabled:!root.modalOpen; sequence:"Ctrl+N"; onActivated: { if(!editor.visible&&!transfer.visible) root.openEvent(null); } }
    Shortcut { enabled:!root.modalOpen; sequence:"Ctrl+L"; onActivated: { dateJump.error=""; jumpInput.text=Cal.key(root.selected); dateJump.open(); jumpInput.forceActiveFocus(); } }
    Timer { interval:60000; running:true; repeat:true; onTriggered:root.today=new Date() }

    component GlassButton: Button {
        id: control
        property color tint: root.ink
        leftPadding: 10
        rightPadding: 10
        topPadding: 6
        bottomPadding: 6
        implicitHeight: Math.max(34, contentItem.implicitHeight+topPadding+bottomPadding)
        implicitWidth: Math.max(34, contentItem.implicitWidth+leftPadding+rightPadding)
        contentItem: Text { textFormat:Text.PlainText; clip:true; text:control.text; opacity:control.enabled?1:.5; color:control.tint; font.pixelSize:12; font.weight:Font.Medium; horizontalAlignment:Text.AlignHCenter; verticalAlignment:Text.AlignVCenter; elide:Text.ElideRight }
        background: Rectangle { radius:11; color:control.down?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.25):control.hovered? (root.light?"#180e254e":"#18ffffff") : "transparent"; border.width:1; border.color:control.activeFocus||control.highlighted?root.accent:root.line }
    }
    component GlassField: TextField {
        opacity:enabled?1:.5
        selectionColor:root.accent; selectedTextColor:"#111a2b"
        color: root.ink
        placeholderTextColor: root.muted
        font.pixelSize: 12
        leftPadding: 10; rightPadding: 10; topPadding: 8; bottomPadding: 8
        implicitHeight: 36
        background: Rectangle { radius: 10; color: root.field; border.color: parent.activeFocus ? root.accent : root.line }
    }
    component GlassCheck: CheckBox {
        id: check
        padding:0; spacing:8; implicitHeight:32
        contentItem:Text { text:check.text; textFormat:Text.PlainText; color:root.ink; font.pixelSize:12; leftPadding:28; verticalAlignment:Text.AlignVCenter }
        indicator:Rectangle {
            x:0; y:(check.height-height)/2; width:20; height:20; radius:6
            color:check.checked?root.accent:root.field
            border.color:check.activeFocus?root.accent:root.line
            Text { anchors.centerIn:parent; visible:check.checked; text:"✓"; font.pixelSize:14; font.bold:true; color:"#111a2b" }
        }
    }
    component GlassSpin: SpinBox {
        id:spin
        opacity:enabled?1:.5
        implicitWidth:150; implicitHeight:36
        leftPadding:36; rightPadding:36; editable:true
        font.pixelSize:12
        contentItem:TextInput {
            text:spin.textFromValue(spin.value,spin.locale)
            font:spin.font; color:root.ink; selectionColor:root.accent; selectedTextColor:"#111a2b"
            horizontalAlignment:Text.AlignHCenter; verticalAlignment:Text.AlignVCenter
            readOnly:!spin.editable; validator:spin.validator
            inputMethodHints:Qt.ImhDigitsOnly; selectByMouse:true
            onEditingFinished: {
                var parsed=spin.valueFromText(text,spin.locale);
                if(Number.isFinite(parsed)) spin.value=Math.max(spin.from,Math.min(spin.to,Math.round(parsed)));
                text=Qt.binding(function(){return spin.textFromValue(spin.value,spin.locale);});
            }
        }
        up.indicator:Rectangle {
            x:spin.width-width; width:32; height:spin.height; radius:9
            color:spin.up.pressed?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.25):root.field
            Text { anchors.centerIn:parent; text:"+"; color:root.ink; font.pixelSize:18 }
        }
        down.indicator:Rectangle {
            width:32; height:spin.height; radius:9
            color:spin.down.pressed?Qt.rgba(root.accent.r,root.accent.g,root.accent.b,.25):root.field
            Text { anchors.centerIn:parent; text:"−"; color:root.ink; font.pixelSize:18 }
        }
        background:Rectangle { radius:10; color:root.field; border.color:spin.activeFocus?root.accent:root.line }
    }
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
            y:combo.height+4
            width:combo.width
            padding:4
            implicitHeight:Math.min(contentItem.implicitHeight+8,root.height-40)
            background:Rectangle { radius:12; color:root.panel; border.color:root.line }
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

    Rectangle {
        anchors.fill:parent; radius:28
        color:root.light?Qt.rgba(.9,.94,1,root.renderOpacity):Qt.rgba(.06,.09,.17,root.renderOpacity)
        border.width:1; border.color:root.line
        Rectangle { x:25; y:1; width:parent.width-50; height:1; color:root.light?"#cfffffff":"#80ffffff" }
        Rectangle { anchors.fill:parent; anchors.margins:1; radius:27; gradient:Gradient { GradientStop { position:0; color:"#16ffffff" } GradientStop { position:.4; color:"transparent" } GradientStop { position:1; color:"#0a9aafff" } } }
    }
    ColumnLayout {
        id: calendarLayout
        anchors.fill: parent
        anchors.margins: root.compact ? 14 : 18
        spacing: root.compact ? 5 : 8
        RowLayout {
            Layout.fillWidth:true
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
            Layout.fillWidth:true
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
            ScrollBar.vertical:ScrollBar { }
            Label { visible:agenda.count===0; anchors.centerIn:parent; width:Math.max(0,parent.width-20); text:root.globalMode?"No matching entries.\nTry a different search or filter.":"Room for your plans.\nStart with + Event."; color:root.muted; horizontalAlignment:Text.AlignHCenter; font.pixelSize:root.compact?11:13; lineHeight:1.3; wrapMode:Text.Wrap; textFormat:Text.PlainText }
        }
        RowLayout {
            visible:root.deletedEntry!==null
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
        id:filters
        parent:root; anchors.centerIn:parent; width:Math.min(root.width-24,360); modal:true; focus:true
        background:Rectangle { radius:20; color:root.panel; border.color:root.line }
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
        id:dateJump
        property string error:""
        parent:root; anchors.centerIn:parent; width:Math.min(root.width-24,380); modal:true; focus:true
        background:Rectangle { radius:20; color:root.panel; border.color:root.line }
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
        id:editor
        property string eventId:""
        property var original:null
        property string validation:""
        parent:root; anchors.centerIn:parent; width:Math.min(root.width-16,520); height:Math.min(root.height-16,660)
        modal:true; focus:true; closePolicy:Popup.CloseOnEscape
        background:Rectangle { radius:22; color:root.panel; border.color:root.line }
        contentItem:ColumnLayout {
            spacing:9
            RowLayout {
                Label { Layout.fillWidth:true; Layout.minimumWidth:0; text:editor.eventId?"Edit entry":"New entry"; font.pixelSize:root.narrow?17:20; font.weight:Font.DemiBold; color:root.ink; elide:Text.ElideRight }
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
                        ColumnLayout { Layout.fillWidth:true; Label { text:"Date (YYYY-MM-DD)"; color:root.muted } GlassField { id:dateField; Accessible.name:"Date in year-month-day format"; Layout.fillWidth:true; placeholderText:"2026-10-28"; maximumLength:10; selectByMouse:true } }
                        ColumnLayout { Label { text:"Time (HH:MM)"; color:root.muted } GlassField { id:timeField; Accessible.name:"Time in hours and minutes"; Layout.preferredWidth:100; enabled:!allDay.checked; maximumLength:5; selectByMouse:true } }
                    }
                    RowLayout {
                        GlassCheck { id:allDay; visible:!task.checked||scheduled.checked; text:"All day" }
                        GlassCheck { id:task; text:"Task"; onClicked:{if(checked&&!editor.original)scheduled.checked=false;else if(!checked)scheduled.checked=true;} }
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
                            Menu {id:projectChoices
                                Repeater {model:root.events.filter(function(e){return e.task&&e.project;}).map(function(e){return e.project;}).filter(function(v,i,a){return a.indexOf(v)===i;}).sort()
                                    delegate:MenuItem {required property string modelData;text:modelData;onTriggered:projectField.text=modelData}
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
                    Label { text:"Category"; color:root.muted }
                    GlassCombo { id:categoryBox; Accessible.name:"Category"; Layout.fillWidth:true; model:root.categories }
                    Label { visible:!task.checked||scheduled.checked; text:"Repeat"; color:root.muted }
                    GlassCombo { visible:!task.checked||scheduled.checked; id:repeatBox; Accessible.name:"Repeat"; Layout.fillWidth:true; model:["Once","Daily","Weekly","Monthly","Yearly"] }
                    Label { visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0; text:"Repeat until · YYYY-MM-DD (blank = no end)"; color:root.muted; font.pixelSize:11 }
                    GlassField { id:untilField; Accessible.name:"Repeat end date"; visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0; Layout.fillWidth:true; maximumLength:10; selectByMouse:true }
                    Label { visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>=3; Layout.fillWidth:true; text:"Dates that do not exist are skipped (e.g. February 31). Changes apply to the entire series."; color:root.muted; font.pixelSize:10; wrapMode:Text.Wrap }
                    Label { text:"Location"; color:root.muted }
                    GlassField { id:locationField; Accessible.name:"Location"; Layout.fillWidth:true; maximumLength:1000; placeholderText:"Location or video link"; selectByMouse:true }
                    Label { text:"Notes"; color:root.muted }
                    GlassArea { id:notesField; Accessible.name:"Notes"; Layout.fillWidth:true; Layout.preferredHeight:90; placeholderText:"Details, ideas, preparation …"; wrapMode:TextEdit.Wrap; selectByMouse:true }
                }
            }
            Label { textFormat:Text.PlainText; text:editor.validation; visible:text!==""; color:root.danger; Layout.fillWidth:true; wrapMode:Text.Wrap }
            Label { visible:(!task.checked||scheduled.checked)&&repeatBox.currentIndex>0; text:"Editing and deleting applies to the entire series."; font.pixelSize:10; color:root.muted; Layout.fillWidth:true; wrapMode:Text.Wrap }
            RowLayout {
                GlassButton { visible:editor.eventId!==""; text:"Delete …"; tint:root.danger; onClicked:deleteConfirm.open() }
                GlassButton { id:duplicateButton; visible:editor.eventId!==""; text:"Duplicate"; onClicked: { editor.eventId=""; editor.original=null; titleField.text=Array.from(titleField.text+" – Copy").slice(0,200).join(""); } Accessible.name:"Duplicate event as a template" }
                Item { Layout.fillWidth:true }
                GlassButton {
                    id:saveButton
                    text:"Save"; highlighted:true; tint:root.accentInk
                    onClicked: {
                        var previous=editor.original||root.events.filter(function(e){return e.id===editor.eventId;})[0];
                        var undated=task.checked&&!scheduled.checked;
                        var e=Object.assign({},previous||{},{id:editor.eventId||Date.now().toString(36)+'-'+Math.random().toString(36).slice(2),title:titleField.text.trim(),date:undated?"":dateField.text,time:undated?"":timeField.text,minutes:durationField.value,allDay:undated?false:allDay.checked,task:task.checked,done:previous?previous.done:false,repeat:undated?"none":["none","daily","weekly","monthly","yearly"][repeatBox.currentIndex],until:!undated&&repeatBox.currentIndex>0?untilField.text:"",category:categoryBox.currentIndex,location:locationField.text,notes:notesField.text});
                        if(undated){e.exceptions={};e.reminder=-1;}
                        if(task.checked) {
                            if(priorityBox.currentIndex||(previous&&previous.priority!==undefined))e.priority=priorityBox.currentIndex;
                            if(projectField.text.trim()||(previous&&previous.project!==undefined))e.project=projectField.text.trim();
                            if(editor.checklist.length||(previous&&previous.checklist!==undefined))e.checklist=JSON.parse(JSON.stringify(editor.checklist));
                        } else {delete e.priority;delete e.project;delete e.checklist;}
                        if(task.checked&&e.project==="*"){editor.validation="Choose a different project name; * is reserved.";return;}
                        if(task.checked&&!Cal.validTaskDetails(e)){editor.validation="Every checklist step needs a title of 1–200 characters. Fill in or remove empty steps.";return;}
                        if(!Cal.valid(e)) { editor.validation="Check the title and, for scheduled entries, the date, time and repeat end date. Notes can contain up to 10,000 characters."; return; }
                        var next=root.events.filter(function(v){return v.id!==e.id;}); next.push(e);
                        if(root.store(next)) { if(e.date)root.select(Cal.parse(e.date));else{searchInput.clear();kindBox.currentIndex=3;} editor.close(); } else editor.validation=root.error;
                    }
                }
            }
        }
    }
    Dialog {
        id:deleteConfirm; parent:root; anchors.centerIn:parent; modal:true; title:"Delete entry"
        width:Math.min(root.width-20,420)
        contentItem:Label { text:repeatBox.currentIndex>0?"The entire series will be deleted. You can restore it for 60 seconds afterwards.":"This entry will be deleted. You can restore it for 60 seconds afterwards."; color:root.ink; wrapMode:Text.Wrap }
        background:Rectangle { radius:20; color:root.panel; border.color:root.line }
        header:Label { text:deleteConfirm.title; color:root.ink; font.pixelSize:18; font.weight:Font.DemiBold; padding:14; wrapMode:Text.Wrap }
        footer:DialogButtonBox {
            background:Rectangle { color:root.panel; radius:16 }
            GlassButton { text:"Cancel"; DialogButtonBox.buttonRole:DialogButtonBox.RejectRole }
            GlassButton { text:"Delete"; tint:root.danger; DialogButtonBox.buttonRole:DialogButtonBox.AcceptRole }
        }
        onAccepted: {
            var removed=root.events.filter(function(e){return e.id===editor.eventId||e.seriesId===editor.eventId;});
            if(root.store(root.events.filter(function(e){return e.id!==editor.eventId&&e.seriesId!==editor.eventId;}))) {
                root.deletedEntry=removed.length?{entries:removed}:null; undoExpiry.restart(); editor.close();
            } else editor.validation=root.error;
        }
    }
    Popup {
        id:options; parent:root; anchors.centerIn:parent; width:Math.min(root.width-20,430); modal:true; focus:true
        background:Rectangle { radius:22; color:root.panel; border.color:root.line }
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
                            model:["#a498ff","#7dcfff","#6edfc2","#f49ac4","#ffbd83"]
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
        id:transfer; parent:root; anchors.centerIn:parent; width:root.width-20; height:root.height-30; modal:true; focus:true
        property bool importing:false
        property string title:""
        property string message:""
        background:Rectangle { radius:22; color:root.panel; border.color:root.line }
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
