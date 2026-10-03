import QtQuick
import QtQuick.Controls
TabButton {
    id: control
    Keys.onReturnPressed: click()
    Keys.onEnterPressed: click()
    contentItem: Text {
        text: control.text
        textFormat: Text.PlainText
        font: control.font
        color: control.palette.buttonText
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
    background: Rectangle {
        implicitHeight: 40
        color: control.checked ? control.palette.base : control.palette.button
        border.color: "#97beff"
        border.width: control.activeFocus ? 2 : 0
    }
}
