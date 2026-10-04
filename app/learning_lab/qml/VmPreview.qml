import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: panel; objectName: "vmPreview"
    required property QtObject backend
    property var info: backend.view
    property var session: info.session
    property bool running: ["running","paused","io-error","prelaunch"].indexOf(info.state)>=0
    property string chosenMode: session ? session.mode : "Learn"
    property var returnFocus: null
    title: "Real Linux · optional offline VM preview"
    modal: false; closePolicy: Popup.NoAutoClose
    width: Math.min(parent.width-32,1000); height: Math.min(parent.height-32,850)
    x: (parent.width-width)/2; y: (parent.height-height)/2
    onOpened: backend.refresh()
    onClosed: if(returnFocus) returnFocus.forceActiveFocus()
    Timer { interval: 5000; repeat: true; running: panel.opened; onTriggered: if(!info.busy) backend.refresh() }
    contentItem: InsetScrollView {
        id: contents; objectName: "vmContents"
        LabText { text: info.lesson.title; font.pixelSize: 24; font.bold: true; Layout.fillWidth: true }
        LabText { text: info.lesson.goal; Layout.fillWidth: true }
        LabText { objectName: "vmBoundary"; text: "Use the separate GTK console for real guest commands. No networking, host folders or clipboard; not protection against hostile malware."; Layout.fillWidth: true }
        LabText { objectName: "vmBackupWarning"; text: "VM sessions and disks are NOT included in profile backups or exports. Resume keeps files, not RAM or shell jobs."; Layout.fillWidth: true; font.bold: true }
        LabText { text: "Status: "+info.state+(info.other_profile_running ? " · another profile has the running VM" : "")+(info.busy ? " · operation in progress…" : ""); Layout.fillWidth: true; Accessible.role: Accessible.StaticText }
        LabText { text: info.error || info.message || info.notice; visible: text.length>0; Layout.fillWidth: true; color: info.error ? "#ff9a9a" : palette.text }
        LabText { visible: !info.prerequisites; text: "Preview prerequisites are unavailable: QEMU x86, qemu-img and writable KVM access are required. All simulated labs remain usable. No software will be installed automatically."; Layout.fillWidth: true }
        RowLayout {
            Label { text: "Mode" }
            ComboBox { objectName: "vmMode"; model: ["Learn","Challenge"]; currentIndex: panel.chosenMode==="Learn" ? 0 : 1; enabled: !info.busy && !session; onActivated: panel.chosenMode=currentText }
            LabText { text: session ? "Changing mode starts a new session through Reset." : "Learn offers guidance; Challenge hides it."; Layout.fillWidth: true }
        }
        ColumnLayout {
            visible: !!session && session.mode==="Learn"; Layout.fillWidth: true; spacing: 12
            LabText { text: "Learn step "+((session ? session.step : 0)+1)+" of "+info.lesson.steps.length; font.bold: true; Layout.fillWidth: true }
            TextArea { objectName: "vmCommand"; Layout.fillWidth: true; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.family: "monospace"; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this); text: info.lesson.steps[session ? session.step : 0].command; Accessible.name: "Command to type in the guest console" }
            LabText { text: info.lesson.steps[session ? session.step : 0].explanation; Layout.fillWidth: true }
            LabText { text: "Expected: "+info.lesson.steps[session ? session.step : 0].expected; Layout.fillWidth: true }
            RowLayout {
                LabButton { text: "Previous"; enabled: !info.busy && !!session && session.step>0; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this); onClicked: backend.progress("back") }
                LabButton { objectName: "vmNext"; text: "Next step"; enabled: !info.busy && !!session && session.step<info.lesson.steps.length-1; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this); onClicked: backend.progress("next") }
                LabButton { text: "Hint"; enabled: !info.busy && !!session && session.hints<info.lesson.hints.length; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this); onClicked: backend.progress("hint") }
            }
            Repeater { model: session && session.mode==="Learn" ? info.lesson.hints.slice(0,session.hints) : []; LabText { required property string modelData; text: modelData; Layout.fillWidth: true } }
        }
        LabText { visible: !session || session.mode==="Challenge"; text: info.lesson.challenge; Layout.fillWidth: true }
        LabText { text: "Self-review · no verification score"; font.bold: true; Layout.fillWidth: true }
        Repeater { model: info.lesson.review; LabText { required property string modelData; text: "• "+modelData; Layout.fillWidth: true } }
        LabText { objectName: "vmCompletion"; text: session && session.completion ? "Recorded as self-reviewed on "+session.completion.at+". Guest state was not verified." : "Completion records your own review; the app does not inspect guest commands or results."; Layout.fillWidth: true }
        LabButton { objectName: "vmComplete"; text: "Record my self-review…"; enabled: !!session && !info.busy; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this); onClicked: selfReview.open() }
        LabText { text: "Prepared local image: "+info.image.image_id+". Start checks the full pinned hash. If the image is absent, use the reviewed local preparation/registration recipe in docs/vm-preview/setup.md; this preview has no image downloader."; Layout.fillWidth: true }
        LabText { text: info.lesson.coverage; Layout.fillWidth: true }
        LabText { text: "Disk safety: 18 GiB per-file limit; no aggregate quota or guaranteed free-space reserve. Retained generations are never automatically pruned. Storage monitoring runs while this panel is open. Close the guest with Stop for a clean shutdown."; Layout.fillWidth: true }
        LabText { text: "Closing this panel/app can leave the guest running. Reopen the same profile to control it. Only one preview VM can run for this user, across all profiles."; Layout.fillWidth: true }
    }
    footer: ColumnLayout {
        spacing: 8
        RowLayout {
            Layout.margins: 12; Layout.fillWidth: true
            LabButton { objectName: "vmStart"; text: session ? "Resume disk" : "Start"; enabled: !info.busy && !running && !info.other_profile_running && info.prerequisites && info.state!=="disk-missing" && info.state!=="unclean"; onClicked: backend.start(panel.chosenMode) }
            LabButton { objectName: "vmStop"; text: "Stop"; enabled: !info.busy && running; onClicked: backend.stop() }
            LabButton { objectName: "vmReset"; text: "Reset…"; enabled: !info.busy && !running && !info.other_profile_running; onClicked: resetDialog.open() }
            LabButton { text: "Force stop…"; enabled: !info.busy && running; onClicked: forceDialog.open() }
            Item { Layout.fillWidth: true }
            LabButton { objectName: "vmClose"; text: "Close panel"; enabled: !info.busy; onClicked: panel.close() }
        }
    }
    Dialog {
        id: resetDialog; objectName: "vmResetConfirmation"; title: "Start a fresh VM session?"; modal: true; anchors.centerIn: parent
        width: Math.min(panel.width-40,540); height: 340; standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: ColumnLayout {
            LabText { text: "Stop the VM first. Reset retains the old disk and session for recovery, then creates a fresh disk. Old shell jobs and files will not appear in the new guest. No automatic repair or deletion. VM disks are excluded from profile backups."; Layout.fillWidth: true }
            ComboBox { id: resetMode; model: ["Learn","Challenge"]; Accessible.name: "New session mode" }
        }
        onAccepted: backend.reset(resetMode.currentText,true)
    }
    Dialog {
        id: forceDialog; title: "Force stop this guest?"; modal: true; anchors.centerIn: parent; width: Math.min(panel.width-40,500); height: 260; standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: LabText { text: "This is like cutting power. Unsaved guest work may be lost and the filesystem may be inconsistent. The disk is retained unclean; no repair runs automatically." }
        onAccepted: backend.forceStop(true)
    }
    Dialog {
        id: selfReview; title: "Record self-reviewed completion?"; modal: true; anchors.centerIn: parent; width: Math.min(panel.width-40,500); height: 260; standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: LabText { text: "Confirm that you completed the review above. This records your statement, not a verified guest assessment or score." }
        onAccepted: backend.progress("complete")
    }
}
