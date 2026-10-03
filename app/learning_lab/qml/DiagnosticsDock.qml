import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: dock; objectName: "diagnosticsDock"
    required property var v
    required property QtObject controller
    property alias commandControl: input
    property alias firstControl: consoleTab
    signal resizeRequested(int delta)
    signal toolsRequested(string tool)
    property bool linuxTools: false
    property bool allowResize: true
    Connections {
        target: controller
        function onChanged() { if(input.text !== v.commandDraft) input.text=v.commandDraft }
    }
    RowLayout {
        Layout.fillWidth: true
        TabBar {
            id: tabs; objectName: "diagnosticTabs"; Layout.fillWidth: true
            LabTabButton { id: consoleTab; objectName: "consoleTab"; text: v.workspaceKind === "linux-service" ? "Simulated Linux terminal" : "Console" }
            LabTabButton { objectName: "resultsTab"; text: "Diagnostics" }
        }
        LabButton { objectName: "openVirtualEditor"; text: "File editor"; visible: dock.linuxTools && v.canEditVirtualFile; onClicked: dock.toolsRequested("editor") }
        LabButton { objectName: "openTerminalHelp"; text: "Help"; visible: dock.linuxTools; onClicked: dock.toolsRequested("help") }
        LabButton { text: "−"; implicitWidth: 38; enabled: dock.allowResize; Accessible.name: "Shrink diagnostics pane"; onClicked: dock.resizeRequested(-40) }
        LabButton { text: "+"; implicitWidth: 38; enabled: dock.allowResize; Accessible.name: "Grow diagnostics pane"; onClicked: dock.resizeRequested(40) }
        LabButton { text: "↺"; implicitWidth: 38; Accessible.name: "Restore default workspace layout"; onClicked: controller.saveLayout({}) }
    }
    StackLayout {
        currentIndex: tabs.currentIndex; Layout.fillWidth: true; Layout.fillHeight: true
        ColumnLayout {
            LabText { text: v.consolePrompt; color: v.palette.muted; Layout.fillWidth: true; font.pixelSize: 12 }
            LabScrollView {
                objectName: "consoleViewport"
                Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                TextArea { objectName: "consoleOutput"; text: v.console || "Type help to see supported simulated commands."; textFormat: TextEdit.PlainText; readOnly: true; wrapMode: TextEdit.Wrap; font.family: "monospace"; font.pixelSize: 13; onTextChanged: cursorPosition=length }
            }
            RowLayout {
                Layout.fillWidth: true
                TextField {
                    id: input; objectName: "commandInput"; Layout.fillWidth: true; text: v.commandDraft; maximumLength: 512; enabled: !v.readOnly
                    property int historyIndex: 0
                    placeholderText: "help"; Accessible.name: "Simulated command"
                    onTextEdited: controller.setCommandDraft(text)
                    function run() { controller.execute(text); historyIndex=0 }
                    onAccepted: run()
                    Keys.onUpPressed: { historyIndex++; var old=controller.commandHistory(historyIndex); if(old) { text=old; controller.setCommandDraft(text) } else historyIndex-- }
                    Keys.onDownPressed: { historyIndex=Math.max(0,historyIndex-1); text=controller.commandHistory(historyIndex);controller.setCommandDraft(text) }
                }
                LabButton { objectName: "runCommand"; text: "Run"; enabled: !v.readOnly; onClicked: { input.run(); input.forceActiveFocus() } }
            }
        }
        LabScrollView {
            id: results; objectName: "diagnosticResults"; clip: true; contentWidth: availableWidth
            ColumnLayout {
                width: results.availableWidth; spacing: 10
                LabText { objectName: "diagnosticRevision"; text: v.diagnosticRevision<0 ? "Run diagnostics on the applied state." : "Tested applied revision " + v.diagnosticRevision + (v.diagnosticRevision===v.revision ? " · current" : " · STALE: state changed; test again"); Layout.fillWidth: true; font.bold: true }
                Repeater {
                    model: v.diagnostics
                    LabText { required property var modelData; text: (modelData.ok ? "PASS · " : "FAIL · ") + modelData.label + "\n" + modelData.evidence; Layout.fillWidth: true; color: modelData.ok ? v.palette.success : v.palette.danger }
                }
            }
        }
    }
}
