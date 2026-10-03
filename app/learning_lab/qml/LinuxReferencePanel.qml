import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: reference; objectName: "labDetailsView"
    required property var v
    signal closeRequested()
    property string currentLab: v.labKey
    onCurrentLabChanged: Qt.callLater(function(){detailsScroll.contentItem.contentY=0})
    property alias firstControl: collapse
    onVisibleChanged: if(visible) Qt.callLater(function(){collapse.forceActiveFocus()})
    color: v.palette.surface; radius: 7
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 10; spacing: 10
        RowLayout {
            Layout.fillWidth: true
            LabButton { id: collapse; objectName: "missionDetailsButton"; text: "Lab details ▾"; Accessible.name: "Collapse Lab details"; onClicked: reference.closeRequested() }
            Item { Layout.fillWidth: true }
            LabButton { objectName: "closeLabDetails"; text: "Close"; implicitWidth: 60; onClicked: reference.closeRequested() }
        }
        LabScrollView {
            id: detailsScroll; objectName: "labDetailsScroll"; Layout.fillWidth: true; Layout.fillHeight: true
            clip: true; contentWidth: availableWidth
            ColumnLayout {
                width: detailsScroll.availableWidth; spacing: 14
                LabText { text: v.missionGoal || ""; font.bold: true; Layout.fillWidth: true }
                LabText { objectName: "missionBrief"; text: v.metadata.brief; Layout.fillWidth: true }
                LabText { text: "Objectives"; font.bold: true }
                Repeater { model: v.objectives; LabText { required property var modelData; text: "• " + modelData.label + " · " + modelData.points + " pts"; Layout.fillWidth: true } }
                LabText { text: "Constraints"; font.bold: true }
                Repeater { model: v.constraints; LabText { required property string modelData; text: "• " + modelData; Layout.fillWidth: true } }
                LabText { text: "Simulation limitations"; font.bold: true }
                LabText { text: v.simulationNotice; Layout.fillWidth: true }
                LabText { visible: v.mode === "Learn"; text: "Revealed hints · no score penalty"; font.bold: true }
                Repeater { model: v.mode === "Learn" ? v.hints : []; LabText { required property string modelData; required property int index; objectName: "revealedDetailHint" + index; text: (index+1) + ". " + modelData; Layout.fillWidth: true } }
            }
        }
    }
}
