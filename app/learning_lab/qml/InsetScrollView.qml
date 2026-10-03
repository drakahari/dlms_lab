import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Shared page/dialog rhythm. Reserve a scrollbar lane even when it is hidden,
// so opening or scrolling long content never crowds or shifts the right edge.
LabScrollView {
    id: control
    property real contentInset: 20
    readonly property real scrollbarLane: Math.max(12, ScrollBar.vertical.width)
    default property alias sections: body.data
    clip: true
    contentWidth: availableWidth
    contentHeight: body.implicitHeight + 2 * contentInset
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOn
    function ensureVisible(item) {
        if(!contentItem || !contentItem.contentItem) return
        var top=item.mapToItem(contentItem.contentItem,0,0).y
        var next=contentItem.contentY
        if(top<next+contentInset) next=top-contentInset
        else if(top+item.height>next+availableHeight-contentInset) next=top+item.height-availableHeight+contentInset
        contentItem.contentY=Math.max(0,Math.min(Math.max(0,contentHeight-availableHeight),next))
    }
    contentData: Item {
        implicitWidth: control.availableWidth
        implicitHeight: control.contentHeight
        ColumnLayout {
            id: body
            x: control.contentInset; y: control.contentInset
            width: Math.max(0, control.availableWidth - 2 * control.contentInset - control.scrollbarLane)
            spacing: control.contentInset
        }
    }
}
