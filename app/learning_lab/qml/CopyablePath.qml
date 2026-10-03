import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: control
    required property string label
    required property string value
    property string fieldName: ""
    signal focusRequested(var item)
    spacing: 8
    LabText { text: control.label; font.bold: true; Layout.fillWidth: true }
    RowLayout {
        Layout.fillWidth: true; spacing: 10
        TextField {
            id: field; objectName: control.fieldName
            Layout.fillWidth: true; Layout.minimumWidth: 0
            text: control.value; readOnly: true; selectByMouse: true; clip: true
            font.pixelSize: 15
            leftPadding: 12; rightPadding: 12; topPadding: 10; bottomPadding: 10
            Accessible.name: control.label
            onTextChanged: cursorPosition = 0
            Component.onCompleted: cursorPosition = 0
            // Single-line text scrolls horizontally; it never splits ordinary words.
            onActiveFocusChanged: if(activeFocus) control.focusRequested(control)
        }
        LabButton {
            objectName: control.fieldName + "Copy"
            property bool copied: false
            text: copied ? "Copied" : "Copy"
            Accessible.name: "Copy " + control.label
            onClicked: { field.selectAll(); field.copy(); copied=true }
            onActiveFocusChanged: if(activeFocus) control.focusRequested(control)
        }
    }
}
