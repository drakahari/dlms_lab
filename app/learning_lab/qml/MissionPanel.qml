import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

LabScrollView {
    id: panel
    objectName: "missionPanel"
    required property var v
    required property QtObject controller
    signal resizeRequested(int delta)
    clip: true
    contentWidth: availableWidth
    ColumnLayout {
        width: panel.availableWidth; spacing: 12
        RowLayout {
            Layout.fillWidth: true
            LabText { text: "MISSION · scroll for details"; color: v.palette.accent; font.bold: true; Layout.fillWidth: true }
            LabButton { text: "−"; implicitWidth: 28; Accessible.name: "Shrink instructions pane"; onClicked: panel.resizeRequested(-20) }
            LabButton { text: "+"; implicitWidth: 28; Accessible.name: "Grow instructions pane"; onClicked: panel.resizeRequested(20) }
        }
        LabText { objectName: "missionBrief"; text: v.metadata.brief; Layout.fillWidth: true }
        LabText { text: "Objectives"; font.bold: true }
        Repeater {
            model: v.objectives
            LabText { required property var modelData; text: "• " + modelData.label + " · " + modelData.points + " pts"; Layout.fillWidth: true }
        }
        LabText { visible: v.constraints.length>0; text: "Constraints"; font.bold: true }
        Repeater {
            model: v.constraints
            LabText { required property string modelData; text: "• " + modelData; Layout.fillWidth: true }
        }
        LabText { text: v.mode === "Learn" ? "Hints · " + v.hintCount + "/" + v.hintTotal + " used · no score penalty" : "Challenge · hints hidden"; font.bold: true; Layout.fillWidth: true }
        Repeater {
            model: v.hints
            LabText { required property string modelData; required property int index; objectName: "shownHint" + index; text: (index+1) + ". " + modelData; Layout.fillWidth: true }
        }
        LabButton { objectName: "hintButton"; text: "Reveal next hint"; visible: v.mode === "Learn"; enabled: !v.readOnly && v.hintCount < v.hintTotal
            onClicked: { controller.hint(); Qt.callLater(function(){panel.contentItem.contentY=Math.max(0,panel.contentItem.contentHeight-panel.availableHeight)}) }
            onActiveFocusChanged: if(activeFocus) panel.contentItem.contentY=Math.max(0,panel.contentItem.contentHeight-panel.availableHeight)
        }
        LabText { text: "Simulation only. Portal checks model DNS and reachability; TCP permission uses connect. No real commands or traffic."; color: v.palette.muted; Layout.fillWidth: true }
    }
}
