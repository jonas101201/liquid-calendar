import QtQuick
import QtQuick.Shapes

// Cubic corners meet their straight edges with zero curvature at each join.
Shape {
    id:contour
    property real radius:18
    property color fillColor:"transparent"
    property color strokeColor:"transparent"
    property real strokeWidth:0
    property alias fillGradient:path.fillGradient
    readonly property real inset:Math.max(0,strokeWidth)/2
    readonly property real shoulder:inset+Math.max(0,Math.min(radius*1.55,(width-2*inset)/2,(height-2*inset)/2))
    preferredRendererType:Shape.CurveRenderer
    antialiasing:true
    ShapePath {
        id:path
        strokeWidth:contour.strokeWidth>0?contour.strokeWidth:-1
        strokeColor:contour.strokeColor;fillColor:contour.fillColor
        joinStyle:ShapePath.RoundJoin
        startX:contour.shoulder;startY:contour.inset
        PathLine {x:contour.width-contour.shoulder;y:contour.inset}
        PathCubic {x:contour.width-contour.inset;y:contour.shoulder;control1X:contour.width-contour.inset;control1Y:contour.inset;control2X:control1X;control2Y:control1Y}
        PathLine {x:contour.width-contour.inset;y:contour.height-contour.shoulder}
        PathCubic {x:contour.width-contour.shoulder;y:contour.height-contour.inset;control1X:contour.width-contour.inset;control1Y:contour.height-contour.inset;control2X:control1X;control2Y:control1Y}
        PathLine {x:contour.shoulder;y:contour.height-contour.inset}
        PathCubic {x:contour.inset;y:contour.height-contour.shoulder;control1X:contour.inset;control1Y:contour.height-contour.inset;control2X:control1X;control2Y:control1Y}
        PathLine {x:contour.inset;y:contour.shoulder}
        PathCubic {x:contour.shoulder;y:contour.inset;control1X:contour.inset;control1Y:contour.inset;control2X:control1X;control2Y:control1Y}
    }
}
