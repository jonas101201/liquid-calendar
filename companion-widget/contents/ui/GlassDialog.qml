import QtQuick
import QtQuick.Controls

Dialog {
    id:sheet
    property bool motionEnabled:true
    opacity:motion.visualProgress
    scale:.97+.03*motion.visualProgress
    PopupMotion {id:motion;popup:sheet;motionEnabled:sheet.motionEnabled}
    // Keep the popup alive for its visual exit; the independent tween can stop/retarget.
    enter:Transition {PauseAnimation {duration:sheet.motionEnabled?200:0}}
    exit:Transition {PauseAnimation {duration:sheet.motionEnabled?110:0}}
}
