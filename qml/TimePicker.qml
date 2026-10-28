import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "Calendar.js" as Cal

Popup {
    id:picker
    property bool light:false
    property color ink:light?"#202631":"#f0f2f6"
    property color accent:light?"#6652ce":"#b2a5f4"
    property color field:light?"#edf0f5":"#303541"
    property color line:light?"#191c2b42":"#24ffffff"
    component PickerButton: Button {
        id:control
        implicitWidth:Math.max(34,contentItem.implicitWidth+18);implicitHeight:34;padding:6
        contentItem:Text {text:control.text;textFormat:Text.PlainText;color:control.highlighted?(picker.light?"#ffffff":"#171620"):picker.ink;font.pixelSize:12;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter;elide:Text.ElideRight}
        background:Rectangle {radius:9;color:control.highlighted?picker.accent:control.hovered?picker.field:"transparent";border.width:control.activeFocus?1:0;border.color:picker.accent}
    }
    component PickerSpin: GlassSpinBox {
        inkColor:picker.ink; accentColor:picker.accent; fieldColor:picker.field; lineColor:picker.line
    }
    signal picked(string value)
    width:Math.min(parent?parent.width-12:320,320)
    modal:true;focus:true;padding:16
    background:Rectangle {radius:16;color:picker.light?"#fafbfe":"#242833";border.color:picker.light?"#6652ce":"#b2a5f4"}
    function openFor(value){var parts=/^([01]\d|2[0-3]):([0-5]\d)$/.exec(value);hours.value=parts?Number(parts[1]):9;minutes.value=parts?Number(parts[2]):0;open();}
    function choose(){picked(Cal.pad(hours.value)+":"+Cal.pad(minutes.value));close();}
    contentItem:ColumnLayout {
        spacing:12
        Label {text:"Start time · 24-hour";color:picker.light?"#202631":"#f0f2f6";font.bold:true}
        RowLayout {
            PickerSpin {id:hours;from:0;to:23;editable:true;wrap:true;Accessible.name:"Start hour";Layout.fillWidth:true}
            Label {text:":";color:picker.light?"#202631":"#f0f2f6"}
            PickerSpin {id:minutes;from:0;to:59;stepSize:5;editable:true;wrap:true;Accessible.name:"Start minute";Layout.fillWidth:true}
        }
        RowLayout {
            Repeater {model:["09:00","12:00","15:00"];delegate:PickerButton {required property string modelData;text:modelData;onClicked:{picker.picked(modelData);picker.close();}}}
        }
        RowLayout {
            PickerButton {text:"Cancel";onClicked:picker.close()}
            Item {Layout.fillWidth:true}
            PickerButton {text:"Use time";highlighted:true;onClicked:picker.choose()}
        }
    }
}
