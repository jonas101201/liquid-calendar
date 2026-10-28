import QtQuick
import QtQuick.Controls

MenuItem {
    id:item
    property bool light:false
    implicitHeight:38
    leftPadding:12;rightPadding:12
    contentItem:Text {text:item.text;textFormat:Text.PlainText;font.pixelSize:13;color:item.light?"#202631":"#f0f2f6";opacity:item.enabled?1:.4;verticalAlignment:Text.AlignVCenter;elide:Text.ElideRight}
    background:Rectangle {radius:8;color:item.highlighted?(item.light?"#146652ce":"#24b2a5f4"):"transparent";border.width:item.activeFocus?1:0;border.color:item.light?"#6652ce":"#b2a5f4"}
}
