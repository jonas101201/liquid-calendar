import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "Calendar.js" as Cal

Popup {
    id:picker
    property bool light:false
    property color ink:light?"#202631":"#f0f2f6"
    property color muted:light?"#596373":"#adb5c4"
    property color accent:light?"#6652ce":"#b2a5f4"
    property date monthDate:new Date(new Date().getFullYear(),new Date().getMonth(),1,12)
    property string selectedDate:""
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
    width:Math.min(parent?parent.width-12:360,360)
    modal:true;focus:true;padding:14
    background:Rectangle {radius:16;color:picker.light?"#fafbfe":"#242833";border.color:picker.accent;border.width:1}
    function openFor(value){var date=Cal.parse(value)||new Date();selectedDate=Cal.key(date);monthDate=Cal.month(date,0);open();}
    function choose(value){selectedDate=value;picked(value);close();}
    function shift(amount){var next=Cal.month(monthDate,amount);if(next.getFullYear()>=1000&&next.getFullYear()<=9999)monthDate=next;}
    contentItem:ColumnLayout {
        spacing:8
        RowLayout {
            Layout.fillWidth:true
            PickerButton {text:"‹";Accessible.name:"Previous month";onClicked:picker.shift(-1)}
            Label {Layout.fillWidth:true;text:Cal.monthNames[picker.monthDate.getMonth()]+" "+picker.monthDate.getFullYear();color:picker.ink;font.bold:true;horizontalAlignment:Text.AlignHCenter}
            PickerButton {text:"›";Accessible.name:"Next month";onClicked:picker.shift(1)}
        }
        RowLayout {
            Layout.fillWidth:true
            PickerSpin {id:yearChoice;from:1000;to:9999;value:picker.monthDate.getFullYear();editable:true;textFromValue:function(value){return String(value);};Layout.fillWidth:true;Accessible.name:"Calendar year";onValueChanged:if(picker.visible&&value!==picker.monthDate.getFullYear())picker.monthDate=new Date(value,picker.monthDate.getMonth(),1,12)}
            Label {text:"Year";color:picker.muted}
        }
        GridLayout {
            columns:7;columnSpacing:2;rowSpacing:2;Layout.fillWidth:true
            Repeater {model:["Mo","Tu","We","Th","Fr","Sa","Su"];delegate:Label {required property string modelData;text:modelData;color:picker.muted;Layout.fillWidth:true;horizontalAlignment:Text.AlignHCenter;font.pixelSize:11}}
            Repeater {model:42
                delegate:PickerButton {
                    required property int index
                    readonly property date day:Cal.add(Cal.monday(picker.monthDate),index)
                    readonly property string dayKey:Cal.key(day)
                    Layout.fillWidth:true;Layout.preferredWidth:38;Layout.preferredHeight:34;padding:0
                    text:String(day.getDate());Accessible.name:dayKey
                    enabled:day.getFullYear()>=1000&&day.getFullYear()<=9999
                    highlighted:dayKey===picker.selectedDate
                    opacity:day.getMonth()===picker.monthDate.getMonth()?1:.45
                    onClicked:picker.choose(dayKey)
                }
            }
        }
        RowLayout {
            PickerButton {text:"Today";onClicked:picker.choose(Cal.key(new Date()))}
            PickerButton {text:"Tomorrow";onClicked:picker.choose(Cal.key(Cal.add(new Date(),1)))}
            Item {Layout.fillWidth:true}
            PickerButton {text:"Close";onClicked:picker.close()}
        }
    }
}
