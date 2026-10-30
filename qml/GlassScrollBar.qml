import QtQuick
import QtQuick.Controls

ScrollBar {
    id:bar
    property bool light:false
    property color accent:light?"#087f9c":"#7ceafa"
    property bool motionEnabled:true
    readonly property bool dragging:pointer.pressed
    visible:policy===ScrollBar.AlwaysOn||(policy!==ScrollBar.AlwaysOff&&size<.9999)
    interactive:true
    hoverEnabled:true
    padding:3
    minimumSize:Math.min(1,44/Math.max(1,orientation===Qt.Horizontal?availableWidth:availableHeight))
    implicitWidth:orientation===Qt.Vertical?16:100
    implicitHeight:orientation===Qt.Horizontal?16:100
    Accessible.name:orientation===Qt.Horizontal?"Scroll calendar horizontally":"Scroll vertically"
    contentItem:Rectangle {
        implicitWidth:10;implicitHeight:10;radius:5
        color:bar.accent
        opacity:bar.dragging?1:bar.hovered?.85:.55
        Behavior on opacity {enabled:bar.motionEnabled;NumberAnimation {duration:120}}
    }
    background:Rectangle {radius:8;color:bar.light?"#14087f9c":"#127ceafa";visible:bar.size<1}
    MouseArea {
        id:pointer
        anchors.fill:parent
        acceptedButtons:Qt.LeftButton
        preventStealing:true
        property real grabOffset:0
        function coordinate(mouse){return bar.orientation===Qt.Horizontal?mouse.x-bar.leftPadding:mouse.y-bar.topPadding;}
        function moveTo(mouse){
            var length=bar.orientation===Qt.Horizontal?bar.availableWidth:bar.availableHeight;
            var travel=length*(1-bar.visualSize);
            if(travel<=0)return;
            bar.position=Math.max(0,Math.min(1,(coordinate(mouse)-grabOffset)/travel))*(1-bar.size);
        }
        onPressed:function(mouse){
            var length=bar.orientation===Qt.Horizontal?bar.availableWidth:bar.availableHeight;
            var start=bar.visualPosition*length;
            var thumb=bar.visualSize*length;
            var point=coordinate(mouse);
            grabOffset=point>=start&&point<=start+thumb?point-start:thumb/2;
            bar.forceActiveFocus();moveTo(mouse);
        }
        onPositionChanged:function(mouse){if(pressed)moveTo(mouse);}
    }
    Keys.onPressed:function(event){
        var step=bar.stepSize||.05;
        if(event.key===Qt.Key_Home)bar.position=0;
        else if(event.key===Qt.Key_End)bar.position=1-bar.size;
        else if(event.key===Qt.Key_PageDown)bar.position=Math.min(1-bar.size,bar.position+bar.size);
        else if(event.key===Qt.Key_PageUp)bar.position=Math.max(0,bar.position-bar.size);
        else if((bar.orientation===Qt.Horizontal&&event.key===Qt.Key_Right)||(bar.orientation===Qt.Vertical&&event.key===Qt.Key_Down))bar.position=Math.min(1-bar.size,bar.position+step);
        else if((bar.orientation===Qt.Horizontal&&event.key===Qt.Key_Left)||(bar.orientation===Qt.Vertical&&event.key===Qt.Key_Up))bar.position=Math.max(0,bar.position-step);
        else {event.accepted=false;return;}
        event.accepted=true;
    }
}
