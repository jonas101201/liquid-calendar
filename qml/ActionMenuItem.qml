import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

MenuItem {
    id:item
    property bool light:false
    property color accent:light?"#006c86":"#7ceafa"
    implicitHeight:visible?38:0
    height:implicitHeight
    leftPadding:checkable?32:12;rightPadding:12
    indicator:Text {visible:item.checkable;x:10;y:(item.height-height)/2;text:item.checked?"✓":"";color:item.accent;font.pixelSize:14}
    contentItem:Text {text:item.text;textFormat:Text.PlainText;font.pixelSize:13;color:Theme.palette(item.light,item.accent).ink;opacity:item.enabled?1:.4;verticalAlignment:Text.AlignVCenter;elide:Text.ElideRight}
    background:Rectangle {radius:8;color:item.highlighted?(Qt.rgba(item.accent.r,item.accent.g,item.accent.b,.14)):"transparent";border.width:item.activeFocus?1:0;border.color:item.accent}
}
