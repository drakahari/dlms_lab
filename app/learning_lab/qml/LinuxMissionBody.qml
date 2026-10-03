import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: body
    required property var v
    required property QtObject controller
    required property var scrollPanel
    signal resizeRequested(int delta)
    signal detailsRequested()
    function focusDetails() { details.forceActiveFocus() }
    property alias firstControl: shrink
    property string currentLab: v.labKey
    onCurrentLabChanged: Qt.callLater(function() {
        scrollPanel.contentItem.contentY=0
    })
    spacing: 12
    RowLayout {
        Layout.fillWidth: true
        LabText { text: "GOAL"; color: v.palette.accent; font.bold: true; Layout.fillWidth: true }
        LabButton { id: shrink; text: "−"; implicitWidth: 28; Accessible.name: "Shrink instructions pane"; onClicked: body.resizeRequested(-20); KeyNavigation.tab: grow }
        LabButton { id: grow; text: "+"; implicitWidth: 28; Accessible.name: "Grow instructions pane"; onClicked: body.resizeRequested(20); KeyNavigation.tab: hint.visible && hint.enabled ? hint : details }
    }
    LabText { objectName: "missionGoal"; text: v.missionGoal; font.bold: true; Layout.fillWidth: true }
    LabText {
        objectName: "missionProgress"; Layout.fillWidth: true; color: v.palette.muted; font.pixelSize: 13
        text: (v.hasGrade ? "Submitted · " + v.grade.score + "/100" : "Not submitted · " + v.objectives.length + (v.objectives.length === 1 ? " objective" : " objectives")) + (v.dirty ? " · draft pending" : "")
    }
    ColumnLayout {
        objectName: "beginnerGuide"; visible: v.mode === "Learn" && v.guide.total !== undefined
        Layout.fillWidth: true; spacing: 8
        LabText { objectName: "guideHeading"; text: "Learn · step " + ((v.guide.index || 0)+1) + " of " + (v.guide.total || 0); font.bold: true; Layout.fillWidth: true }
        LabText { objectName: "guideCommand"; text: v.guide.command || ""; font.family: "monospace"; color: v.palette.accent; Layout.fillWidth: true }
        LabText { objectName: "guideExplanation"; text: v.guide.explanation || ""; Layout.fillWidth: true }
        LabText { objectName: "guideExpected"; text: "Expect: " + (v.guide.expected || ""); color: v.palette.muted; Layout.fillWidth: true }
        LabText { objectName: "guideVerified"; visible: v.guide.verified === true; text: v.guide.completionMessage || "Running status verified. Submit when ready."; color: v.palette.success; Layout.fillWidth: true }
    }
    RowLayout {
        Layout.fillWidth: true
        LabButton {
            id: hint; objectName: "hintButton"; text: "Hint · " + v.hintCount + "/" + v.hintTotal
            KeyNavigation.tab: details
            visible: v.mode === "Learn"; enabled: !v.readOnly && v.hintCount < v.hintTotal
            onClicked: { controller.hint(); Qt.callLater(function(){scrollPanel.ensureVisible(latestHint)}) }
            onActiveFocusChanged: if(activeFocus) scrollPanel.ensureVisible(this)
            ToolTip.visible: hovered; ToolTip.text: "Reveal next hint. No score penalty. Previous hints are in Lab details."
        }
        LabButton { id: details; objectName: "missionDetailsButton"; text: "Lab details ▾"; onClicked: body.detailsRequested(); onActiveFocusChanged: if(activeFocus) scrollPanel.ensureVisible(this) }
    }
    LabText { id: latestHint; objectName: "latestHint"; visible: v.mode === "Learn" && v.hints.length>0; text: v.hints.length ? v.hints[v.hints.length-1] : ""; Layout.fillWidth: true }
    LabText { visible: v.mode === "Challenge"; text: "Challenge · guidance and hints hidden"; color: v.palette.muted; Layout.fillWidth: true; font.pixelSize: 13 }
}
