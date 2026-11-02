import QtQuick
import QtQuick.Controls
import "Theme.js" as Theme

MenuItem {
    id:item
    property bool light:false
    property color accent:light?"#006c86":"#7ceafa"
    property string shortcutHint:""
    implicitHeight:visible?38:0
    height:implicitHeight
    leftPadding:checkable?32:12;rightPadding:12
    indicator:Text {visible:item.checkable;x:10;y:(item.height-height)/2;text:item.checked?"✓":"";color:item.accent;font.pixelSize:14}
    contentItem:Item {
        implicitWidth:caption.implicitWidth+(item.shortcutHint?hint.implicitWidth+18:0)
        implicitHeight:caption.implicitHeight
        Text {id:caption;anchors.left:parent.left;anchors.right:hint.left;anchors.rightMargin:item.shortcutHint?12:0;anchors.verticalCenter:parent.verticalCenter;text:item.text;textFormat:Text.PlainText;font.pixelSize:13;color:Theme.palette(item.light,item.accent).ink;opacity:item.enabled?1:.4;elide:Text.ElideRight}
        Text {id:hint;anchors.right:parent.right;anchors.verticalCenter:parent.verticalCenter;text:item.shortcutHint;font.pixelSize:10;color:Theme.palette(item.light,item.accent).muted;opacity:item.enabled?1:.4}
    }
    background:Rectangle {radius:8;color:item.highlighted?(Qt.rgba(item.accent.r,item.accent.g,item.accent.b,.14)):"transparent";border.width:item.activeFocus?1:0;border.color:item.accent}
}
