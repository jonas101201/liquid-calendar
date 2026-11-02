import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Text {
    id:heading
    property string sourceText:""
    property bool fullTextHint:true
    textFormat:Text.PlainText
    Layout.preferredWidth:metrics.advanceWidth(sourceText)
    maximumLineCount:2
    wrapMode:Text.Wrap
    elide:Text.ElideRight
    FontMetrics {id:metrics;font:heading.font}
    function balanced(value,available) {
        if(maximumLineCount<2||available<=0||value.indexOf("\n")>=0||metrics.advanceWidth(value)<=available)return value;
        var words=value.trim().split(/\s+/),best=value,score=Infinity;
        for(var i=1;i<words.length;i++) {
            var first=words.slice(0,i).join(" "),second=words.slice(i).join(" ");
            var a=metrics.advanceWidth(first),b=metrics.advanceWidth(second);
            if(a>available||b>available)continue;
            var difference=Math.abs(a-b);
            if(difference<score){score=difference;best=first+"\n"+second;}
        }
        return best;
    }
    text:balanced(sourceText,width)
    ToolTip.visible:fullTextHint&&headingHover.hovered&&truncated
    ToolTip.delay:650
    ToolTip.text:sourceText
    HoverHandler {id:headingHover}
    Accessible.name:sourceText
}
