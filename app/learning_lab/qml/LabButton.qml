import QtQuick
import QtQuick.Controls
Button {
    id: control
    Keys.onReturnPressed: click()
    Keys.onEnterPressed: click()
    background: Rectangle {
        implicitWidth: 100
        implicitHeight: 40
        radius: 5
        color: control.highlighted ? control.palette.highlight : control.palette.button
        border.color: "#97beff"
        border.width: control.activeFocus ? 2 : 0
        opacity: control.enabled ? 1 : 0.45
    }
}
