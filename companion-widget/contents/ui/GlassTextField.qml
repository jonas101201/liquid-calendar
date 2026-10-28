import QtQuick
import QtQuick.Controls

TextField {
    property color inkColor: "#f5f7ff"
    property color accentColor: "#a498ff"
    property color fieldColor: "#242833"
    property color lineColor: "#32dbe5ff"
    property color mutedColor: "#ccd6e8"

    id: control
    opacity:enabled?1:.5
    selectionColor:control.accentColor; selectedTextColor:"#111a2b"
    color: control.inkColor
    placeholderTextColor: control.mutedColor
    font.pixelSize: 12
    leftPadding: 10; rightPadding: 10; topPadding: 8; bottomPadding: 8
    implicitHeight: 36
    background: Rectangle { radius: 10; color: control.fieldColor; border.color: parent.activeFocus ? control.accentColor : control.lineColor }
}
