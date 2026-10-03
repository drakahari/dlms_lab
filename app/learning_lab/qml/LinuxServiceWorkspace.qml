import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: workspace; objectName: "linuxServiceWorkspace"
    required property var v
    required property QtObject controller
    signal closeRequested()
    property string currentLab: v.labKey
    onCurrentLabChanged: appliedToggle.checked=false
    function showTool(tool) { tabs.currentIndex=tool === "editor" && v.canEditVirtualFile ? 0 : tool === "diagnostics" ? 2 : 1 }
    function focusTool() { if(tabs.currentIndex === 0) editor.forceActiveFocus(); else if(tabs.currentIndex === 1) helpTab.forceActiveFocus(); else diagnosticsTab.forceActiveFocus() }
    Connections {
        target: controller
        function onChanged() { if(editor.text !== v.virtualFileDraft) editor.text=v.virtualFileDraft }
    }
    RowLayout {
    TabBar {
        id: tabs; objectName: "serviceTabs"; Layout.fillWidth: true
        LabTabButton { objectName: "virtualEditorTab"; text: "Virtual file editor"; visible: v.canEditVirtualFile }
        LabTabButton {
            id: helpTab; objectName: "terminalHelpTab"; text: "Command reference"
            KeyNavigation.tab: tabs.currentIndex === 0 ? (v.readOnly ? appliedToggle : editor) : null
        }
        LabTabButton { id: diagnosticsTab; text: "Diagnostics" }
    }
    LabButton { objectName: "closeLinuxTools"; text: "Close"; onClicked: workspace.closeRequested() }
    }
    StackLayout {
        currentIndex: tabs.currentIndex; Layout.fillWidth: true; Layout.fillHeight: true
        LabScrollView {
            id: editorScroll; objectName: "virtualEditorViewport"; contentWidth: availableWidth; clip: true
            function showCursor(item) {
                if(!contentItem || !contentItem.contentItem) return
                var point=item.mapToItem(contentItem.contentItem,item.cursorRectangle.x,item.cursorRectangle.y)
                var top=contentItem.contentY
                if(point.y<top) top=point.y
                else if(point.y+item.cursorRectangle.height>top+availableHeight) top=point.y+item.cursorRectangle.height-availableHeight
                contentItem.contentY=Math.max(0,Math.min(Math.max(0,contentItem.contentHeight-availableHeight),top))
            }
            Item {
                width: editorScroll.availableWidth; implicitHeight: editorContent.implicitHeight+24
            ColumnLayout {
                id: editorContent; x: 12; y: 12; width: parent.width-24; spacing: 12
                LabText { text: v.virtualFilePath + " · virtual file only"; font.bold: true; Layout.fillWidth: true }
                LabText { text: "Apply saves the draft. Start/restart loads it into the service."; Layout.fillWidth: true; color: v.palette.muted }
                LabText { objectName: "editingConstraints"; text: v.constraints.length ? "Lab rule · " + v.constraints[0] : ""; Layout.fillWidth: true; color: v.palette.muted }
                Rectangle {
                    Layout.fillWidth: true; implicitHeight: draftGroup.implicitHeight+24
                    color: v.palette.background; radius: 6
                    ColumnLayout {
                        id: draftGroup; x: 12; y: 12; width: parent.width-24; spacing: 10
                        LabText { text: "Editable draft"; font.bold: true; Layout.fillWidth: true }
                TextArea {
                    id: editor; objectName: "virtualFileEditor"; Layout.fillWidth: true
                    Layout.preferredHeight: Math.max(85,implicitHeight)
                    text: v.virtualFileDraft; textFormat: TextEdit.PlainText; wrapMode: TextEdit.Wrap
                    font.family: "monospace"; font.pixelSize: 14; padding: 10; selectByMouse: true; enabled: !v.readOnly; activeFocusOnTab: true
                    Accessible.name: "Draft virtual service configuration"
                    // Tab navigates out of this simple editor; it never traps the
                    // keyboard by inserting indentation into the configuration.
                    Keys.onPressed: function(event) {
                        if(event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) {
                            var back = event.key === Qt.Key_Backtab || (event.modifiers & Qt.ShiftModifier)
                            var target = back ? helpTab : appliedToggle
                            target.forceActiveFocus(back ? Qt.BacktabFocusReason : Qt.TabFocusReason)
                            event.accepted=true
                        }
                    }
                    onTextChanged: if(activeFocus && text !== v.virtualFileDraft) {
                        controller.edit(v.virtualFilePath,text)
                        if(text !== v.virtualFileDraft) text=v.virtualFileDraft
                    }
                    onActiveFocusChanged: if(activeFocus) { if(height<=editorScroll.availableHeight) editorScroll.ensureVisible(editor); else editorScroll.showCursor(editor) }
                    onCursorRectangleChanged: if(activeFocus) editorScroll.showCursor(editor)
                }
                    }
                }
                LabButton {
                    id: appliedToggle; objectName: "appliedVersionToggle"; Layout.fillWidth: true
                    text: "Applied version " + (checked ? "▾" : "▸"); checkable: true; checked: false
                    onActiveFocusChanged: if(activeFocus) editorScroll.ensureVisible(this)
                    KeyNavigation.backtab: editor
                    KeyNavigation.tab: checked ? applied : null
                }
                Rectangle {
                    visible: appliedToggle.checked; Layout.fillWidth: true; implicitHeight: appliedGroup.implicitHeight+24
                    color: v.palette.background; radius: 6
                    ColumnLayout {
                        id: appliedGroup; x: 12; y: 12; width: parent.width-24; spacing: 10
                        LabText { text: "Read only · used by terminal and grading"; Layout.fillWidth: true; color: v.palette.muted }
                TextArea {
                    id: applied; objectName: "virtualFileApplied"; Layout.fillWidth: true
                    text: v.virtualFileApplied; textFormat: TextEdit.PlainText; readOnly: true; wrapMode: TextEdit.Wrap
                    font.family: "monospace"; font.pixelSize: 14; padding: 10; selectByMouse: true; activeFocusOnTab: true
                    Accessible.name: "Applied virtual service configuration"
                    Keys.onPressed: function(event) {
                        if(event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) {
                            var back = event.key === Qt.Key_Backtab || (event.modifiers & Qt.ShiftModifier)
                            var target = back ? appliedToggle : nextItemInFocusChain(true)
                            target.forceActiveFocus(back ? Qt.BacktabFocusReason : Qt.TabFocusReason)
                            event.accepted=true
                        }
                    }
                    onActiveFocusChanged: if(activeFocus) editorScroll.ensureVisible(applied)
                    onCursorRectangleChanged: if(activeFocus) editorScroll.showCursor(applied)
                }
                    }
                }
            }
            }
        }
        LabScrollView {
            id: help; contentWidth: availableWidth; clip: true
            LabText { width: help.availableWidth; text: v.terminalHelp; font.family: "monospace" }
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
