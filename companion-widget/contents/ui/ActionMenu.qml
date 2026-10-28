import QtQuick
import QtQuick.Controls

Menu {
    id:menu
    property bool light:false
    width:230;padding:6
    background:Rectangle {radius:13;color:menu.light?"#fafbfe":"#242833";border.color:menu.light?"#241c2b42":"#26ffffff"}
}
