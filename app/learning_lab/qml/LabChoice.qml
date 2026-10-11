import QtQuick
import QtQuick.Controls

// Keep the Basic ComboBox's navigation/activation behavior, with explicit
// readable color pairs instead of its unrelated palette.light highlight fill.
ComboBox {
    id: control
    hoverEnabled: true
    padding: 10
    leftPadding: 12
    rightPadding: 34
    implicitHeight: Math.max(44, contentItem.implicitHeight + topPadding + bottomPadding)
    displayText: currentIndex >= 0 ? currentText : "No selection available"
    contentItem: Text {
        text: control.displayText
        font: control.font
        color: control.enabled ? control.palette.buttonText : control.palette.mid
        wrapMode: Text.Wrap
        verticalAlignment: Text.AlignVCenter
    }
    indicator: Text {
        text: "▾"
        x: control.width - width - 12
        y: (control.height - height) / 2
        font: control.font
        color: control.enabled ? control.palette.buttonText : control.palette.mid
    }
    background: Rectangle {
        implicitWidth: 240
        implicitHeight: 44
        radius: 5
        color: control.palette.button
        border.color: control.activeFocus ? control.palette.highlight : control.palette.mid
        border.width: control.activeFocus ? 2 : 1
    }
    delegate: ItemDelegate {
        id: row
        required property int index
        objectName: "labChoiceRow" + index
        width: ListView.view.width
        text: control.textAt(index)
        highlighted: control.highlightedIndex === index
        hoverEnabled: control.hoverEnabled
        readonly property bool marked: highlighted || hovered || activeFocus
        padding: 12
        rightPadding: 24 // Reserve a lane for the popup scrollbar.
        contentItem: Text {
            text: row.text
            font: control.font
            color: row.marked ? control.palette.highlightedText : control.palette.text
            wrapMode: Text.Wrap
            verticalAlignment: Text.AlignVCenter
        }
        background: Rectangle {
            color: row.marked ? control.palette.highlight : control.palette.window
            border.color: control.currentIndex === row.index ? control.palette.highlight : "transparent"
            border.width: control.currentIndex === row.index ? 1 : 0
        }
    }
    popup: Popup {
        y: control.height + 2
        width: control.width
        padding: 1
        topMargin: 8
        bottomMargin: 8
        palette: control.palette
        font: control.font
        implicitHeight: Math.min(list.contentHeight + 2, Math.max(80, control.Window.height * 0.55))
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
        contentItem: ListView {
            id: list
            clip: true
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
            highlightMoveDuration: 0
            boundsBehavior: Flickable.StopAtBounds
            ScrollBar.vertical: ScrollBar { }
        }
        background: Rectangle {
            color: control.palette.window
            border.color: control.palette.mid
            radius: 4
        }
    }
}
