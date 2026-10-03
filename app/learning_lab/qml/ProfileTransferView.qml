import QtQuick
import QtQuick.Layouts

InsetScrollView {
    id: control
    property var details: ({})
    property string fieldPrefix: "profile"
    LabText {
        objectName: control.fieldPrefix + "Summary"
        Layout.fillWidth: true; text: control.details.summary || ""
    }
    ColumnLayout {
        Layout.fillWidth: true; spacing: 8
        visible: !!control.details.counts
        LabText { text: "Backup contents"; font.bold: true; Layout.fillWidth: true }
        LabText { objectName: control.fieldPrefix + "Counts"; text: control.details.counts || ""; Layout.fillWidth: true }
        LabText { text: control.details.created || ""; Layout.fillWidth: true }
    }
    ColumnLayout {
        Layout.fillWidth: true; spacing: 8
        visible: !!control.details.labs
        LabText { text: "Included labs"; font.bold: true; Layout.fillWidth: true }
        LabText { text: control.details.labs || ""; Layout.fillWidth: true }
    }
    Repeater {
        model: control.details.paths || []
        CopyablePath {
            required property var modelData
            required property int index
            Layout.fillWidth: true
            label: modelData.label; value: modelData.value
            fieldName: control.fieldPrefix + "Path" + index
            onFocusRequested: function(item) { control.ensureVisible(item) }
        }
    }
    ColumnLayout {
        Layout.fillWidth: true; spacing: 8
        visible: !!control.details.warning
        LabText { text: "Before you continue"; font.bold: true; Layout.fillWidth: true }
        LabText { objectName: control.fieldPrefix + "Warning"; text: control.details.warning || ""; Layout.fillWidth: true }
    }
}
