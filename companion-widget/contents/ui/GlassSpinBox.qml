import QtQuick
import QtQuick.Controls

SpinBox {
    property color inkColor: "#f5f7ff"
    property color accentColor: "#a498ff"
    property color fieldColor: "#242833"
    property color lineColor: "#32dbe5ff"

    id:spin
    opacity:enabled?1:.5
    implicitWidth:150; implicitHeight:36
    leftPadding:36; rightPadding:36; editable:true
    font.pixelSize:12
    contentItem:TextInput {
        text:spin.textFromValue(spin.value,spin.locale)
        font:spin.font; color:spin.inkColor; selectionColor:spin.accentColor; selectedTextColor:"#111a2b"
        horizontalAlignment:Text.AlignHCenter; verticalAlignment:Text.AlignVCenter
        readOnly:!spin.editable; validator:spin.validator
        inputMethodHints:Qt.ImhDigitsOnly; selectByMouse:true
        onEditingFinished: {
            var parsed=spin.valueFromText(text,spin.locale);
            if(Number.isFinite(parsed)) spin.value=Math.max(spin.from,Math.min(spin.to,Math.round(parsed)));
            text=Qt.binding(function(){return spin.textFromValue(spin.value,spin.locale);});
        }
    }
    up.indicator:Rectangle {
        x:spin.width-width; width:32; height:spin.height; radius:9
        color:spin.up.pressed?Qt.rgba(spin.accentColor.r,spin.accentColor.g,spin.accentColor.b,.25):spin.fieldColor
        Text { anchors.centerIn:parent; text:"+"; color:spin.inkColor; font.pixelSize:18 }
    }
    down.indicator:Rectangle {
        width:32; height:spin.height; radius:9
        color:spin.down.pressed?Qt.rgba(spin.accentColor.r,spin.accentColor.g,spin.accentColor.b,.25):spin.fieldColor
        Text { anchors.centerIn:parent; text:"−"; color:spin.inkColor; font.pixelSize:18 }
    }
    background:Rectangle { radius:10; color:spin.fieldColor; border.color:spin.activeFocus?spin.accentColor:spin.lineColor }
}
