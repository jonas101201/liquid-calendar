import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

Menu {
    id:menu
    property bool light:false
    property color accent:light?"#006c86":"#7ceafa"
    width:230;padding:6
    background:Rectangle {radius:13;color:Theme.palette(menu.light,menu.accent).panel;border.color:Qt.rgba(menu.accent.r,menu.accent.g,menu.accent.b,.3)}
}
