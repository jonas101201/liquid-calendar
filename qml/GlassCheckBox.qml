import QtQuick
import QtQuick.Controls

CheckBox {
    property color inkColor: "#f5f7ff"
    property color accentColor: "#a498ff"
    property color fieldColor: "#242833"
    property color lineColor: "#32dbe5ff"

    id: check
    padding:0; spacing:8; implicitHeight:32
    contentItem:Text { text:check.text; textFormat:Text.PlainText; color:check.inkColor; font.pixelSize:12; leftPadding:28; verticalAlignment:Text.AlignVCenter }
    indicator:Rectangle {
        x:0; y:(check.height-height)/2; width:20; height:20; radius:6
        color:check.checked?check.accentColor:check.fieldColor
        border.color:check.activeFocus?check.accentColor:check.lineColor
        Text { anchors.centerIn:parent; visible:check.checked; text:"✓"; font.pixelSize:14; font.bold:true; color:"#111a2b" }
    }
}
