import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "Theme.js" as Theme

GlassPopup {
    id:commandSheet
    objectName:"commandPalette"
    property bool light:false
    property color accent:"#7ceafa"
    property var commands:[]
    property Item previousFocus:null
    property bool executing:false
    property string pendingCommand:""
    readonly property var colors:Theme.palette(light,accent)
    readonly property var matches: {
        var words=query.text.toLowerCase().trim().split(/\s+/);
        return commands.filter(function(command) {
            var text=(command.title+" "+(command.keywords||"")).toLowerCase();
            return command.available!==false&&words.every(function(word){return text.indexOf(word)>=0;});
        });
    }
    signal chosen(string command)
    parent:Overlay.overlay
    anchors.centerIn:parent
    width:Math.min(parent.width-48,580)
    padding:16;modal:true;focus:true
    closePolicy:Popup.CloseOnEscape|Popup.CloseOnPressOutside
    background:LiquidSurface {light:commandSheet.light;tint:commandSheet.accent;glassOpacity:1;radius:20;motionEnabled:commandSheet.motionEnabled}
    function show(focusItem) {previousFocus=focusItem;executing=false;query.text="";results.currentIndex=0;open();}
    function step(delta) {
        if(!matches.length)return;
        results.currentIndex=(results.currentIndex+delta+matches.length)%matches.length;
        results.positionViewAtIndex(results.currentIndex,ListView.Contain);
    }
    function run(index) {
        if(index<0||index>=matches.length)return;
        pendingCommand=matches[index].id;executing=true;close();
    }
    onOpened:{query.forceActiveFocus();results.positionViewAtBeginning();}
    onClosed: {
        if(executing)chosen(pendingCommand);
        else if(previousFocus)previousFocus.forceActiveFocus();
    }
    onMatchesChanged:{results.currentIndex=matches.length?0:-1;Qt.callLater(function(){results.positionViewAtBeginning();});}
    contentItem:ColumnLayout {
        spacing:12
        RowLayout {
            Layout.fillWidth:true
            Label {Layout.fillWidth:true;text:"Commands";color:commandSheet.colors.ink;font.pixelSize:20;font.weight:Font.DemiBold}
            Button {
                id:closeButton;text:"Esc";Accessible.name:"Close commands";implicitHeight:38;implicitWidth:44
                contentItem:Text {text:closeButton.text;color:commandSheet.colors.muted;font.pixelSize:12;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter}
                background:Rectangle {radius:10;color:closeButton.hovered?commandSheet.colors.field:"transparent";border.color:closeButton.activeFocus?commandSheet.accent:commandSheet.colors.line}
                onClicked:commandSheet.close()
            }
        }
        GlassTextField {
            id:query;objectName:"commandQuery";Layout.fillWidth:true;implicitHeight:44
            inkColor:commandSheet.colors.ink;mutedColor:commandSheet.colors.muted;accentColor:commandSheet.accent;fieldColor:commandSheet.colors.field;lineColor:commandSheet.colors.line
            placeholderText:"Search actions, views or settings…";Accessible.name:"Search commands"
            Keys.onDownPressed:commandSheet.step(1)
            Keys.onUpPressed:commandSheet.step(-1)
            onAccepted:commandSheet.run(results.currentIndex)
        }
        ListView {
            id:results;objectName:"commandResults";Layout.fillWidth:true
            Layout.preferredHeight:Math.min(336,Math.max(48,contentHeight))
            clip:true;model:commandSheet.matches;spacing:2;boundsBehavior:Flickable.StopAtBounds
            ScrollBar.vertical:ScrollBar {}
            delegate:ItemDelegate {
                id:row
                required property var modelData
                required property int index
                width:results.width;height:46
                Accessible.name:modelData.title+(modelData.shortcut?" · "+modelData.shortcut:"")
                highlighted:results.currentIndex===index
                onHoveredChanged:if(hovered)results.currentIndex=index
                onClicked:commandSheet.run(index)
                contentItem:RowLayout {
                    Label {Layout.fillWidth:true;text:row.modelData.title;textFormat:Text.PlainText;color:commandSheet.colors.ink;elide:Text.ElideRight;font.pixelSize:14}
                    Label {text:row.modelData.shortcut||"";color:commandSheet.colors.muted;font.pixelSize:11}
                }
                background:Rectangle {radius:10;color:row.highlighted?Qt.rgba(commandSheet.accent.r,commandSheet.accent.g,commandSheet.accent.b,.16):"transparent";border.width:row.activeFocus?1:0;border.color:commandSheet.accent}
            }
            Label {anchors.centerIn:parent;visible:commandSheet.matches.length===0;text:"No matching commands";color:commandSheet.colors.muted}
        }
        Label {Layout.fillWidth:true;text:"↑ ↓ Choose    Enter Run    Esc Close";color:commandSheet.colors.muted;font.pixelSize:11}
    }
}
