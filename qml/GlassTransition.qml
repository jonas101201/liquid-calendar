import QtQuick

Transition {
    id:motion
    property bool entering:true
    property bool motionEnabled:true
    animations:entering?[opening]:[closing]
    property ParallelAnimation opening:ParallelAnimation {
        NumberAnimation {property:"opacity";from:0;to:1;duration:motion.motionEnabled?160:0;easing.type:Easing.OutCubic}
        NumberAnimation {property:"scale";from:.97;to:1;duration:motion.motionEnabled?200:0;easing.type:Easing.OutCubic}
    }
    property ParallelAnimation closing:ParallelAnimation {
        NumberAnimation {property:"opacity";to:0;duration:motion.motionEnabled?110:0;easing.type:Easing.OutCubic}
        NumberAnimation {property:"scale";to:.985;duration:motion.motionEnabled?110:0;easing.type:Easing.OutCubic}
    }
}
