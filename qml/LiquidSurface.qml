import QtQuick
import QtQuick.Shapes
import "Theme.js" as Theme

ContinuousSurface {
    id: glass
    property bool light:false
    property color tint:"#7ceafa"
    readonly property var colors:Theme.palette(light,tint)
    property bool motionEnabled:true
    property bool initialized:false
    property real highlight:0
    Behavior on highlight {enabled:glass.motionEnabled&&glass.initialized;NumberAnimation {duration:180;easing.type:Easing.OutCubic}}
    property real glassOpacity:light?.86:.82
    property real shadowStrength:light?.08:.12
    Component.onCompleted:initialized=true
    radius:18
    antialiasing:true
    color:Qt.rgba(colors.panel.r,colors.panel.g,colors.panel.b,glassOpacity)
    border.width:1
    border.color:light?"#b3ffffff":Qt.rgba(tint.r,tint.g,tint.b,.25)
    Behavior on color {enabled:glass.motionEnabled&&glass.initialized;ColorAnimation {duration:140}}
    ContinuousSurface {
        z:-1;x:-2;y:5;width:glass.width+4;height:glass.height+3;radius:glass.radius+2
        color:Qt.rgba(.01,.015,.035,glass.shadowStrength/3)
        visible:glass.shadowStrength>0
    }
    ContinuousShape {
        anchors.fill:parent;anchors.margins:1;radius:Math.max(0,glass.radius-1)
        opacity:glass.highlight
        fillGradient:LinearGradient {
            x1:0;y1:0;x2:0;y2:glass.height;
            GradientStop {position:0;color:glass.light?"#60ffffff":"#27ffffff"}
            GradientStop {position:.65;color:"transparent"}
        }
    }
    ContinuousShape {
        anchors.fill:parent;anchors.margins:1;radius:Math.max(0,glass.radius-1)
        visible:glass.color.a>.1
        fillGradient:LinearGradient {
            x1:0;y1:0;x2:0;y2:glass.height;
            GradientStop {position:0;color:glass.light?"#36ffffff":Qt.rgba(glass.tint.r,glass.tint.g,glass.tint.b,.065)}
            GradientStop {position:.28;color:glass.light?"#0affffff":Qt.rgba(glass.tint.r,glass.tint.g,glass.tint.b,.012)}
            GradientStop {position:.70;color:"transparent"}
            GradientStop {position:1;color:glass.light?"#12ffffff":Qt.rgba(glass.tint.r,glass.tint.g,glass.tint.b,.035)}
        }
    }
}
