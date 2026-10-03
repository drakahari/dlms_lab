import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

FocusScope {
    id: root; objectName: "linuxTerminalWorkspace"
    required property var v
    required property QtObject controller
    property alias terminalRegion: terminal
    property alias toolsRegion: tools
    property alias consoleControl: terminal.firstControl
    property bool compactReference: false
    property bool toolsOpen: false
    property bool wasDragging: false
    property int requestedHeight: v.workspaceLayout.dock_height || Math.round(height * 0.68)
    property string currentLab: v.labKey
    onCurrentLabChanged: toolsOpen=false
    function focusTerminal() { terminal.commandControl.forceActiveFocus() }
    function applySize() {
        if(!split.resizing && toolsOpen) terminal.SplitView.preferredHeight=requestedHeight
    }
    function rememberSize(value) {
        var sizes=Object.assign({},v.workspaceLayout)
        sizes.dock_height=Math.round(Math.max(root.compactReference && root.toolsOpen ? 110 : 156,Math.min(1800,value)))
        controller.saveLayout(sizes)
        applySize()
    }
    function openTool(tool) {
        toolsOpen=true; auxiliary.showTool(tool)
        Qt.callLater(function(){applySize();auxiliary.focusTool()})
    }
    onRequestedHeightChanged: Qt.callLater(applySize)
    onHeightChanged: Qt.callLater(applySize)
    SplitView {
        id: split; objectName: "linuxTerminalSplit"; anchors.fill: parent; orientation: Qt.Vertical
        handle: Rectangle {
            objectName: "linuxTerminalDivider"; implicitHeight: 8
            activeFocusOnTab: root.toolsOpen
            Accessible.name: "Resize terminal and supporting tools. Use Up and Down arrows."
            Keys.onUpPressed: root.rememberSize(terminal.height-20)
            Keys.onDownPressed: root.rememberSize(terminal.height+20)
            color: activeFocus || SplitHandle.pressed ? v.palette.accent : v.palette.muted
            Rectangle { anchors.centerIn: parent; width: 48; height: 2; color: v.palette.background }
        }
        onResizingChanged: {
            if(resizing) root.wasDragging=true
            else if(root.wasDragging) { root.wasDragging=false; root.rememberSize(terminal.height) }
        }
        LinuxConsole {
            id: terminal; v: root.v; controller: root.controller; showTools: !(root.compactReference && root.toolsOpen)
            SplitView.fillHeight: !root.toolsOpen
            SplitView.minimumHeight: terminal.showTools ? 156 : 110
            SplitView.maximumHeight: root.toolsOpen ? Math.max(terminal.showTools ? 156 : 110,split.height-148) : Infinity
            onToolsRequested: function(tool) {root.openTool(tool)}
        }
        FocusScope {
            id: tools; objectName: "domainWorkspace"; visible: root.toolsOpen
            SplitView.fillHeight: true; SplitView.minimumHeight: 140
            Rectangle { anchors.fill: parent; color: root.v.palette.surface; radius: 7 }
            LinuxServiceWorkspace {
                id: auxiliary; anchors.fill: parent; anchors.margins: 4; v: root.v; controller: root.controller; focus: true
                onCloseRequested: {root.toolsOpen=false;root.focusTerminal()}
            }
        }
    }
}
