import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id:win
    objectName:"plannerWindow"
    visible:true
    width:1280; height:860
    minimumWidth:980; minimumHeight:planner.widgetCompatible?680:780
    title:"Liquid Calendar — "+planner.version
    color:light?"#f1f3f7":"#101217"
    property bool trayAvailable:false
    readonly property bool motionEnabled:planner.animationsEnabled
    SystemPalette {id:systemPalette}
    readonly property bool light:planner.theme==="light"||(planner.theme==="auto"&&systemPalette.window.r>.6)
    readonly property color ink:light?"#202631":"#f0f2f6"
    readonly property color muted:light?"#596373":"#adb5c4"
    readonly property color panel:light?"#fafbfe":"#1a1d25"
    readonly property color field:light?"#edf0f5":"#242833"
    readonly property color line:light?"#191c2b42":"#16ffffff"
    readonly property color accent:light?"#6652ce":"#b2a5f4"
    readonly property color danger:light?"#ad2850":"#ffabc6"
    readonly property var weekData:planner.weekItems
    property var planningTask:null
    property var suggestedSlots:[]
    property string exportKind:"json"
    property string slotDate:""
    property string slotError:""
    property var expandedChecklists:({})
    function checklistKey(record){return (record.event.seriesId||record.id)+"|"+(record.event.originalDate||record.occurrenceDate||"");}
    property date clockNow:new Date()
    Timer {interval:60000;running:true;repeat:true;onTriggered:win.clockNow=new Date()}
    readonly property var nextAppointment: {
        var now=Qt.formatDateTime(clockNow,"yyyy-MM-dd");
        var time=Qt.formatDateTime(clockNow,"HH:mm");
        var items=planner.dayItems.filter(function(e){return !e.allDay&&!(e.task&&e.done)&&(planner.selected!==now||e.time>=time);});
        return items.length?items[0]:null;
    }
    onClosing:function(close) {if(trayAvailable&&planner.remindersEnabled){close.accepted=false;win.hide();}else Qt.quit();}

    component Action: Button {
        id:button
        property bool primary:false
        property bool navigation:false
        property color textColor:win.ink
        leftPadding:10;rightPadding:10;topPadding:6;bottomPadding:6
        implicitHeight:38
        implicitWidth:Math.max(38,contentItem.implicitWidth+22)
        contentItem:Text {text:button.text; textFormat:Text.PlainText; color:button.primary&&!button.navigation?(win.light?"#ffffff":"#171620"):button.textColor; opacity:button.enabled?1:.45; font.pixelSize:13; font.weight:Font.Medium; horizontalAlignment:button.navigation?Text.AlignLeft:Text.AlignHCenter;leftPadding:button.navigation?4:0;verticalAlignment:Text.AlignVCenter;elide:Text.ElideRight}
        scale:button.down&&win.motionEnabled?.98:1
        Behavior on scale {enabled:win.motionEnabled;NumberAnimation {duration:120;easing.type:Easing.OutCubic}}
        background:Rectangle {
            radius:10
            color:button.primary?(button.navigation?(win.light?"#146652ce":"#1da99be9"):(win.light?"#6655df":"#b4a5f6")):button.hovered?(win.light?"#09000000":"#0cffffff"):"transparent"
            border.width:button.activeFocus?1:0
            border.color:win.accent
            Behavior on color {enabled:win.motionEnabled;ColorAnimation {duration:120}}
            Rectangle {visible:button.navigation&&button.primary;x:0;anchors.verticalCenter:parent.verticalCenter;width:3;height:16;radius:1;color:win.accent}
        }
    }
    component Surface: LiquidSurface {light:win.light;motionEnabled:win.motionEnabled;glassOpacity:win.light?.97:.96}
    component Field: TextField {
        color:win.ink;placeholderTextColor:win.muted;selectionColor:"#b5a6ff";selectedTextColor:"#171d32"
        font.pixelSize:13;padding:11;implicitHeight:40;selectByMouse:true
        background:LiquidSurface {light:win.light;motionEnabled:win.motionEnabled;radius:10;shadowStrength:0;glassOpacity:win.light?.96:.92;border.color:parent.activeFocus?win.accent:win.line}
    }
    component Entry: Surface {
        id:entry
        required property var record
        property bool showDate:false
        property bool compact:false
        readonly property bool checklistExpanded:win.expandedChecklists[win.checklistKey(record)]===true
        function setChecklistExpanded(expanded){var state=Object.assign({},win.expandedChecklists);state[win.checklistKey(record)]=expanded;win.expandedChecklists=state;}
        function toggleStep(stepId){planner.toggleChecklist(record.id,record.occurrenceDate,stepId,record.fingerprint)}
        implicitHeight:82+(checklistExpanded?record.checklist.length*38+8:0)
        radius:10
        shadowStrength:0
        border.width:0
        color:entryHover.hovered?(win.light?"#08a4adbd":"#08ffffff"):"transparent"
        HoverHandler {id:entryHover}
        Rectangle {x:12;y:parent.height-1;width:parent.width-24;height:1;color:win.line;opacity:.7}
        RowLayout {
            anchors.left:parent.left;anchors.right:parent.right;anchors.top:parent.top;anchors.margins:12;height:58;spacing:10
            Rectangle {width:3;Layout.preferredHeight:26;Layout.alignment:Qt.AlignVCenter;radius:1;color:entry.record.conflict?win.danger:entry.record.color}
            Action {visible:entry.record.task;text:entry.record.done?"✓":"○";Accessible.name:entry.record.repeated&&entry.record.done?"Reopen completed series":"Toggle task completion";onClicked:planner.toggleTask(entry.record.id,entry.record.occurrenceDate,entry.record.fingerprint)}
            ColumnLayout {
                Layout.fillWidth:true;Layout.minimumWidth:0;spacing:5
                Label {Layout.fillWidth:true;text:entry.record.title;textFormat:Text.PlainText;color:win.ink;font.pixelSize:14;font.weight:Font.DemiBold;font.strikeout:entry.record.done;elide:Text.ElideRight}
                Label {Layout.fillWidth:true;text:entry.record.unscheduled?"Undated · "+entry.record.minutes+" min":(entry.showDate?entry.record.date+" · ":"")+(entry.record.allDay?"All day":(entry.record.carry?"Continued · ":"")+entry.record.time+" · "+entry.record.minutes+" min")+(entry.record.conflict?" · Overlap":"");color:entry.record.conflict?win.danger:win.muted;font.pixelSize:11;elide:Text.ElideRight}
                Label {visible:entry.record.task&&(entry.record.priority>0||entry.record.project.length>0);Layout.fillWidth:true;text:(["","Low priority","Medium priority","High priority"])[entry.record.priority]+(entry.record.priority&&entry.record.project?" · ":"")+entry.record.project;textFormat:Text.PlainText;color:entry.record.priority===3?win.danger:win.accent;font.pixelSize:11;elide:Text.ElideRight}
            }
            Action {visible:entry.record.task&&entry.record.checklist.length>0;text:entry.record.checklistDone+"/"+entry.record.checklist.length+(entry.checklistExpanded?" ▴":" ▾");Accessible.name:"Show checklist progress";onClicked:entry.setChecklistExpanded(!entry.checklistExpanded)}
            Action {visible:entry.record.task&&!entry.record.done;text:entry.compact?"Plan":"Find time";onClicked:win.planTask(entry.record)}
            Action {visible:entry.record.repeated;text:"Series";onClicked:planner.edit(entry.record.id,entry.record.occurrenceDate,false);Accessible.name:"Edit entire series"}
            Action {text:"↗";Accessible.name:entry.record.task?"Edit task":"Edit event";ToolTip.visible:hovered;ToolTip.text:Accessible.name;onClicked:planner.edit(entry.record.id,entry.record.occurrenceDate,true)}
        }
        ColumnLayout {
            visible:entry.checklistExpanded
            anchors.left:parent.left;anchors.right:parent.right;anchors.top:parent.top;anchors.topMargin:82;anchors.leftMargin:26;anchors.rightMargin:18;spacing:0
            Repeater {model:entry.checklistExpanded?entry.record.checklist:[]
                delegate:RowLayout {
                    required property var modelData
                    Layout.fillWidth:true;Layout.preferredHeight:38
                    Action {text:modelData.done?"✓":"○";Accessible.name:"Toggle checklist step "+modelData.title;onClicked:entry.toggleStep(modelData.id)}
                    Label {Layout.fillWidth:true;text:modelData.title;textFormat:Text.PlainText;color:win.muted;font.pixelSize:12;font.strikeout:modelData.done;elide:Text.ElideRight}
                }
            }
        }
    }
    function dateValue(s){return new Date(Number(s.slice(0,4)),Number(s.slice(5,7))-1,Number(s.slice(8,10)),12);}
    function refreshSlots(){planner.clearError();slotError="";suggestedSlots=planner.slotsOn(planningTask.id,planningTask.occurrenceDate,slotDate);slotError=planner.error;}
    function planTask(record){planningTask=record;slotDate=planner.selected;slotDateField.text=slotDate;refreshSlots();slotPopup.open();}
    function shiftSlots(n){var d=dateValue(slotDate);d.setDate(d.getDate()+n);slotDate=Qt.formatDateTime(d,"yyyy-MM-dd");slotDateField.text=slotDate;refreshSlots();}
    function newEvent(){editorSurface.openEvent(null,dateValue(planner.selected));}
    Shortcut {sequence:"Ctrl+N";enabled:!editorSurface.modalOpen;onActivated:win.newEvent()}
    Shortcut {sequence:"Ctrl+F";enabled:!editorSurface.modalOpen;onActivated:{planner.setView("search");globalSearch.forceActiveFocus();}}
    Shortcut {sequence:"Ctrl+Z";enabled:!editorSurface.modalOpen&&planner.canUndo;onActivated:planner.undo()}
    Shortcut {sequence:"Ctrl+Q";onActivated:Qt.quit()}

    Popup {
        id:projectPopup;parent:Overlay.overlay;anchors.centerIn:parent;width:420;modal:true;focus:true
        background:LiquidSurface {light:win.light;radius:18;glassOpacity:1}
        contentItem:ColumnLayout {
            spacing:12
            Label {text:"Edit project";color:win.ink;font.pixelSize:20}
            Label {text:"Rename to an existing project to merge them. Clearing the project keeps all tasks.";Layout.fillWidth:true;wrapMode:Text.Wrap;color:win.muted}
            Field {id:renameProjectField;Layout.fillWidth:true;maximumLength:160;Accessible.name:"Project name"}
            RowLayout {
                Action {text:"Clear project";onClicked:{planner.renameProject(planner.projectFilter,"");projectPopup.close();}}
                Item {Layout.fillWidth:true}
                Action {text:"Cancel";onClicked:projectPopup.close()}
                Action {text:"Save";primary:true;enabled:renameProjectField.text.trim().length>0&&Array.from(renameProjectField.text.trim()).length<=80&&renameProjectField.text.trim()!=="*";onClicked:{planner.renameProject(planner.projectFilter,renameProjectField.text);projectPopup.close();}}
            }
        }
    }
    Canvas {
        id:liquidBackdrop
        x:-18;y:-18;width:win.width+36;height:win.height+36
        opacity:1
        onWidthChanged:requestPaint()
        onHeightChanged:requestPaint()
        Connections {target:win;function onLightChanged(){liquidBackdrop.requestPaint();}}
        onPaint:{
            var ctx=getContext("2d");ctx.clearRect(0,0,width,height);
            var base=ctx.createLinearGradient(0,0,width,height);
            base.addColorStop(0,win.light?"#f4f5f9":"#111318");base.addColorStop(1,win.light?"#eef0f6":"#151820");
            ctx.fillStyle=base;ctx.fillRect(0,0,width,height);
            function glow(x,y,r,color){var g=ctx.createRadialGradient(x,y,0,x,y,r);g.addColorStop(0,color);g.addColorStop(1,"transparent");ctx.fillStyle=g;ctx.fillRect(x-r,y-r,r*2,r*2);}
            glow(width*.96,height*.02,width*.62,win.light?"rgba(160,146,225,.14)":"rgba(133,111,209,.08)");
            glow(width*.65,height*.98,width*.56,win.light?"rgba(143,183,211,.08)":"rgba(65,140,165,.05)");
        }
        SequentialAnimation on x {
            running:win.motionEnabled&&win.visible&&win.active;loops:Animation.Infinite
            NumberAnimation {to:-5;duration:14000;easing.type:Easing.InOutSine}
            NumberAnimation {to:-18;duration:14000;easing.type:Easing.InOutSine}
        }
    }
    RowLayout {
        anchors.fill:parent;anchors.margins:18;spacing:18
        Surface {
            Layout.preferredWidth:176;Layout.fillHeight:true
            glassOpacity:win.light?.42:.24
            shadowStrength:0;border.width:0
            radius:16
            ColumnLayout {
                anchors.fill:parent;anchors.margins:14;spacing:10
                Label {text:"LIQUID";color:win.accent;font.pixelSize:10;font.letterSpacing:1.7;font.weight:Font.DemiBold}
                Label {text:"Calendar";color:win.ink;font.pixelSize:24;font.weight:Font.DemiBold}
                Label {text:"BETA · "+planner.version;color:win.muted;font.pixelSize:10}
                Label {text:"Time for your plans.";color:win.muted;font.pixelSize:11;Layout.bottomMargin:20}
                Repeater {
                    model:[{id:"today",label:"Today"},{id:"week",label:"Week"},{id:"month",label:"Calendar"},{id:"agenda",label:"Agenda"},{id:"tasks",label:"Tasks"},{id:"search",label:"Search"}]
                    delegate:Action {required property var modelData;Layout.fillWidth:true;navigation:true;text:modelData.label;primary:planner.view===modelData.id;onClicked:planner.setView(modelData.id)}
                }
                Item {Layout.fillHeight:true}
                Label {Layout.fillWidth:true;text:planner.remindersEnabled?"● Reminders enabled":"Reminders paused";color:win.muted;font.pixelSize:10;wrapMode:Text.Wrap}
                Label {Layout.fillWidth:true;text:"Local to this computer";color:win.muted;font.pixelSize:10;wrapMode:Text.Wrap}
                Action {Layout.fillWidth:true;navigation:true;text:"Settings";primary:planner.view==="settings";onClicked:planner.setView("settings")}
            }
        }
        ColumnLayout {
            Layout.fillWidth:true;Layout.fillHeight:true;Layout.minimumWidth:0;spacing:12
            RowLayout {
                Layout.fillWidth:true
                ColumnLayout {
                    Layout.fillWidth:true;Layout.minimumWidth:0;spacing:4
                    Label {text:planner.view==="today"?"YOUR OVERVIEW":planner.view==="week"?"MAKE ROOM FOR YOUR PLANS":"YOUR CALENDAR";color:win.accent;font.pixelSize:10;font.letterSpacing:1.5}
                    Label {Layout.fillWidth:true;text:planner.view==="today"?planner.dayTitle:planner.view==="agenda"?"Coming up":planner.view==="search"?"Find anything":planner.view==="tasks"?"Your tasks":planner.view==="settings"?"Make it yours":planner.title;color:win.ink;font.pixelSize:28;font.weight:Font.DemiBold;elide:Text.ElideRight}
                }
                Action {visible:["today","week","month","agenda"].indexOf(planner.view)>=0;text:"Date";onClicked:{jumpDate.text=planner.selected;datePopup.open();}}
                Action {visible:planner.view!=="settings";text:"Today";onClicked:planner.today()}
                Action {visible:planner.view!=="settings";text:"+ Task";primary:planner.view==="tasks";onClicked:editorSurface.openNewTask(win.dateValue(planner.selected))}
                Action {visible:planner.view!=="settings";text:"+ Event";primary:planner.view!=="tasks";onClicked:win.newEvent()}
            }
            RowLayout {
                visible:["today","week"].indexOf(planner.view)>=0
                Action {text:"‹";Accessible.name:"Previous period";onClicked:planner.navigate(-1)}
                Action {text:"›";Accessible.name:"Next period";onClicked:planner.navigate(1)}
                Label {Layout.fillWidth:true;text:planner.view==="week"?"Drag to reschedule · 15-minute steps · series: this occurrence only":"Your day · tasks in a separate overview";color:win.muted;font.pixelSize:11;wrapMode:Text.Wrap}
                Label {visible:planner.view==="today"&&planner.conflictCount>0;text:planner.conflictCount+" entries overlap";color:win.danger;font.pixelSize:11}
            }
            Surface {
                visible:!planner.widgetCompatible
                Layout.fillWidth:true;implicitHeight:76
                RowLayout {
                    anchors.fill:parent;anchors.margins:12
                    Label {Layout.fillWidth:true;text:"Update the desktop calendar once so the app and widget can share data safely. This briefly reloads the desktop and panels. The app is read-only until connected.";color:win.muted;font.pixelSize:12;wrapMode:Text.Wrap}
                    Action {text:"Connect";primary:true;onClicked:planner.refreshWidget()}
                }
            }
            Surface {
                visible:planner.error!==""
                Layout.fillWidth:true;implicitHeight:Math.max(44,errorLabel.implicitHeight+20)
                RowLayout {anchors.fill:parent;anchors.margins:10;Label {id:errorLabel;Layout.fillWidth:true;text:planner.error;textFormat:Text.PlainText;color:win.danger;wrapMode:Text.Wrap;font.pixelSize:12} Action {text:"×";onClicked:planner.clearError()}}
            }
            Item {
                id:workspace
                Layout.fillWidth:true;Layout.fillHeight:true;Layout.minimumHeight:200
                // TODAY: real dates and tasks, with an actionable gap finder.
                GridLayout {
                    anchors.fill:parent;visible:planner.view==="today";columns:2;rowSpacing:12;columnSpacing:12
                    Surface {
                        Layout.fillWidth:true;Layout.fillHeight:true;Layout.preferredWidth:600;Layout.minimumHeight:200;Layout.preferredHeight:500
                        ColumnLayout {
                            anchors.fill:parent;anchors.margins:16;spacing:12
                            RowLayout {Layout.fillWidth:true;Label {Layout.fillWidth:true;text:"Your day";font.pixelSize:18;font.weight:Font.DemiBold;color:win.ink} Label {text:planner.dayItems.length+(planner.dayItems.length===1?" entry":" entries");color:win.muted;font.pixelSize:11}}
                            Rectangle {
                                visible:win.nextAppointment!==null
                                Layout.fillWidth:true;implicitHeight:74;radius:12
                                color:win.light?"#eeeafa":"#29263d"
                                RowLayout {
                                    anchors.fill:parent;anchors.margins:12;spacing:12
                                    Label {text:win.nextAppointment?win.nextAppointment.time:"";color:win.accent;font.pixelSize:23;font.weight:Font.DemiBold}
                                    ColumnLayout {Layout.fillWidth:true;spacing:4
                                        Label {text:planner.selected===Qt.formatDateTime(win.clockNow,"yyyy-MM-dd")?"UP NEXT":"FIRST TIME BLOCK";color:win.muted;font.pixelSize:10;font.letterSpacing:.8}
                                        Label {Layout.fillWidth:true;text:win.nextAppointment?win.nextAppointment.title:"";textFormat:Text.PlainText;color:win.ink;font.pixelSize:14;font.weight:Font.DemiBold;elide:Text.ElideRight}
                                    }
                                    Action {text:"Open";onClicked:planner.edit(win.nextAppointment.id,win.nextAppointment.occurrenceDate,true)}
                                }
                            }
                            ListView {id:dayList;Layout.fillWidth:true;Layout.fillHeight:true;clip:true;spacing:8;model:planner.dayItems;delegate:Entry {required property var modelData;record:modelData;width:dayList.width} ScrollBar.vertical:ScrollBar {} Label {anchors.centerIn:parent;width:parent.width-20;text:"Nothing planned yet.\nMake room for your next steps.";visible:dayList.count===0;color:win.muted;horizontalAlignment:Text.AlignHCenter;wrapMode:Text.Wrap;lineHeight:1.5}}
                        }
                    }
                    Surface {
                        Layout.fillWidth:true;Layout.fillHeight:false;Layout.alignment:Qt.AlignTop;Layout.preferredWidth:320;Layout.minimumWidth:300;Layout.maximumWidth:360;Layout.minimumHeight:240;Layout.preferredHeight:Math.max(260,Math.min(500,160+planner.tasks.length*104))
                        ColumnLayout {
                            anchors.fill:parent;anchors.margins:16;spacing:10
                            Label {text:"Open tasks";font.pixelSize:18;font.weight:Font.DemiBold;color:win.ink}
                            Label {Layout.fillWidth:true;text:"Collect without pressure. Schedule when needed.";color:win.muted;font.pixelSize:11;wrapMode:Text.Wrap}
                            Action {Layout.fillWidth:true;text:"View all tasks ("+planner.tasks.length+")";onClicked:planner.setView("tasks")}
                            ListView {
                                id:quickTasks;Layout.fillWidth:true;Layout.fillHeight:true;clip:true;spacing:8;model:planner.tasks.slice(0,3)
                                delegate:Item {
                                    required property var modelData;width:quickTasks.width;implicitHeight:104
                                    Rectangle {x:0;y:8;width:3;height:26;radius:1;color:modelData.color}
                                    ColumnLayout {anchors.fill:parent;anchors.leftMargin:12;spacing:4
                                        Label {Layout.fillWidth:true;text:modelData.title;textFormat:Text.PlainText;color:win.ink;font.pixelSize:13;font.weight:Font.DemiBold;wrapMode:Text.Wrap;maximumLineCount:2;elide:Text.ElideRight}
                                        Label {Layout.fillWidth:true;text:modelData.unscheduled?"Undated · "+modelData.minutes+" min":modelData.date+" · "+modelData.time;color:win.muted;font.pixelSize:11;elide:Text.ElideRight}
                                        RowLayout {Layout.fillWidth:true
                                            Action {text:"✓";Accessible.name:"Complete task";onClicked:planner.toggleTask(modelData.id,modelData.occurrenceDate,modelData.fingerprint)}
                                            Item {Layout.fillWidth:true}
                                            Action {text:"Schedule";onClicked:win.planTask(modelData)}
                                            Action {text:"↗";Accessible.name:"Edit task";onClicked:planner.edit(modelData.id,modelData.occurrenceDate,true)}
                                        }
                                    }
                                }
                                ScrollBar.vertical:ScrollBar {}
                                Label {anchors.centerIn:parent;visible:quickTasks.count===0;text:"All caught up.";color:win.muted;font.pixelSize:13}
                            }
                        }
                    }
                }
                Surface {
                    anchors.fill:parent;visible:planner.view==="agenda"
                    ColumnLayout {anchors.fill:parent;anchors.margins:16;spacing:12
                        RowLayout {Layout.fillWidth:true
                            Label {Layout.fillWidth:true;text:"From "+win.dateValue(planner.selected).toLocaleDateString(Qt.locale("en_GB"),"dd MMMM yyyy");color:win.muted;font.pixelSize:12}
                            Repeater {model:[7,14,30];delegate:Action {required property int modelData;text:modelData+" days";primary:planner.agendaDays===modelData;onClicked:planner.setAgendaDays(modelData)}}
                        }
                        Label {Layout.fillWidth:true;text:"Events and scheduled tasks · completed tasks hidden";color:win.muted;font.pixelSize:11;wrapMode:Text.Wrap}
                        ListView {id:agendaList;Layout.fillWidth:true;Layout.fillHeight:true;clip:true;spacing:4;model:planner.agendaItems
                            section.property:"date";section.criteria:ViewSection.FullString
                            section.delegate:Label {required property string section;width:agendaList.width;height:36;verticalAlignment:Text.AlignVCenter;text:win.dateValue(section).toLocaleDateString(Qt.locale("en_GB"),"dddd, dd MMMM yyyy");color:win.accent;font.pixelSize:13;font.weight:Font.DemiBold}
                            delegate:Entry {required property var modelData;width:agendaList.width;record:modelData}
                            ScrollBar.vertical:ScrollBar {}
                            Label {anchors.centerIn:parent;width:parent.width-24;visible:agendaList.count===0;text:"No entries in this period.\nChoose another start date or create an event.";wrapMode:Text.Wrap;horizontalAlignment:Text.AlignHCenter;color:win.muted}
                        }
                    }
                }
                // WEEK: vertically and horizontally scrollable 24-hour time grid.
                Surface {
                    anchors.fill:parent;visible:planner.view==="week"
                    ColumnLayout {
                        anchors.fill:parent;anchors.margins:10;spacing:6
                        RowLayout {
                            Layout.fillWidth:true;Layout.leftMargin:48;spacing:0
                            Repeater {model:planner.weekDays;delegate:Item {required property var modelData;Layout.fillWidth:true;implicitHeight:46;Column {anchors.centerIn:parent;spacing:3;Label {anchors.horizontalCenter:parent.horizontalCenter;text:modelData.name;font.pixelSize:10;color:win.muted} Label {anchors.horizontalCenter:parent.horizontalCenter;text:modelData.number;color:modelData.today?win.accent:win.ink;font.pixelSize:20;font.bold:modelData.today}}}}
                        }
                        ListView {
                            id:allDayList;visible:count>0;Layout.fillWidth:true;Layout.preferredHeight:34;orientation:ListView.Horizontal;spacing:6;clip:true
                            model:win.weekData.filter(function(v){return v.allDay;})
                            delegate:Action {required property var modelData;text:modelData.date.slice(5)+" · "+modelData.title;onClicked:planner.edit(modelData.id,modelData.occurrenceDate,true)}
                            ScrollBar.horizontal:ScrollBar {}
                        }
                        Flickable {
                            id:timeline
                            objectName:"timeline"
                            Layout.fillWidth:true;Layout.fillHeight:true;clip:true
                            readonly property real hourHeight:66
                            readonly property real gutter:48
                            readonly property real columnWidth:(width-gutter)/7
                            contentWidth:width;contentHeight:24*hourHeight
                            Component.onCompleted:contentY=7.5*hourHeight
                            boundsBehavior:Flickable.StopAtBounds
                            ScrollBar.vertical:ScrollBar {}
                            Item {
                                id:timeContent
                                width:timeline.contentWidth;height:timeline.contentHeight
                                Repeater {model:24;delegate:Item {required property int index;x:0;y:index*timeline.hourHeight;width:timeContent.width;height:timeline.hourHeight;Label {x:1;y:2;text:(index<10?"0":"")+index+":00";color:win.muted;font.pixelSize:10} Rectangle {x:timeline.gutter;y:0;width:parent.width-timeline.gutter;height:1;color:win.line} Rectangle {x:timeline.gutter;y:timeline.hourHeight/2;width:parent.width-timeline.gutter;height:1;color:win.light?"#0b0e254e":"#0affffff"}}}
                                Repeater {
                                    model:planner.weekDays
                                    delegate:DropArea {
                                        required property var modelData
                                        required property int index
                                        x:timeline.gutter+index*timeline.columnWidth;y:0;width:timeline.columnWidth;height:timeContent.height
                                        keys:["liquid-calendar-event"]
                                        Rectangle {anchors.left:parent.left;width:1;height:parent.height;color:win.line}
                                        Rectangle {anchors.fill:parent;color:parent.containsDrag?"#30b5a6ff":modelData.today?(win.light?"#0c7361ba":"#098a9bff"):"transparent"}
                                        onDropped:function(drop){var source=drop.source;var minute=Math.max(0,Math.min(1425,Math.round((drop.y-8)/timeline.hourHeight*4)*15));planner.move(source.record.id,source.record.occurrenceDate,modelData.date,minute,source.record.fingerprint);drop.acceptProposedAction();}
                                    }
                                }
                                Repeater {
                                    model:win.weekData.filter(function(v){return !v.allDay;})
                                    delegate:Rectangle {
                                        id:eventBlock
                                        required property var modelData
                                        property var record:modelData
                                        readonly property real homeX:timeline.gutter+record.dayIndex*timeline.columnWidth+record.lane*timeline.columnWidth/record.lanes+3
                                        readonly property real homeY:record.start/60*timeline.hourHeight+2
                                        x:homeX;y:homeY;width:Math.max(24,timeline.columnWidth/record.lanes-6);height:Math.max(20,record.segmentMinutes/60*timeline.hourHeight-4)
                                        readonly property color eventTint:record.conflict?win.danger:record.color
                                        radius:7;border.width:dragMouse.drag.active?1:0;border.color:eventTint;clip:true
                                        color:Qt.rgba(eventTint.r,eventTint.g,eventTint.b,win.light?.15:.16)
                                        Rectangle {anchors.left:parent.left;anchors.top:parent.top;anchors.bottom:parent.bottom;width:3;color:eventBlock.eventTint}
                                        z:dragMouse.drag.active?20:3
                                        Drag.active:dragMouse.drag.active;Drag.keys:["liquid-calendar-event"];Drag.source:eventBlock;Drag.hotSpot.x:width/2;Drag.hotSpot.y:8
                                        Column {
                                            anchors.fill:parent;anchors.margins:6;spacing:3
                                            Label {width:parent.width;text:(eventBlock.record.carry?"↳ ":"")+eventBlock.record.time;color:win.ink;font.pixelSize:10;elide:Text.ElideRight}
                                            Label {visible:eventBlock.height>38;width:parent.width;text:eventBlock.record.title;textFormat:Text.PlainText;color:win.ink;font.pixelSize:11;font.bold:true;wrapMode:Text.Wrap;maximumLineCount:3;elide:Text.ElideRight}
                                            Label {visible:eventBlock.height>95&&eventBlock.record.conflict;width:parent.width;text:"Overlap";color:win.danger;font.pixelSize:9;elide:Text.ElideRight}
                                        }
                                        MouseArea {
                                            id:dragMouse;anchors.fill:parent;hoverEnabled:true;drag.smoothed:false;drag.target:eventBlock.record.carry?null:eventBlock;drag.minimumX:timeline.gutter;drag.maximumX:timeContent.width-eventBlock.width;drag.minimumY:0;drag.maximumY:timeContent.height-eventBlock.height
                                            onReleased:{eventBlock.Drag.drop();eventBlock.x=Qt.binding(function(){return eventBlock.homeX;});eventBlock.y=Qt.binding(function(){return eventBlock.homeY;});}
                                            onDoubleClicked:planner.edit(eventBlock.record.id,eventBlock.record.occurrenceDate,true)
                                        }
                                        ToolTip.visible:dragMouse.containsMouse&&!dragMouse.drag.active;ToolTip.delay:400;ToolTip.text:record.time+" · "+record.title+(record.conflict?"\nOverlaps another event":"")+"\nDouble-click to edit"
                                    }
                                }
                            }
                        }
                    }
                }
                Surface {
                    anchors.fill:parent;visible:planner.view==="tasks"||planner.view==="search"
                    ColumnLayout {
                        anchors.fill:parent;anchors.margins:16;spacing:12
                        RowLayout {
                            Layout.fillWidth:true
                            Field {id:globalSearch;Layout.fillWidth:true;placeholderText:"Title, project, checklist, notes or date …";maximumLength:200;text:planner.query;onTextEdited:planner.setQuery(text);Accessible.name:"Global search"}
                                                        Action {text:"All";primary:planner.kind==="all"||planner.kind==="tasks";onClicked:planner.setFilter(planner.view==="tasks"?"tasks":"all",planner.category)}
                            Action {text:"Open";primary:planner.kind==="open";onClicked:planner.setFilter("open",planner.category)}
                            Action {text:"Completed";primary:planner.kind==="done";onClicked:planner.setFilter("done",planner.category)}
                        }
                        RowLayout {
                            Layout.fillWidth:true;spacing:8
                            Action {visible:planner.view==="search";text:"Events only";primary:planner.kind==="events";onClicked:planner.setFilter("events",planner.category)}
                            Action {visible:planner.view==="search";text:"Tasks only";primary:planner.kind==="tasks";onClicked:planner.setFilter("tasks",planner.category)}
                            Action {text:(["All categories","Personal","Work","Important","Leisure"])[planner.category+1]+" ▾";onClicked:categoryMenu.open()
                                Menu {id:categoryMenu
                                    Repeater {model:["All categories","Personal","Work","Important","Leisure"];delegate:MenuItem {required property int index;required property string modelData;text:modelData;onTriggered:planner.setFilter(planner.kind,index-1)}}
                                }
                            }
                            Action {visible:planner.view==="tasks";text:"Sort ▾";onClicked:sortMenu.open()
                                Menu {id:sortMenu
                                    MenuItem {text:"Default";checkable:true;checked:planner.taskOrder==="default";onTriggered:planner.setTaskOrder("default")}
                                    MenuItem {text:"Priority: high first";checkable:true;checked:planner.taskOrder==="priority";onTriggered:planner.setTaskOrder("priority")}
                                    MenuItem {text:"Project";checkable:true;checked:planner.taskOrder==="project";onTriggered:planner.setTaskOrder("project")}
                                    MenuItem {text:"Title A–Z";checkable:true;checked:planner.taskOrder==="title";onTriggered:planner.setTaskOrder("title")}
                                    MenuItem {text:"Scheduled first";checkable:true;checked:planner.taskOrder==="planned";onTriggered:planner.setTaskOrder("planned")}
                                    MenuItem {text:"Shortest duration first";checkable:true;checked:planner.taskOrder==="duration";onTriggered:planner.setTaskOrder("duration")}
                                }
                            }
                            Item {Layout.fillWidth:true}
                            Action {visible:planner.projectFilter!=="*"||planner.priorityFilter>=0||planner.category>=0||planner.query.length>0||planner.planningFilter!=="all"||planner.taskOrder!=="default"||["all","tasks"].indexOf(planner.kind)<0;text:"Reset";onClicked:{planner.setTaskFilters("*",-1);planner.setTaskOrder("default");planner.setPlanningFilter("all");planner.setQuery("");planner.setFilter(planner.view==="tasks"?"tasks":"all",-1);}}
                        }
                        RowLayout {
                            visible:planner.view==="tasks";Layout.fillWidth:true;spacing:8
                            Action {Layout.maximumWidth:240;text:(planner.projectFilter==="*"?"All projects":planner.projectFilter||"No project")+" ▾";onClicked:taskProjectMenu.open()
                                Menu {id:taskProjectMenu
                                    MenuItem {text:"All projects";onTriggered:planner.setTaskFilters("*",planner.priorityFilter)}
                                    MenuItem {text:"No project";onTriggered:planner.setTaskFilters("",planner.priorityFilter)}
                                    Repeater {model:planner.projects;delegate:MenuItem {required property var modelData;text:modelData.name+" · "+modelData.done+"/"+modelData.total;onTriggered:planner.setTaskFilters(modelData.name,planner.priorityFilter)}}
                                }
                            }
                            Action {text:(["Any priority","No priority","Low","Medium","High"])[planner.priorityFilter+1]+" ▾";onClicked:taskPriorityMenu.open()
                                Menu {id:taskPriorityMenu
                                    Repeater {model:["Any priority","No priority","Low","Medium","High"];delegate:MenuItem {required property int index;required property string modelData;text:modelData;onTriggered:planner.setTaskFilters(planner.projectFilter,index-1)}}
                                }
                            }
                            Action {visible:planner.projectFilter!=="*"&&planner.projectFilter!=="";text:"Edit project";onClicked:{renameProjectField.text=planner.projectFilter;projectPopup.open();}}
                            Item {Layout.fillWidth:true}
                            Label {text:planner.results.length+" tasks";color:win.muted;font.pixelSize:12}
                        }
                        RowLayout {visible:planner.view==="tasks";Layout.fillWidth:true
                            Action {text:"Any schedule";primary:planner.planningFilter==="all";onClicked:planner.setPlanningFilter("all")}
                            Action {text:"Undated";primary:planner.planningFilter==="undated";onClicked:planner.setPlanningFilter("undated")}
                            Action {text:"Scheduled";primary:planner.planningFilter==="planned";onClicked:planner.setPlanningFilter("planned")}
                        }
                        RowLayout {
                            visible:planner.dateHints.length>0
                            Layout.fillWidth:true
                            Repeater {model:planner.dateHints;delegate:Action {required property var modelData;text:modelData.label+" · "+modelData.date;onClicked:{planner.selectDate(modelData.date);planner.setView("today");}}}
                            Item {Layout.fillWidth:true}
                        }
                        Label {text:planner.view==="tasks"?"Undated tasks stay here. Scheduled tasks also appear in the calendar.":"Search all months and years · includes projects and checklist steps";Layout.fillWidth:true;wrapMode:Text.Wrap;color:win.muted;font.pixelSize:11}
                        ListView {id:resultList;Layout.fillWidth:true;Layout.fillHeight:true;clip:true;spacing:8;model:planner.view==="tasks"?planner.results.filter(function(e){return e.task;}):planner.results;delegate:Entry {required property var modelData;width:resultList.width;record:modelData;showDate:true} ScrollBar.vertical:ScrollBar {} Label {anchors.centerIn:parent;text:"No matching entries.";color:win.muted;visible:resultList.count===0}}
                    }
                }
                Surface {
                    anchors.fill:parent;visible:planner.view==="settings"
                    ScrollView {
                        id:settingsScroll;anchors.fill:parent;anchors.margins:24;contentWidth:availableWidth;clip:true
                        ColumnLayout {
                            width:settingsScroll.availableWidth;spacing:18
                            Label {text:"Your calendar, your data";color:win.ink;font.pixelSize:22;font.bold:true}
                            Label {Layout.fillWidth:true;text:"The app and widget share a local database. The app backs up your data before changes and detects conflicting edits to the same event.";color:win.muted;font.pixelSize:13;wrapMode:Text.Wrap}
                            RowLayout {Action {text:planner.remindersEnabled?"✓ Reminders enabled":"Enable reminders";primary:planner.remindersEnabled;onClicked:planner.setReminders(!planner.remindersEnabled)} Label {Layout.fillWidth:true;text:"Reminders run while the app is open or running in the system tray.";color:win.muted;font.pixelSize:12;wrapMode:Text.Wrap}}
                            Label {Layout.fillWidth:true;text:win.trayAvailable?"When reminders are enabled, closing the window keeps the app in the system tray. Use the tray menu or Ctrl+Q to quit.":"No system tray available: keep the app open for reminders.";color:win.muted;wrapMode:Text.Wrap;font.pixelSize:12}
                            Action {text:planner.autoStart?"✓ Start at login":"Start at login";primary:planner.autoStart;onClicked:planner.setAutoStart(!planner.autoStart)}
                            Label {text:"Appearance";color:win.ink;font.pixelSize:16;font.bold:true}
                            RowLayout {Action {text:"Dark glass";primary:planner.theme==="dark";onClicked:planner.setTheme("dark")} Action {text:"Light glass";primary:planner.theme==="light";onClicked:planner.setTheme("light")} Action {text:"System";primary:planner.theme==="auto";onClicked:planner.setTheme("auto")}}
                            Action {text:planner.animationsEnabled?"✓ Gentle motion":"Enable motion";primary:planner.animationsEnabled;onClicked:planner.setAnimations(!planner.animationsEnabled)}
                            Label {text:"Backup and sharing";color:win.ink;font.pixelSize:16;font.bold:true}
                            RowLayout {Action {text:"Back up JSON";onClicked:{win.exportKind="json";saveDialog.nameFilters=["JSON backup (*.json)"];saveDialog.defaultSuffix="json";saveDialog.open();}} Action {text:"Import JSON";onClicked:importDialog.open()} Action {text:"Export ICS";onClicked:{win.exportKind="ics";saveDialog.nameFilters=["Calendar (*.ics)"];saveDialog.defaultSuffix="ics";saveDialog.open();}}}
                            Label {Layout.fillWidth:true;text:"ICS exports events for other calendar apps. JSON also preserves tasks, categories, reminders and repeat exceptions. Import adds new IDs without overwriting existing entries.";color:win.muted;wrapMode:Text.Wrap;font.pixelSize:12}
                            Label {text:"Keyboard";color:win.ink;font.pixelSize:16;font.bold:true}
                            Label {text:"Ctrl+N · New event\nCtrl+F · Search\nCtrl+Z · Undo last change\nCtrl+Q · Quit app and reminders";color:win.muted;font.pixelSize:13;lineHeight:1.7}
                            Label {Layout.fillWidth:true;text:"Database: "+planner.databasePath;textFormat:Text.PlainText;color:win.muted;font.pixelSize:10;wrapMode:Text.WrapAnywhere}
                            Label {Layout.fillWidth:true;text:"Account sync is not configured. This calendar stores your data locally.";color:win.muted;font.pixelSize:12;wrapMode:Text.Wrap}
                        }
                    }
                }
                CalendarEditor {
                    id:editorSurface
                    anchors.fill:parent
                    persistence:planner
                    light:win.light
                    motionEnabled:win.motionEnabled
                    editorOnly:planner.view!=="month"
                    z:20
                }
            }
            RowLayout {
                Layout.fillWidth:true
                Label {Layout.fillWidth:true;Layout.minimumWidth:0;text:planner.notice||"Saved locally · app and widget connected";textFormat:Text.PlainText;color:win.muted;font.pixelSize:11;elide:Text.ElideRight}
                Action {visible:planner.canUndo;text:"Undo";onClicked:planner.undo()}
            }
        }
    }
    Popup {
        id:slotPopup;anchors.centerIn:Overlay.overlay;width:Math.min(win.width-60,480);modal:true;focus:true
        background:Surface {}
        contentItem:ColumnLayout {
            spacing:14
            Label {Layout.fillWidth:true;text:win.planningTask?win.planningTask.title:"Free time";textFormat:Text.PlainText;color:win.ink;font.pixelSize:20;font.bold:true;wrapMode:Text.Wrap}
            Label {Layout.fillWidth:true;text:win.slotDate+" · "+(win.planningTask?win.planningTask.minutes:0)+" minutes";color:win.muted;wrapMode:Text.Wrap}
            RowLayout {Layout.fillWidth:true
                Action {text:"‹";Accessible.name:"Previous planning day";onClicked:win.shiftSlots(-1)}
                Field {id:slotDateField;Layout.fillWidth:true;placeholderText:"YYYY-MM-DD";maximumLength:10;Accessible.name:"Date for available time slots";onAccepted:{win.slotDate=text;win.refreshSlots();}}
                Action {text:"›";Accessible.name:"Next planning day";onClicked:win.shiftSlots(1)}
                Action {text:"Find";onClicked:{win.slotDate=slotDateField.text;win.refreshSlots();}}
            }
            Label {Layout.fillWidth:true;visible:win.slotError!=="";text:win.slotError;color:win.danger;wrapMode:Text.Wrap}
            Repeater {model:win.suggestedSlots;delegate:Action {required property var modelData;Layout.fillWidth:true;text:modelData.time+" · "+modelData.minutes+" minutes to schedule";onClicked:{if(planner.scheduleTask(win.planningTask.id,win.planningTask.occurrenceDate,modelData.date,modelData.minute,win.planningTask.fingerprint))slotPopup.close();else {win.slotError=planner.error;win.suggestedSlots=[];}}}}
            Label {visible:win.suggestedSlots.length===0;Layout.fillWidth:true;text:"No suitable free time between 09:00 and 18:00 on this day. Choose another day or adjust the duration.";color:win.muted;wrapMode:Text.Wrap}
            Action {Layout.fillWidth:true;text:"Cancel";onClicked:slotPopup.close()}
        }
    }
    Popup {
        id:datePopup;anchors.centerIn:Overlay.overlay;width:360;modal:true;focus:true
        property string validation:""
        onOpened:{validation="";jumpDate.forceActiveFocus();jumpDate.selectAll();}
        function go(){var result=planner.resolveDate(jumpDate.text);if(result.error){validation=result.error;return;}planner.selectDate(result.date);close();}
        background:Surface {glassOpacity:1}
        contentItem:ColumnLayout {spacing:12
            Label {text:"Jump to date";color:win.ink;font.pixelSize:20;font.weight:Font.DemiBold}
            Field {id:jumpDate;Layout.fillWidth:true;maximumLength:40;placeholderText:"2026-11-15 or tomorrow";Accessible.name:"Target date";onAccepted:datePopup.go()}
            Label {Layout.fillWidth:true;visible:datePopup.validation!=="";text:datePopup.validation;color:win.danger;wrapMode:Text.Wrap}
            RowLayout {Action {text:"Cancel";onClicked:datePopup.close()} Item {Layout.fillWidth:true} Action {text:"Open";primary:true;onClicked:datePopup.go()}}
        }
    }
    FileDialog {id:saveDialog;fileMode:FileDialog.SaveFile;onAccepted:planner.exportFile(selectedFile.toString(),win.exportKind)}
    FileDialog {id:importDialog;fileMode:FileDialog.OpenFile;nameFilters:["JSON backup (*.json)"];onAccepted:planner.importFile(selectedFile.toString())}
    Connections {
        target:planner
        function onEditRequested(event){editorSurface.openEvent(event);}
        function onChanged(){if(!editorSurface.modalOpen){editorSurface.events=planner.events;if(Qt.formatDateTime(editorSurface.selected,"yyyy-MM-dd")!==planner.selected)editorSurface.select(win.dateValue(planner.selected));}}
    }
}
