import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs as FileDialogs

Dialog {
    id: panel; objectName: "authoringDialog"
    required property QtObject workflow
    property var v: workflow.view
    property int section: 0
    parent: Overlay.overlay
    anchors.centerIn: parent
    width: Math.min(780,parent.width-32); height: Math.min(720,parent.height-32)
    modal: true; title: "Create a lab · Linux permissions"
    contentItem: ColumnLayout {
        TabBar {
            id: tabs; Layout.fillWidth: true; currentIndex: panel.section
            onCurrentIndexChanged: panel.section=currentIndex
            LabTabButton { objectName: "authorGuideTab"; text: "Quick guide" }
            LabTabButton { objectName: "authorExampleTab"; text: "Worked example" }
            LabTabButton { objectName: "authorPromptTab"; text: "AI prompt" }
            LabTabButton { objectName: "authorResultTab"; text: "Validation" }
        }
        InsetScrollView {
            id: reference; objectName: "authorReference"
            Layout.fillWidth: true; Layout.fillHeight: true
            LabText {
                Layout.fillWidth: true
                text: panel.section===3 ? panel.v.message : "Data-only scenarios for the shipped permissions engine. No new commands, scripts or simulation behavior."
                Accessible.name: text
            }
            TextArea {
                id: body; objectName: "authorReferenceText"
                Layout.fillWidth: true
                readOnly: true; selectByMouse: true; textFormat: TextEdit.PlainText
                wrapMode: TextEdit.Wrap; font.pixelSize: 15
                font.family: panel.section===1 ? "monospace" : "sans-serif"
                text: panel.section===0 ? panel.v.guide : panel.section===1 ? panel.v.example : panel.section===2 ? panel.v.prompt : panel.v.summary
                Accessible.name: panel.section===3 ? "Validated pack summary, not a gameplay test" : "Authoring reference"
            }
            LabButton {
                objectName: "copyAuthorReference"; text: panel.section===2 ? "Copy AI prompt" : "Copy reference"
                visible: panel.section!==3
                onClicked: { body.selectAll(); body.copy(); body.deselect() }
                onActiveFocusChanged: if(activeFocus) reference.ensureVisible(this)
            }
        }
    }
    footer: DialogButtonBox {
        LabButton { objectName: "saveStarterButton"; text: "Save starter…"; onClicked: saveFile.open() }
        LabButton { objectName: "validateAuthorLabButton"; text: "Validate lab…"; onClicked: validateFile.open() }
        LabButton { objectName: "importValidatedButton"; text: "Import validated lab"; enabled: panel.section===3 && panel.v.canImport; onClicked: { workflow.importValidated(); panel.section=3 } }
        LabButton { id: closeButton; objectName: "closeAuthoring"; text: "Close"; onClicked: panel.close() }
    }
    onOpened: { section=0; tabs.itemAt(0).forceActiveFocus() }
    FileDialogs.FileDialog {
        id: saveFile; objectName: "starterFileDialog"; title: "Save a new permissions starter"
        fileMode: FileDialogs.FileDialog.SaveFile; defaultSuffix: "lab.json"
        nameFilters: ["Learning Lab scenario (*.lab.json)"]
        onAccepted: { if(workflow.prepareStarter(selectedFile.toString())) saveConfirmation.open(); else panel.section=3 }
        onRejected: closeButton.forceActiveFocus()
    }
    FileDialogs.FileDialog {
        id: validateFile; objectName: "validateAuthorFileDialog"; title: "Validate a data-only scenario"
        nameFilters: ["Learning Lab scenarios (*.lab.json)", "JSON files (*.json)"]
        onAccepted: { workflow.validateLab(selectedFile.toString()); panel.section=3; tabs.itemAt(3).forceActiveFocus() }
        onRejected: closeButton.forceActiveFocus()
    }
    Dialog {
        id: saveConfirmation; objectName: "starterConfirmation"
        parent: Overlay.overlay; anchors.centerIn: parent
        width: Math.min(660,parent.width-40); height: Math.min(360,parent.height-40)
        modal: true; title: panel.v.replacing ? "Replace this file?" : "Save this starter?"
        contentItem: InsetScrollView {
            LabText { Layout.fillWidth: true; text: panel.v.replacing ? "This replaces the selected file with a new starter and a new scenario ID. Cancel keeps the original file." : "Save a new starter with a unique scenario ID. Nothing will be imported." }
            CopyablePath { Layout.fillWidth: true; label: "Destination"; value: panel.v.savePath; fieldName: "starterDestination" }
        }
        footer: DialogButtonBox {
            LabButton { id: cancelSave; objectName: "cancelStarterSave"; text: "Cancel"; onClicked: saveConfirmation.reject() }
            LabButton { objectName: "confirmStarterSave"; text: panel.v.replacing ? "Replace file" : "Save starter"; onClicked: saveConfirmation.accept() }
        }
        onOpened: cancelSave.forceActiveFocus()
        onAccepted: { workflow.confirmStarter(true); panel.section=3 }
        onRejected: workflow.confirmStarter(false)
        onClosed: closeButton.forceActiveFocus()
    }
}
