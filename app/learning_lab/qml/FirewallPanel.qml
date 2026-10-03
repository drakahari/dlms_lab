import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

LabScrollView {
    id: control
    objectName: "firewallViewport"
    required property QtObject controller
    required property var v
    required property var hostWindow
    required property Item beforePanel
    required property Item afterPanel
    property var focusControls: [defaultPolicyInput, inspectAppliedButton, ruleSelect, ruleIdInput, ruleActionInput, ruleSourceInput, ruleDestinationInput, rulePortInput, moveRuleUp, moveRuleDown, addRule, removeRule]
    function nextFocus(item, direction) {
        var index = focusControls.indexOf(item) + direction
        while (index >= 0 && index < focusControls.length) {
            if (focusControls[index].enabled) return focusControls[index]
            index += direction
        }
        return direction > 0 ? afterPanel : beforePanel
    }
    function navigateShortcut(event) {
        if ((event.modifiers & Qt.AltModifier) && event.key >= Qt.Key_1 && event.key <= Qt.Key_3) {
            controller.navigate(event.key - Qt.Key_1); event.accepted = true
        } else event.accepted = false
    }
    function focusFirst() { defaultPolicyInput.forceActiveFocus(Qt.TabFocusReason) }
    function focusLast() {
        for (var i = focusControls.length - 1; i >= 0; i--) if (focusControls[i].enabled) {
            focusControls[i].forceActiveFocus(Qt.BacktabFocusReason); return
        }
    }
    property var colors: v.palette
    clip: true
    contentWidth: availableWidth
    function ensureVisible(item) {
        if (!item || !contentItem) return
        var parentItem = item
        while (parentItem && parentItem !== contentItem) parentItem = parentItem.parent
        if (!parentItem) return
        var top = item.mapToItem(contentItem.contentItem, 0, 0).y
        var next = contentItem.contentY
        if (top < next) next = top - 8
        if (top + item.height > next + availableHeight) next = top + item.height - availableHeight + 8
        contentItem.contentY = Math.max(0, Math.min(Math.max(0, contentItem.contentHeight - availableHeight), next))
    }
    Connections {
        target: control.hostWindow
        function onActiveFocusItemChanged() { control.ensureVisible(control.hostWindow.activeFocusItem) }
    }
    ColumnLayout {
        width: control.availableWidth
        spacing: 8
        LabText { text: v.firewallDevice + " · draft TCP policy"; font.pixelSize: 23; font.bold: true; Layout.fillWidth: true }
        LabText { text: "First matching rule wins; otherwise the default decides. Draft rules do not affect tests until Apply."; color: colors.muted; Layout.fillWidth: true }
        RowLayout {
            Layout.fillWidth: true
            LabText { text: "Default policy" }
            ComboBox {
                id: defaultPolicyInput; Keys.onPressed: function(event) { control.navigateShortcut(event) }; objectName: "defaultPolicyInput";
                KeyNavigation.tab: control.nextFocus(defaultPolicyInput, 1); KeyNavigation.backtab: control.nextFocus(defaultPolicyInput, -1); model: ["deny", "allow"]
                currentIndex: model.indexOf(v.draftDefault)
                enabled: !v.readOnly; Accessible.name: "Draft default TCP policy"
                onActivated: controller.editDefault(currentText)
                Layout.minimumWidth: 110
            }
            Item { Layout.fillWidth: true }
            LabButton { id: inspectAppliedButton; KeyNavigation.tab: control.nextFocus(inspectAppliedButton, 1); KeyNavigation.backtab: control.nextFocus(inspectAppliedButton, -1); objectName: "inspectAppliedPolicy"; text: "Inspect Applied policy"; onClicked: appliedDialog.open() }
        }
        ComboBox {
            id: ruleSelect; Keys.onPressed: function(event) { control.navigateShortcut(event) }; objectName: "ruleSelect";
                KeyNavigation.tab: control.nextFocus(ruleSelect, 1); KeyNavigation.backtab: control.nextFocus(ruleSelect, -1); Layout.fillWidth: true; model: v.ruleChoices
            currentIndex: v.ruleCount > 0 ? v.ruleIndex : -1
            enabled: v.ruleCount > 0; Accessible.name: "Ordered draft rule selection"
            onActivated: controller.selectRule(currentIndex)
        }
        GridLayout {
            columns: control.availableWidth < 720 ? 2 : 4; columnSpacing: 12; rowSpacing: 8; Layout.fillWidth: true
            LabText { text: "Rule ID" }
            TextField {
                id: ruleIdInput; objectName: "ruleIdInput";
                KeyNavigation.tab: control.nextFocus(ruleIdInput, 1); KeyNavigation.backtab: control.nextFocus(ruleIdInput, -1); text: v.ruleInputs.id; maximumLength: 32
                Layout.fillWidth: true; Layout.minimumWidth: 180; enabled: !v.readOnly && v.ruleCount > 0
                Accessible.name: "Draft rule ID"; onTextEdited: controller.editRule("id", text)
            }
            LabText { text: "Action" }
            ComboBox {
                id: ruleActionInput; Keys.onPressed: function(event) { control.navigateShortcut(event) }; objectName: "ruleActionInput";
                KeyNavigation.tab: control.nextFocus(ruleActionInput, 1); KeyNavigation.backtab: control.nextFocus(ruleActionInput, -1); model: ["deny", "allow"]; currentIndex: model.indexOf(v.ruleInputs.action)
                Layout.fillWidth: true; Layout.minimumWidth: 180; enabled: !v.readOnly && v.ruleCount > 0
                Accessible.name: "Draft rule action"; onActivated: controller.editRule("action", currentText)
            }
            LabText { text: "Source" }
            TextField {
                id: ruleSourceInput; objectName: "ruleSourceInput";
                KeyNavigation.tab: control.nextFocus(ruleSourceInput, 1); KeyNavigation.backtab: control.nextFocus(ruleSourceInput, -1); text: v.ruleInputs.source; maximumLength: 64
                Layout.fillWidth: true; Layout.minimumWidth: 180; enabled: !v.readOnly && v.ruleCount > 0
                Accessible.name: "Draft rule source IPv4 selector"; onTextEdited: controller.editRule("source", text)
            }
            LabText { text: "Destination" }
            TextField {
                id: ruleDestinationInput; objectName: "ruleDestinationInput";
                KeyNavigation.tab: control.nextFocus(ruleDestinationInput, 1); KeyNavigation.backtab: control.nextFocus(ruleDestinationInput, -1); text: v.ruleInputs.destination; maximumLength: 64
                Layout.fillWidth: true; Layout.minimumWidth: 180; enabled: !v.readOnly && v.ruleCount > 0
                Accessible.name: "Draft rule destination IPv4 selector"; onTextEdited: controller.editRule("destination", text)
            }
            LabText { text: "Port" }
            TextField {
                id: rulePortInput; objectName: "rulePortInput";
                KeyNavigation.tab: control.nextFocus(rulePortInput, 1); KeyNavigation.backtab: control.nextFocus(rulePortInput, -1); text: v.ruleInputs.port; maximumLength: 5
                Layout.fillWidth: true; Layout.minimumWidth: 180; enabled: !v.readOnly && v.ruleCount > 0
                Accessible.name: "Draft rule TCP destination port"; onTextEdited: controller.editRule("port", text)
            }
            LabText { text: "Protocol" }
            LabText { text: "TCP (fixed)"; Layout.fillWidth: true }
        }
        RowLayout {
            Layout.fillWidth: true
            LabButton { id: moveRuleUp; objectName: "moveRuleUp";
                KeyNavigation.tab: control.nextFocus(moveRuleUp, 1); KeyNavigation.backtab: control.nextFocus(moveRuleUp, -1); text: "Move up"; enabled: !v.readOnly && v.ruleIndex > 0; onClicked: controller.moveRule(-1) }
            LabButton { id: moveRuleDown; objectName: "moveRuleDown";
                KeyNavigation.tab: control.nextFocus(moveRuleDown, 1); KeyNavigation.backtab: control.nextFocus(moveRuleDown, -1); text: "Move down"; enabled: !v.readOnly && v.ruleIndex + 1 < v.ruleCount; onClicked: controller.moveRule(1) }
            LabButton { id: addRule; objectName: "addRule";
                KeyNavigation.tab: control.nextFocus(addRule, 1); KeyNavigation.backtab: control.nextFocus(addRule, -1); text: "Add rule"; enabled: !v.readOnly && v.ruleCount < 16; onClicked: controller.addRule() }
            LabButton { id: removeRule; objectName: "removeRule";
                KeyNavigation.tab: control.nextFocus(removeRule, 1); KeyNavigation.backtab: control.nextFocus(removeRule, -1); text: "Remove rule"; enabled: !v.readOnly && v.ruleCount > 0; onClicked: controller.removeRule() }
        }
        LabText { text: "Selectors: IPv4 host, canonical CIDR or any. Port: 1–65535 or any. All rules match TCP only; ICMP and DNS are unaffected."; Layout.fillWidth: true; color: colors.muted }
        LabText { objectName: "appliedPolicySummary"; text: "APPLIED · default " + (v.hasFirewall ? v.applied.firewall.default : "deny") + " · " + (v.hasFirewall ? v.applied.firewall.rules.length : 0) + " rules. Inspect Applied policy to compare."; Layout.fillWidth: true; font.bold: true; color: v.firewallDirty ? colors.danger : colors.accent }
    }
    Dialog {
        id: appliedDialog; objectName: "appliedPolicyDialog"
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(740, control.hostWindow.width - 60)
        height: Math.min(500, control.hostWindow.height - 100)
        modal: true; title: "Applied TCP rules · revision " + v.revision
        closePolicy: Popup.CloseOnEscape
        contentItem: LabScrollView {
            clip: true
            TextArea {
                objectName: "appliedPolicyText"; text: v.appliedPolicy
                textFormat: TextEdit.PlainText; readOnly: true; wrapMode: TextEdit.Wrap
                font.family: "monospace"; font.pixelSize: 14
            }
        }
        standardButtons: Dialog.Close
        onClosed: inspectAppliedButton.forceActiveFocus()
    }
}
