import QtQuick

ListView {
    id:list
    property var refreshSource:null
    property string contextKey:""
    property var remembered:({})
    onModelChanged:Qt.callLater(restore)
    onVisibleChanged:if(visible)Qt.callLater(restore)
    function recordKey(index) {
        if(index<0||index>=count||!model)return "";
        var record=model[index],event=record.event||record;
        return (record.id||event.id)+"|"+(record.occurrenceDate||record.date||event.date||"")+"|"+(record.carry===true);
    }
    function indexFor(key) {for(var i=0;i<count;i++)if(recordKey(i)===key)return i;return -1;}
    function capture() {
        if(!visible||height<=0||!count)return;
        var index=-1;
        for(var y=1;y<Math.min(height,100)&&index<0;y+=4)index=indexAt(2,contentY+y);
        if(index<0)return;
        var item=itemAtIndex(index),states=Object.assign({},remembered);
        states[contextKey]={anchor:recordKey(index),index:index,offset:item?item.y-contentY:0,selection:recordKey(currentIndex)};
        var keys=Object.keys(states);if(keys.length>24)delete states[keys[0]];
        remembered=states;
    }
    function restore() {
        if(!visible||height<=0||!count)return;
        var state=remembered[contextKey];if(!state)return;
        var index=indexFor(state.anchor);if(index<0)index=Math.min(state.index,count-1);
        forceLayout();positionViewAtIndex(index,ListView.Beginning);forceLayout();
        var item=itemAtIndex(index);
        if(item)contentY=Math.max(originY,Math.min(originY+Math.max(0,contentHeight-height),item.y-state.offset));
        var selection=indexFor(state.selection);currentIndex=selection;
    }
    Connections {
        target:list.refreshSource
        function onAboutToRefresh(){list.capture();}
        function onChanged(){Qt.callLater(list.restore);}
    }
}
