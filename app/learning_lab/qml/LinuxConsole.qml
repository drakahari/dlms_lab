import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// Linux-only presentation. Commands still enter through the simulated controller.
ColumnLayout {
    id: dock; objectName: "diagnosticsDock"
    required property var v
    required property QtObject controller
    property alias commandControl: input
    property alias firstControl: terminalHeading
    signal toolsRequested(string tool)
    property bool showTools: true
    spacing: 6
    Connections {
        target: controller
        function onChanged() { if(input.text !== v.commandDraft) input.text=v.commandDraft }
    }
    RowLayout {
        visible: dock.showTools
        Layout.fillWidth: true; spacing: 6
        LabButton { objectName: "openTerminalHelp"; text: "Command reference"; onClicked: dock.toolsRequested("help") }
        LabButton { objectName: "openVirtualEditor"; text: "Virtual file editor"; visible: v.canEditVirtualFile; onClicked: dock.toolsRequested("editor") }
        LabButton { objectName: "resultsTab"; text: "Diagnostics"; onClicked: dock.toolsRequested("diagnostics") }
        Item { Layout.fillWidth: true }
    }
    Rectangle {
        id: consoleFrame; objectName: "linuxConsole"
        Layout.fillWidth: true; Layout.fillHeight: true
        // Stable accessible console colors, independent of the surrounding theme.
        color: "#080e16"; border.color: "#63758c"; radius: 7
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 10; spacing: 4
            RowLayout {
                Layout.fillWidth: true
                ToolButton {
                    id: terminalHeading; objectName: "consoleTab"; text: "Terminal"
                    Accessible.name: "Terminal — focus command entry"
                    font.bold: true; font.pixelSize: 16; padding: 0
                    contentItem: Text { text: terminalHeading.text; color: "#eef4fc"; font: terminalHeading.font }
                    background: Rectangle { color: "transparent"; border.color: terminalHeading.activeFocus ? "#97beff" : "transparent"; radius: 3 }
                    onClicked: input.forceActiveFocus()
                    Keys.onReturnPressed: input.forceActiveFocus()
                }
                Rectangle {
                    implicitWidth: badge.implicitWidth+14; implicitHeight: badge.implicitHeight+6
                    color: "#243448"; radius: 4
                    Text { id: badge; anchors.centerIn: parent; text: "Simulated Linux"; color: "#eef4fc"; font.pixelSize: 11 }
                }
                Item { Layout.fillWidth: true }
            }
            LabScrollView {
                id: transcript; objectName: "consoleViewport"; contentWidth: availableWidth; contentHeight: output.height; Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                onAvailableHeightChanged: Qt.callLater(function(){ if(contentItem) contentItem.contentY=Math.max(0,Math.min(contentItem.contentY,output.height-availableHeight)) })
                TextEdit {
                    id: output; objectName: "consoleOutput"; width: transcript.availableWidth; height: implicitHeight; text: v.console || "Type help and press Enter."
                    textFormat: TextEdit.PlainText; readOnly: true; selectByMouse: true; activeFocusOnTab: true
                    wrapMode: TextEdit.Wrap; font.family: "monospace"; font.pixelSize: 14
                    color: "#eef4fc"; selectionColor: "#97beff"; selectedTextColor: "#080e16"
                    // Follow new output without changing focus or existing text selection on refresh.
                    onTextChanged: { cursorPosition=length; Qt.callLater(function(){if(transcript.contentItem) transcript.contentItem.contentY=Math.max(0,output.height-transcript.availableHeight)}) }
                }
            }
            Rectangle { Layout.fillWidth: true; implicitHeight: 1; color: "#63758c" }
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Text {
                    objectName: "terminalPrompt"; text: "learner@lab:" + v.serviceCwd + "$"
                    Layout.maximumWidth: consoleFrame.width * 0.42; elide: Text.ElideMiddle
                    font.family: "monospace"; font.pixelSize: 14; color: "#97beff"
                    Accessible.name: text
                    ToolTip.visible: promptHover.hovered
                    ToolTip.text: text
                    HoverHandler { id: promptHover }
                }
                TextField {
                    id: input; objectName: "commandInput"; Layout.fillWidth: true
                    text: v.commandDraft; maximumLength: 512; enabled: !v.readOnly
                    placeholderText: "Type a command…"; placeholderTextColor: "#b3c2d6"
                    color: "#eef4fc"; selectionColor: "#97beff"; selectedTextColor: "#080e16"
                    font.family: "monospace"; font.pixelSize: 14; selectByMouse: true
                    Accessible.name: "Simulated Linux command entry"
                    background: Rectangle { color: "#142133"; radius: 4; border.color: input.activeFocus ? "#97beff" : "#63758c" }
                    property int historyIndex: 0
                    onTextEdited: controller.setCommandDraft(text)
                    function run() { controller.execute(text); historyIndex=0 }
                    onAccepted: run()
                    Keys.onUpPressed: { historyIndex++; var old=controller.commandHistory(historyIndex); if(old) { text=old; controller.setCommandDraft(text) } else historyIndex-- }
                    Keys.onDownPressed: { historyIndex=Math.max(0,historyIndex-1); text=controller.commandHistory(historyIndex);controller.setCommandDraft(text) }
                }
                LabButton { objectName: "runCommand"; text: "Run"; implicitWidth: 54; implicitHeight: 34; enabled: !v.readOnly; onClicked: { input.run(); input.forceActiveFocus() } }
            }
        }
    }
}
