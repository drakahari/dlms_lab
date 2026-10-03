import QtQuick
import QtQuick.Controls
ScrollView {
    id: control
    activeFocusOnTab: true
    function ensureVisible(item) {
        if(!contentItem || !contentItem.contentItem) return
        var top=item.mapToItem(contentItem.contentItem,0,0).y
        var next=contentItem.contentY
        if(top<next) next=top
        else if(top+item.height>next+availableHeight) next=top+item.height-availableHeight
        contentItem.contentY=Math.max(0,Math.min(Math.max(0,contentItem.contentHeight-availableHeight),next))
    }
    Keys.onPressed: function(event) {
        var amount = 0
        if (event.key === Qt.Key_PageDown) amount = availableHeight * 0.8
        if (event.key === Qt.Key_PageUp) amount = -availableHeight * 0.8
        if (event.key === Qt.Key_Down) amount = 40
        if (event.key === Qt.Key_Up) amount = -40
        if (amount !== 0 && contentItem && contentItem.contentY !== undefined) {
            contentItem.contentY = Math.max(0, Math.min(contentItem.contentHeight - availableHeight, contentItem.contentY + amount))
            event.accepted = true
        }
    }
    Rectangle {
        parent: control
        anchors.fill: parent
        color: "transparent"
        border.color: "#97beff"
        border.width: control.activeFocus ? 2 : 0
    }
}
