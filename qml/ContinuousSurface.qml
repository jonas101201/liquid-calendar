import QtQuick

Item {
    id:surface
    property real radius:18
    property color color:"transparent"
    property alias border:pen.border
    Rectangle {id:pen;visible:false;width:0;height:0;border.width:0;border.color:"transparent"}
    ContinuousShape {
        anchors.fill:parent
        radius:surface.radius
        fillColor:surface.color
        strokeColor:surface.border.color
        strokeWidth:surface.border.width
    }
}
