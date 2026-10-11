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
    property string selectedLessonId: info.selected_lesson_id
    // QVariant views are rebuilt on every status poll. Only replace navigation
    // models when their actual IDs/titles change, preserving popup highlight.
    property string unitOptionsKey: JSON.stringify(info.units || [])
    property string lessonOptionsKey: JSON.stringify(info.choices || [])
    property var unitOptions: JSON.parse(unitOptionsKey)
    property var lessonOptions: JSON.parse(lessonOptionsKey)
    readonly property bool navigationEnabled: !info.busy || info.refreshing === true
    readonly property bool vmSelectionValid: {
        if(!info.lesson || info.lesson.id!==info.selected_lesson_id) return false
        for(var i=0;i<lessonOptions.length;i++)
            if(lessonOptions[i].id===info.selected_lesson_id) return true
        return false
    }
    function chooseUnit(index) {
        if(!navigationEnabled || index<0 || index>=unitOptions.length) return
        var id=unitOptions[index].id
        for(var i=0;i<(info.units || []).length;i++)
            if(info.units[i].id===id) { backend.selectUnit(id); return }
    }
    function chooseLesson(index) {
        if(!navigationEnabled || index<0 || index>=lessonOptions.length) return
        var id=lessonOptions[index].id
        for(var i=0;i<(info.choices || []).length;i++)
            if(info.choices[i].id===id) { backend.selectLesson(id); return }
    }
    onSelectedLessonIdChanged: Qt.callLater(function() {
        // A delayed top reset must not scroll newly focused navigation away.
        var choice=unitChoice.activeFocus ? unitChoice : lessonChoice.activeFocus ? lessonChoice : modeChoice.activeFocus ? modeChoice : null
        if(choice) contents.ensureVisible(choice)
        else if(contents.contentItem) contents.contentItem.contentY=0
        supportToggle.checked=false
    })
    property bool anyRunning: !!info.running_lesson_id || info.other_profile_running
    onSessionChanged: chosenMode=session ? session.mode : "Learn"
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
        LabText { text: "Choose a collection, then a lesson and mode. Start opens the separate real-Linux guest console. Selecting a lesson does not start a VM. Simulator activities remain in the Library."; Layout.fillWidth: true }
        Label { text: "1. Collection · a group of real-VM lessons"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        LabChoice {
            id: unitChoice; objectName: "vmUnitChoice"; Layout.fillWidth: true; model: panel.unitOptions; textRole: "title"
            currentIndex: { for(var i=0;i<panel.unitOptions.length;i++) if(panel.unitOptions[i].id===info.unit.id) return i; return -1 }
            enabled: panel.navigationEnabled && count>0; Accessible.name: "Choose a real-Linux collection"
            onActiveFocusChanged: if(activeFocus && focusReason!==Qt.MouseFocusReason) contents.ensureVisible(this)
            onActivated: function(index) { panel.chooseUnit(index) }
        }
        LabText { text: info.unit.title; font.bold: true; Layout.fillWidth: true }
        LabText { text: info.unit.purpose; Layout.fillWidth: true }
        Label { text: "2. Lesson in this collection ("+panel.lessonOptions.length+")"; Layout.fillWidth: true; wrapMode: Text.WordWrap }
        LabChoice {
            id: lessonChoice; objectName: "vmLessonChoice"; Layout.fillWidth: true; model: panel.lessonOptions; textRole: "title"
            currentIndex: { for(var i=0;i<panel.lessonOptions.length;i++) if(panel.lessonOptions[i].id===info.selected_lesson_id) return i; return -1 }
            enabled: panel.navigationEnabled && count>0; Accessible.name: "Choose a real-Linux lesson"
            onActiveFocusChanged: if(activeFocus && focusReason!==Qt.MouseFocusReason) contents.ensureVisible(this)
            onActivated: function(index) { panel.chooseLesson(index) }
        }
        LabText { objectName: "vmRunningLesson"; visible: !!info.running_lesson_id; text: "Running lesson: "+info.running_title+" · "+info.running_state+". Stop below controls this guest, even when another lesson is selected."; Layout.fillWidth: true; font.bold: true }
        LabButton { objectName: "vmReturnRunning"; visible: !!info.running_lesson_id && info.running_lesson_id!==info.selected_lesson_id; text: "Return to running lesson"; enabled: !info.busy; onClicked: backend.selectLesson(info.running_lesson_id) }
        LabText { visible: info.other_profile_running; text: "A VM belonging to another application profile/store is running. Stop it from that profile before starting this lesson."; Layout.fillWidth: true }
        LabText { visible: !!info.running_error; text: info.running_error; Layout.fillWidth: true }
        LabText { text: info.lesson.goal; Layout.fillWidth: true }
        LabText { visible: !!info.support.materials; text: "Practice setup and supplied data · available in both modes"; font.bold: true; Layout.fillWidth: true }
        Repeater { model: info.support.materials || []; TextArea { objectName: "vmPracticeMaterial"; required property string modelData; Layout.fillWidth: true; readOnly: true; selectByMouse: true; wrapMode: TextEdit.Wrap; font.family: "monospace"; text: modelData; Accessible.name: "Guest-local practice setup and data"; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this) } }
        LabText { objectName: "vmBoundary"; text: "Use the separate GTK console for real guest commands. No networking, host folders or clipboard; not protection against hostile malware."; Layout.fillWidth: true }
        LabText { objectName: "vmDisplayGuidance"; text: "Console view: keep View → Zoom To Fit enabled beside the Lab. For manual zoom, use a sufficiently large floating window; undersized tiles can distort the console and menu targets. Reopening returns to fit. The manual zoom percentage is not saved."; Layout.fillWidth: true }
        LabText { objectName: "vmBackupWarning"; text: "VM sessions and disks are NOT included in profile backups or exports. Resume keeps files, not RAM or shell jobs."; Layout.fillWidth: true; font.bold: true }
        LabText { text: "Status: "+info.state+(info.other_profile_running ? " · another profile has the running VM" : "")+(info.busy ? " · operation in progress…" : ""); Layout.fillWidth: true; Accessible.role: Accessible.StaticText }
        LabText { text: info.error || info.message || info.notice; visible: text.length>0; Layout.fillWidth: true; color: info.error ? "#ff9a9a" : palette.text }
        LabText { visible: !info.prerequisites; text: "Preview prerequisites are unavailable: QEMU x86, qemu-img and writable KVM access are required. All simulated labs remain usable. No software will be installed automatically."; Layout.fillWidth: true }
        RowLayout {
            Label { text: "3. Mode" }
            LabChoice { id: modeChoice; objectName: "vmMode"; model: ["Learn","Challenge"]; currentIndex: panel.chosenMode==="Learn" ? 0 : 1; enabled: panel.navigationEnabled && !session; onActiveFocusChanged: if(activeFocus && focusReason!==Qt.MouseFocusReason) contents.ensureVisible(this); onActivated: panel.chosenMode=currentText }
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
        LabText { visible: !!info.support.observations; text: "Observations to retain"; font.bold: true; Layout.fillWidth: true }
        Repeater { model: info.support.observations || []; LabText { required property string modelData; text: "• "+modelData; Layout.fillWidth: true } }
        LabText { objectName: "vmInterpretationHeading"; visible: !!info.support.questions; text: "Interpretation questions"; font.bold: true; Layout.fillWidth: true }
        Repeater { model: info.support.questions || []; LabText { required property string modelData; text: modelData; Layout.fillWidth: true } }
        Repeater { model: info.support.limitations || []; LabText { required property string modelData; text: "Limit: "+modelData; Layout.fillWidth: true } }
        Repeater { model: info.lesson.review; LabText { required property string modelData; text: "• "+modelData; Layout.fillWidth: true } }
        LabText { objectName: "vmCompletion"; text: session && session.completion ? "Recorded as self-reviewed on "+session.completion.at+". Guest state was not verified." : "Completion records your own review; the app does not inspect guest commands or results."; Layout.fillWidth: true }
        LabButton { objectName: "vmComplete"; text: "Record my self-review…"; enabled: !!session && !info.busy; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this); onClicked: selfReview.open() }
        LabText { text: "Prepared local image: "+info.image.image_id+". Start checks the full pinned hash. If the image is absent, use the reviewed local preparation/registration recipe in docs/vm-preview/setup.md; this preview has no image downloader."; Layout.fillWidth: true }
        LabText { text: info.lesson.coverage; Layout.fillWidth: true }
        LabText { text: info.unit.coverage; Layout.fillWidth: true }
        LabText { text: "Prerequisites: "+info.unit.prerequisites; Layout.fillWidth: true }
        CheckBox { id: supportToggle; objectName: "vmSupportToggle"; text: "Troubleshooting and cleanup"; Accessible.name: text; onActiveFocusChanged: if(activeFocus) contents.ensureVisible(this) }
        ColumnLayout {
            visible: supportToggle.checked; Layout.fillWidth: true; spacing: 12
            LabText { text: "Before signaling, inspect the actual owner, arguments and PID again. Use bounded owned practice tasks. Saved PIDs can expire or be reused. Finish practice tasks before leaving a lesson. Closing GTK can be an unclean VM stop."; Layout.fillWidth: true }
            Repeater { model: session && session.mode==="Learn" ? info.support.troubleshooting : []; LabText { required property string modelData; text: modelData; Layout.fillWidth: true } }
            Repeater { model: info.support.observations || (session && session.mode==="Learn") ? info.support.cleanup : []; LabText { required property string modelData; text: "Cleanup: "+modelData; Layout.fillWidth: true } }
        }
        LabText { text: "Disk safety: 18 GiB per-file limit; no aggregate quota or guaranteed free-space reserve. Retained generations are never automatically pruned. Storage monitoring runs while this panel is open. Close the guest with Stop for a clean shutdown."; Layout.fillWidth: true }
        LabText { text: "Closing this panel/app can leave the guest running. Reopen the same profile to control it. Only one preview VM can run for this user, across all profiles."; Layout.fillWidth: true }
    }
    footer: ColumnLayout {
        spacing: 8
        LabText { objectName: "vmSelectedSummary"; text: vmSelectionValid ? "Selected real-VM lesson: "+info.lesson.title+"\n"+info.unit.title+" · "+panel.chosenMode+" · self-reviewed, unscored" : "Choose an available lesson before starting."; Layout.fillWidth: true; Layout.leftMargin: 12; Layout.rightMargin: 12; font.bold: true }
        LabText { text: "4. Start or resume the selected lesson"; Layout.fillWidth: true; Layout.leftMargin: 12; Layout.rightMargin: 12 }
        RowLayout {
            Layout.margins: 12; Layout.fillWidth: true
            LabButton { objectName: "vmStart"; text: session ? "Resume disk" : "Start"; enabled: panel.vmSelectionValid && !info.busy && !anyRunning && info.prerequisites && info.state!=="disk-missing" && info.state!=="unclean" && info.state!=="session-unavailable" && info.state!=="control-unavailable"; onClicked: backend.start(panel.chosenMode) }
            LabButton { objectName: "vmStop"; text: "Stop running"; enabled: !info.busy && !!info.running_lesson_id; onClicked: backend.stop() }
            LabButton { objectName: "vmReset"; text: "Reset…"; enabled: panel.vmSelectionValid && !info.busy && !anyRunning && info.state!=="control-unavailable"; onClicked: resetDialog.open() }
            LabButton { text: "Force stop…"; enabled: !info.busy && !!info.running_lesson_id; onClicked: forceDialog.open() }
            Item { Layout.fillWidth: true }
            LabButton { objectName: "vmClose"; text: "Close panel"; enabled: !info.busy; onClicked: panel.close() }
        }
    }
    Dialog {
        id: resetDialog; objectName: "vmResetConfirmation"; title: "Start a fresh selected-lesson session?"; modal: true; anchors.centerIn: parent
        width: Math.min(panel.width-40,540); height: 340; standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: ColumnLayout {
            LabText { text: "Reset applies to the selected lesson only. Stop the VM first. Reset retains the old disk and session for recovery, then creates a fresh disk. Old shell jobs and files will not appear in the new guest. No automatic repair or deletion. VM disks are excluded from profile backups."; Layout.fillWidth: true }
            LabChoice { id: resetMode; model: ["Learn","Challenge"]; Accessible.name: "New session mode" }
        }
        onAccepted: backend.reset(resetMode.currentText,true)
    }
    Dialog {
        id: forceDialog; title: "Force stop the running guest?"; modal: true; anchors.centerIn: parent; width: Math.min(panel.width-40,500); height: 260; standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: LabText { text: "This is like cutting power. Unsaved guest work may be lost and the filesystem may be inconsistent. The disk is retained unclean; no repair runs automatically." }
        onAccepted: backend.forceStop(true)
    }
    Dialog {
        id: selfReview; title: "Record self-reviewed completion?"; modal: true; anchors.centerIn: parent; width: Math.min(panel.width-40,500); height: 260; standardButtons: Dialog.Ok | Dialog.Cancel
        contentItem: LabText { text: "Confirm that you completed the review above. This records your statement, not a verified guest assessment or score." }
        onAccepted: backend.progress("complete")
    }
}
