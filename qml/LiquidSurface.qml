import QtQuick

Rectangle {
    id: glass
    property bool light:false
    property bool motionEnabled:true
    property bool initialized:false
    property real glassOpacity:light?.86:.82
    property real shadowStrength:light?.08:.12
    Component.onCompleted:initialized=true
    radius:18
    color:light?Qt.rgba(1,1,1,glassOpacity):Qt.rgba(.095,.105,.135,glassOpacity)
    border.width:1
    border.color:light?"#bce1e5ed":"#16ffffff"
    Behavior on color {enabled:glass.motionEnabled&&glass.initialized;ColorAnimation {duration:140}}
    Rectangle {
        z:-1;x:-1;y:3;width:glass.width+2;height:glass.height+2;radius:glass.radius+1
        color:Qt.rgba(.02,.025,.04,glass.shadowStrength/3)
        visible:glass.shadowStrength>0
    }
}
