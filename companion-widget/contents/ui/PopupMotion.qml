import QtQuick

QtObject {
    id:motion
    property var popup:null
    property bool motionEnabled:true
    property bool dismissing:false
    property real visualProgress:0
    property NumberAnimation tween:NumberAnimation {target:motion;property:"visualProgress";easing.type:Easing.OutCubic}
    function retarget(value) {
        tween.stop();
        if(!motionEnabled){visualProgress=value;return;}
        tween.to=value;tween.duration=dismissing?110:200;tween.start();
    }
    onMotionEnabledChanged:if(!motionEnabled&&popup) {
        if(tween)tween.stop();visualProgress=popup.visible&&!dismissing?1:0;
    }
    property Connections listeners:Connections {
        target:motion.popup
        function onAboutToShow(){motion.dismissing=false;motion.retarget(1);}
        function onAboutToHide(){motion.dismissing=true;motion.retarget(0);}
        function onClosed(){motion.tween.stop();motion.visualProgress=0;motion.dismissing=false;}
    }
}
