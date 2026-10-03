import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: workspace; objectName: "networkWorkspace"
    required property var v
    required property QtObject controller
    required property var hostWindow
    property bool condensed: height < 340
    property real tabWidth: width/(condensed ? (v.hasFirewall ? 4 : 3) : (v.hasFirewall ? 3 : 2))
    property string activeLab: v.labKey
    onActiveLabChanged: tools.currentIndex=1
    onCondensedChanged: if(!condensed && tools.currentIndex===0) tools.currentIndex=1
    spacing: 6
    TopologyPanel {
        v: workspace.v; controller: workspace.controller
        visible: !workspace.condensed
        Layout.fillWidth: true; Layout.preferredHeight: 190; Layout.minimumHeight: 175; Layout.maximumHeight: 200
    }
    TabBar {
        id: tools; objectName: "inspectorTabs"; Layout.fillWidth: true; currentIndex: 1
        LabTabButton { width: visible ? workspace.tabWidth : 0; objectName: "topologyTab"; text: "Topology"; visible: workspace.condensed }
        LabTabButton { width: workspace.tabWidth; objectName: "inspectTab"; text: "Inspect" }
        LabTabButton { id: settingsTab; width: workspace.tabWidth; objectName: "settingsTab"; text: "Settings"
            onClicked: Qt.callLater(function(){settings.focusFirst()})
            Keys.onTabPressed: if(v.hasFirewall) firewallTab.forceActiveFocus(Qt.TabFocusReason); else settings.focusFirst()
        }
        LabTabButton { id: firewallTab; width: visible ? workspace.tabWidth : 0; objectName: "firewallTab"; text: "Firewall"; visible: v.hasFirewall
            onClicked: Qt.callLater(function(){firewall.focusFirst()})
            Keys.onTabPressed: firewall.focusFirst()
        }
    }
    StackLayout {
        currentIndex: tools.currentIndex; Layout.fillWidth: true; Layout.fillHeight: true
        TopologyPanel { objectName: "compactTopologyPanel"; v: workspace.v; controller: workspace.controller }
        LabScrollView {
            id: inspect; clip: true; contentWidth: availableWidth
            LabText { width: inspect.availableWidth; text: v.deviceDetails; font.family: "monospace" }
        }
        SettingsPanel { id: settings; beforePanel: settingsTab; afterPanel: workspace.hostWindow.consoleControl; v: workspace.v; controller: workspace.controller }
        FirewallPanel { id: firewall; v: workspace.v; controller: workspace.controller; hostWindow: workspace.hostWindow; beforePanel: tools; afterPanel: workspace.hostWindow.consoleControl }
    }
}
