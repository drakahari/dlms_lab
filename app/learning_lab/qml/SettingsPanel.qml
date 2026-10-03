import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

LabScrollView {
    id: panel; objectName: "settingsViewport"
    required property var v
    required property QtObject controller
    required property Item beforePanel
    required property Item afterPanel
    function nextField(index, direction) {
        for(var i=index+direction;i>=0 && i<fields.count;i+=direction) {
            var control=fields.itemAt(i).inputControl
            if(control.enabled && !control.readOnly) return control
        }
        return direction>0 ? afterPanel : beforePanel
    }
    function focusFirst() { nextField(-1,1).forceActiveFocus(Qt.TabFocusReason) }
    clip: true; contentWidth: availableWidth
    function keepVisible(item) {
        var point=item.mapToItem(contentItem.contentItem,0,0)
        contentItem.contentY=Math.max(0,Math.min(contentItem.contentHeight-availableHeight,point.y+item.height-availableHeight+12))
    }
    ColumnLayout {
        width: panel.availableWidth; spacing: 8
        LabText { text: v.sourceDevice + " settings"; font.bold: true; Layout.fillWidth: true }
        GridLayout {
            columns: panel.availableWidth >= 620 ? 2 : 1
            Layout.fillWidth: true; columnSpacing: 18; rowSpacing: 10
            Repeater {
                id: fields
                model: [{key:"address",label:"IPv4 address",applied:"Address"},{key:"prefix",label:"Prefix or subnet mask",applied:"Prefix"},{key:"gateway",label:"Default gateway",applied:"Gateway"},{key:"dns",label:"DNS server",applied:"Dns"}]
                ColumnLayout {
                    required property var modelData
                    required property int index
                    property alias inputControl: input
                    Layout.fillWidth: true; spacing: 4
                    LabText { text: modelData.label + (v.editable.indexOf(modelData.key)<0 ? " (fixed)" : " · Draft"); Layout.fillWidth: true }
                    TextField {
                        id: input
                        KeyNavigation.tab: panel.nextField(index,1)
                        KeyNavigation.backtab: panel.nextField(index,-1)
                        objectName: modelData.key+"Input"
                        Layout.fillWidth: true; maximumLength: 128
                        text: v.inputs[modelData.key]; readOnly: v.editable.indexOf(modelData.key)<0
                        enabled: !v.readOnly; activeFocusOnTab: !readOnly
                        Accessible.name: modelData.label + " draft"
                        onTextEdited: controller.edit(modelData.key,text)
                        onActiveFocusChanged: if(activeFocus) panel.keepVisible(parent)
                    }
                    LabText { objectName: "applied"+modelData.applied; text: "Applied: " + (modelData.key==="prefix" ? "/" : "") + v.applied[modelData.key]; font.family: "monospace"; color: v.palette.accent; Layout.fillWidth: true }
                }
            }
        }
        LabText { text: "Prefixes accept 24, /24, or a contiguous subnet mask. Invalid values remain draft until corrected."; color: v.palette.muted; Layout.fillWidth: true }
    }
}
