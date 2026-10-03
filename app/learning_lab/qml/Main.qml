import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs as FileDialogs

ApplicationWindow {
    id: window; objectName: "labWindow"
    required property QtObject controller
    property var v: controller.view
    property var colors: v.palette
    property bool linux: v.workspaceKind === "linux-service"
    property var linuxWork: linuxLoader.item
    property var consoleControl: linux && linuxWork ? linuxWork.consoleControl : dock.firstControl
    property bool compact: width < 1000
    property int workspaceMinimumHeight: compact ? (v.workspaceKind === "linux-service" ? 140 : 160) : 200
    property bool linuxDetailsOpen: false
    property bool reviewing: false
    property bool historyAll: false
    property string activeLab: v.labKey
    property string pendingMode: ""
    property string pendingLab: ""
    property int pendingPage: 1
    property var removalEntry: ({})
    property string resumeKey: ""
    property var resumeChoices: []
    property int resumeIndex: -1
    property bool showHidden: false
    property string restoreArchive: ""
    property string exportAttemptId: ""
    property var returnFocus: null
    property bool discardFailedSave: false
    onActiveLabChanged: { reviewing=false; Qt.callLater(function(){ if(v.page===1) { if(linux) linuxWork.focusTerminal(); else workspace.forceActiveFocus() } }) }
    visible: true; width: 1280; height: 900; minimumWidth: 800; minimumHeight: 600
    title: (v.page===0 ? "Lab library" : v.page===2 ? "Attempt history" : v.metadata.title) + " — Omarchy Learning Lab"
    color: colors.background; font.family: "sans-serif"; font.pixelSize: 14
    palette.window: colors.background; palette.base: colors.background; palette.alternateBase: colors.surface
    palette.windowText: colors.foreground; palette.text: colors.foreground; palette.button: colors.surface
    palette.buttonText: colors.foreground; palette.highlight: colors.accent; palette.highlightedText: colors.background; palette.mid: colors.muted
    onActiveChanged: if(active) controller.refreshTheme()
    onClosing: function(close) { controller.flush(); if(v.canRetry && !discardFailedSave) { close.accepted=false; failedSave.open() } }
    function navigate(page) { if(!controller.navigate(page)) return; Qt.callLater(function(){ if(page===0) library.forceActiveFocus(); else if(page===1) mission.forceActiveFocus(); else history.forceActiveFocus() }) }
    function openLab(key, origin, page) {
        pendingPage=page===undefined ? 1 : page
        if(key!==v.labKey && v.dirty) { pendingLab=key;returnFocus=origin;switchDialog.open() }
        else if(pendingPage===2) controller.viewHistory(key,false)
        else controller.selectLab(key,false)
    }
    function restoreAndResume(key, origin) {
        resumeKey=key; returnFocus=origin; resumeChoices=controller.resumableAttempts(key)
        resumeIndex=resumeChoices.length===1 ? 0 : -1
        resumeLibraryDialog.open()
    }
    function libraryAction(entry, action, origin) {
        if(action==='history') { openLab(entry.labKey,origin,2); return }
        if(action==='remove') { removalEntry=entry; returnFocus=origin; removeLibraryDialog.open(); return }
        controller.setLibraryState(entry.labKey,action==='hide' ? 'hidden' : 'active',false)
        Qt.callLater(function(){ showHiddenControl.forceActiveFocus() })
    }
    function rememberLayout() { var sizes=Object.assign({},v.workspaceLayout); sizes.mission_width=Math.round(compact ? (v.workspaceLayout.mission_width || 280) : mission.width); sizes.mission_height=Math.round(compact ? mission.height : (v.workspaceLayout.mission_height || 96)); if(!linux) sizes.dock_height=Math.round(dock.height); controller.saveLayout(sizes) }
    function restoreFocus() { if(returnFocus && returnFocus.visible) returnFocus.forceActiveFocus(); else mission.forceActiveFocus() }
    function restart(mode, origin) { pendingMode=mode;returnFocus=origin;restartDialog.open() }
    Shortcut { sequence: "Alt+1"; onActivated: window.navigate(0) }
    Shortcut { sequence: "Alt+2"; onActivated: window.navigate(1) }
    Shortcut { sequence: "Alt+3"; onActivated: window.navigate(2) }
    function focusRegion(direction) {
        var panels=linux ? [mission,reviewing ? review : linuxWork.toolsRegion,linuxWork.terminalRegion] : [mission,reviewing ? review : workspace,dock]; var index=-1
        var item=window.activeFocusItem
        while(item) { var found=panels.indexOf(item); if(found>=0) {index=found;break} item=item.parent }
        for(var step=1;step<=panels.length;step++) {
            var target=panels[(index+direction*step+panels.length*2)%panels.length]
            if(target.visible) {target.forceActiveFocus(Qt.TabFocusReason);return}
        }
    }
    Shortcut { sequence: "F6"; onActivated: window.focusRegion(1) }
    Shortcut { sequence: "Shift+F6"; onActivated: window.focusRegion(-1) }
    ColumnLayout {
        anchors.fill: parent; anchors.margins: compact ? 12 : 18; spacing: 8
        RowLayout {
            Layout.fillWidth: true
            LabText { text: "OMARCHY LEARNING LAB"; color: colors.accent; font.bold: true; Layout.fillWidth: true }
            LabButton { objectName: "libraryNav"; text: "Library"; highlighted: v.page===0; onClicked: window.navigate(0) }
            LabButton { objectName: "labNav"; text: "Current Lab"; highlighted: v.page===1; onClicked: window.navigate(1) }
            LabButton { objectName: "historyNav"; text: "History"; highlighted: v.page===2; onClicked: window.navigate(2) }
            CheckBox { objectName: "fallbackTheme"; text: "Built-in colors"; checked: v.fallback; onToggled: controller.fallbackTheme(checked) }
        }
        StackLayout {
            currentIndex: v.page; Layout.fillWidth: true; Layout.fillHeight: true
            InsetScrollView {
                id: library; objectName: "libraryPage"
                LabText { objectName: "pageHeading"; text: "Lab library"; font.pixelSize: 27; font.bold: true; Layout.fillWidth: true }
                LabText { text: window.showHidden ? "Showing hidden built-ins and removed imports. Uncheck Show hidden / removed to return to the active Library." : "Original, offline learning simulations. Choose a scenario to begin or resume."; color: colors.muted; Layout.fillWidth: true }
                RowLayout {
                    Layout.fillWidth: true
                    CheckBox {
                        id: showHiddenControl; objectName: "showHiddenControl"
                        text: "Show hidden / removed ("+(v.hiddenCount+v.removedCount)+")"
                        checked: window.showHidden; onToggled: window.showHidden=checked
                        onActiveFocusChanged: if(activeFocus) library.ensureVisible(this)
                    }
                    Item { Layout.fillWidth: true }
                    LabButton { objectName: "restoreVisibilityButton"; text: "Restore visibility"; visible: v.hiddenCount>0; enabled: !v.libraryChoicesReadOnly; onClicked: { controller.restoreVisibility(); showHiddenControl.forceActiveFocus() } }
                }
                RowLayout {
                    LabButton { id: createLabButton; objectName: "createLabButton"; text: "Create a lab…"; onClicked: authoringPanel.open(); onActiveFocusChanged: if(activeFocus) library.ensureVisible(this) }
                    LabButton { objectName: "importPackButton"; text: "Import scenario…"; onClicked: importDialog.open() }
                    LabText { text: "Self-contained .lab.json files · data only"; color: colors.muted; Layout.fillWidth: true }
                }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 4
                    RowLayout {
                        LabButton { objectName: "backupProfileButton"; text: "Backup profile…"; onClicked: { returnFocus=this; backupProfileDialog.open() } }
                        LabButton { objectName: "restoreProfileButton"; text: "Restore profile…"; onClicked: { returnFocus=this; restoreArchiveDialog.open() } }
                    }
                    LabText { text: "Restorable personal backup, separate from scenario/history exports. Backup briefly pauses actions to save consistently."; color: colors.muted; Layout.fillWidth: true }
                }
                LabText { visible: !window.showHidden; text: "Linux Fundamentals"; objectName: "fundamentalsHeading"; font.pixelSize: 22; font.bold: true; Layout.fillWidth: true }
                LabText { visible: !window.showHidden; text: v.fundamentals.length ? "A suggested path through six short labs. Start anywhere; no completion prerequisites." + (v.hiddenCount ? " Hidden entries are available with Show hidden / removed." : "") : "This collection is unavailable. Existing labs remain below."; color: colors.muted; Layout.fillWidth: true }
                Repeater {
                    model: window.showHidden ? [] : v.visibleFundamentals
                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        objectName: "fundamentalsCard-"+modelData.order
                        Layout.fillWidth: true; implicitHeight: collectionCard.implicitHeight+2*library.contentInset
                        color: colors.surface; radius: 8
                        RowLayout {
                            id: collectionCard; anchors.fill: parent; anchors.margins: library.contentInset; spacing: 12
                            ColumnLayout {
                                Layout.fillWidth: true; spacing: 4
                                LabText { text: (modelData.order+1)+". "+modelData.title; font.bold: true; Layout.fillWidth: true }
                                LabText { text: modelData.skill; color: colors.muted; Layout.fillWidth: true }
                                LabText { text: modelData.status; visible: text.length>0; Layout.fillWidth: true }
                                LabText { text: modelData.problem; visible: text.length>0; color: colors.danger; Layout.fillWidth: true }
                            }
                            LabButton { objectName: "start-fundamentals-"+modelData.order; text: modelData.action; enabled: modelData.available; onActiveFocusChanged: if(activeFocus) library.ensureVisible(parent.parent); onClicked: window.openLab(modelData.labKey,this) }
                            LibraryActions {
                                objectName: "actions-fundamentals-"+modelData.order
                                entry: modelData; readOnly: v.libraryChoicesReadOnly; hasHistory: modelData.hasHistory; viewport: library
                                onChoose: function(action) { window.libraryAction(modelData,action,this) }
                            }
                        }
                    }
                }
                LabText { visible: !window.showHidden; text: "Networking and other scenarios"; font.pixelSize: 22; font.bold: true; Layout.fillWidth: true }
                Repeater {
                    model: window.showHidden ? 0 : v.otherLabs.length
                    delegate: Rectangle {
                        required property int index
                        property var info: v.otherLabs[index]
                        Layout.fillWidth: true; implicitHeight: card.implicitHeight+2*library.contentInset
                        color: colors.surface; radius: 8
                        ColumnLayout {
                            id: card; anchors.fill: parent; anchors.margins: library.contentInset; spacing: 7
                            LabText { text: info.metadata.title; font.pixelSize: 22; font.bold: true; Layout.fillWidth: true }
                            LabText { text: info.origin + " · v" + info.version + " · " + info.metadata.topic + " · " + info.metadata.minutes + " minutes"; color: colors.muted; Layout.fillWidth: true }
                            RowLayout {
                                LabButton { objectName: "open-"+info.labKey; onActiveFocusChanged: if(activeFocus) library.ensureVisible(parent.parent.parent); text: "Open lab"; onClicked: window.openLab(info.labKey,this) }
                                LabText { text: info.libraryStatus + " · Best: " + info.libraryBest + " · " + info.historyCount + " prior attempts"; Layout.fillWidth: true }
                                LibraryActions {
                                    objectName: "actions-"+info.labKey; entry: info
                                    readOnly: v.libraryChoicesReadOnly; hasHistory: true; viewport: library
                                    onChoose: function(action) { window.libraryAction(info,action,this) }
                                }
                            }
                        }
                    }
                }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: library.contentInset; visible: window.showHidden
                    LabText { text: "Hidden and removed"; font.pixelSize: 22; font.bold: true; Layout.fillWidth: true }
                    LabText { text: "Nothing is deleted. Restore a lab before practicing, or view its saved history here. Restore visibility shows all hidden built-in labs; removed imports are restored individually."; Layout.fillWidth: true }
                    LabText { text: "No hidden or removed labs."; visible: !v.inactiveLabs.length; Layout.fillWidth: true }
                    Repeater {
                        model: v.inactiveLabs
                        delegate: Rectangle {
                            required property var modelData
                            objectName: "inactive-"+modelData.labKey
                            Layout.fillWidth: true; implicitHeight: inactiveCard.implicitHeight+2*library.contentInset
                            color: colors.surface; radius: 8
                            ColumnLayout {
                                id: inactiveCard; anchors.fill: parent; anchors.margins: library.contentInset; spacing: 8
                                LabText { text: modelData.metadata.title; font.bold: true; Layout.fillWidth: true }
                                LabText { text: (modelData.libraryState==='hidden' ? "Hidden built-in" : "Removed import")+" · v"+modelData.version+" · "+modelData.labKey; Layout.fillWidth: true; elide: Text.ElideRight; maximumLineCount: 2 }
                                LabText { text: modelData.status || "Progress unavailable"; Layout.fillWidth: true }
                                RowLayout {
                                    Layout.fillWidth: true
                                    LabButton {
                                        objectName: "restore-primary-"+modelData.labKey
                                        text: modelData.canResume ? "Restore and resume" : "Restore to Library"; enabled: !v.libraryChoicesReadOnly
                                        onActiveFocusChanged: if(activeFocus) library.ensureVisible(parent.parent.parent)
                                        onClicked: { if(modelData.canResume) window.restoreAndResume(modelData.labKey,this); else window.libraryAction(modelData,'restore',this) }
                                    }
                                    Item { Layout.fillWidth: true }
                                    LibraryActions {
                                        objectName: "inactive-actions-"+modelData.labKey
                                        entry: modelData; readOnly: v.libraryChoicesReadOnly; hasHistory: modelData.hasHistory; viewport: library
                                        onChoose: function(action) { window.libraryAction(modelData,action,this) }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            ColumnLayout {
                RowLayout {
                    Layout.fillWidth: true
                    ColumnLayout {
                        Layout.fillWidth: true; spacing: 2
                        LabText { objectName: "labHeading"; text: v.metadata.title; font.pixelSize: compact ? 20 : 24; font.bold: true; Layout.fillWidth: true }
                        LabText { objectName: "simulationIndicator"; text: (linux ? "Simulated environment · " : "") + v.mode + " · v" + v.scenarioVersion + " · attempt " + v.attemptId.slice(0,8) + " · applied revision " + v.revision; color: colors.muted; Layout.fillWidth: true; font.pixelSize: 12 }
                    }
                    LabButton { objectName: "modeButton"; text: "Change mode…"; enabled: !v.readOnly && v.canStartAttempt; onClicked: window.restart(v.mode==="Learn"?"Challenge":"Learn",this) }
                    LabButton { objectName: "exportPackButton"; text: "Export scenario…"; KeyNavigation.tab: window.linux ? mission.linuxFirstControl : null; onClicked: exportDialog.open() }
                }
                SplitView {
                    id: framing; objectName: "workspaceFraming"; Layout.fillWidth: true; Layout.fillHeight: true
                    orientation: compact ? Qt.Vertical : Qt.Horizontal
                    onResizingChanged: if(!resizing) window.rememberLayout()
                    MissionPanel {
                        id: mission; v: window.v; controller: window.controller
                        detailsOpen: window.linuxDetailsOpen
                        onDetailsToggled: { window.linuxDetailsOpen=!window.linuxDetailsOpen; if(!window.linuxDetailsOpen) Qt.callLater(mission.focusDetails) }
                        onResizeRequested: function(delta) { if(compact) mission.SplitView.preferredHeight=Math.max(86,Math.min(180,height+delta)); else mission.SplitView.preferredWidth=Math.max(220,Math.min(420,width+delta)); window.rememberLayout() }
                        SplitView.preferredWidth: linux && linuxDetailsOpen ? Math.max(320,v.workspaceLayout.mission_width || 360) : (v.workspaceLayout.mission_width || 280); SplitView.minimumWidth: compact ? 100 : (linux ? (linuxDetailsOpen ? 320 : 260) : 220); SplitView.maximumWidth: compact ? Infinity : 420
                        SplitView.preferredHeight: compact ? (v.workspaceLayout.mission_height || (linux ? 160 : 96)) : 135; SplitView.minimumHeight: compact ? (linux && linuxDetailsOpen ? 128 : 86) : 200; SplitView.maximumHeight: compact ? 240 : Infinity
                    }
                    StackLayout {
                        currentIndex: reviewing ? 2 : (linux ? 1 : 0)
                        SplitView.fillWidth: true; SplitView.fillHeight: true
                        SplitView.minimumWidth: compact ? 100 : 400; SplitView.minimumHeight: compact ? (linux ? (linuxWork && linuxWork.toolsOpen ? (linuxDetailsOpen ? 258 : 304) : 180) : 286) : 320
                        SplitView {
                            id: workSplit; orientation: Qt.Vertical
                            onResizingChanged: if(!resizing) window.rememberLayout()
                            FocusScope {
                                id: workspace; objectName: "domainWorkspace"
                                SplitView.fillHeight: true; SplitView.minimumHeight: workspaceMinimumHeight
                                Loader {
                                    anchors.fill: parent; focus: true; active: !window.linux
                                    sourceComponent: networkWorkspace
                                }
                                Component { id: networkWorkspace; NetworkWorkspace { v: window.v; controller: window.controller; hostWindow: window; focus: true } }
                            }
                            DiagnosticsDock {
                                id: dock; v: window.v; controller: window.controller
                                SplitView.preferredHeight: v.workspaceLayout.dock_height || (compact ? 135 : 220); SplitView.maximumHeight: Math.max(120,workSplit.height-workspaceMinimumHeight); SplitView.minimumHeight: 120
                                onResizeRequested: function(delta) { dock.SplitView.preferredHeight=Math.max(120,Math.min(workSplit.height-workspaceMinimumHeight,height+delta)); window.rememberLayout() }
                            }
                        }
                        Loader {
                            id: linuxLoader; active: window.linux
                            sourceComponent: Component { LinuxTerminalWorkspace { v: window.v; controller: window.controller; compactReference: window.compact && window.linuxDetailsOpen } }
                        }
                        LabScrollView {
                            id: review; objectName: "reviewPanel"; clip: true; contentWidth: availableWidth
                            ColumnLayout {
                                width: review.availableWidth; spacing: 14
                                LabText { objectName: "gradeHeading"; text: v.hasGrade ? "Submission review · " + v.grade.score + "/100" : "No submission for this applied revision"; font.pixelSize: 24; font.bold: true; Layout.fillWidth: true }
                                LabText { text: "Submission records the applied final state. Diagnostic runs do not submit an assessment. Hints have no score penalty."; color: colors.muted; Layout.fillWidth: true }
                                Repeater {
                                    model: v.hasGrade ? v.grade.objectives : []
                                    LabText { required property var modelData; text: (modelData.ok?"PASS":"FAIL") + " · " + modelData.earned + "/" + modelData.possible + " · " + modelData.label + "\n" + modelData.evidence; color: modelData.ok?colors.success:colors.danger; Layout.fillWidth: true }
                                }
                                LabText { text: v.provenance; color: colors.muted; Layout.fillWidth: true; font.pixelSize: 12 }
                                LabButton { objectName: "continueWorking"; text: "Continue working"; onClicked: { reviewing=false;if(v.page===1) { if(linux) linuxWork.focusTerminal(); else workspace.forceActiveFocus() } } }
                            }
                        }
                    }
                }
                LabText { objectName: "draftWarning"; text: v.dirty ? "UNAPPLIED DRAFTS · diagnostics and Submit use applied state." : "Applied state ready · no pending settings drafts"; color: v.dirty?colors.danger:colors.muted; Layout.fillWidth: true; font.pixelSize: 12 }
                RowLayout {
                    Layout.fillWidth: true
                    LabButton { objectName: "applyButton"; text: "Apply changes"; visible: !window.linux || v.canEditVirtualFile; enabled: !v.readOnly && v.dirty; onClicked: controller.apply() }
                    LabButton { objectName: "testButton"; text: "Run diagnostics"; enabled: !v.readOnly; onClicked: { controller.test(); reviewing=false } }
                    LabButton { objectName: "submitButton"; text: "Submit"; highlighted: true; enabled: !v.readOnly; onClicked: { returnFocus=this; if(v.dirty) submitDialog.open(); else {controller.submit();reviewing=true} } }
                    LabButton { objectName: "reviewButton"; text: "Review"; onClicked: reviewing=true }
                    Item { Layout.fillWidth: true }
                    LabButton { objectName: "resetButton"; text: "Reset…"; enabled: !v.readOnly && v.canStartAttempt; onClicked: window.restart(v.mode,this) }
                }
            }
            ColumnLayout {
                LabText { text: "Attempt history"; font.pixelSize: 27; font.bold: true; Layout.fillWidth: true }
                RowLayout {
                    CheckBox { text: "All labs · recent page per lab"; checked: historyAll; onToggled: historyAll=checked }
                    LabText { text: historyAll ? "Select a lab to browse its full history." : "Selected lab: " + v.metadata.title + " · v" + v.scenarioVersion; Layout.fillWidth: true }
                }
                LabText { text: "Every prior attempt is retained. Scenario export and personal attempt export are separate."; color: colors.muted; Layout.fillWidth: true }
                ListView {
                    id: history; objectName: "historyList"; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 10
                    model: historyAll ? v.allHistory : v.history
                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        width: ListView.view.width; implicitHeight: historyCard.implicitHeight+24; color: colors.surface; radius: 8
                        ColumnLayout {
                            id: historyCard; anchors.fill: parent; anchors.margins: 12
                            LabText { text: (modelData.labTitle || v.metadata.title) + " · " + modelData.mode + " · " + modelData.score + "/100 best · " + modelData.hints + " hints · " + modelData.status; font.bold: true; Layout.fillWidth: true }
                            LabText { text: modelData.started + " · " + modelData.id.slice(0,8) + " · " + modelData.assessments + " submissions"; color: colors.muted; Layout.fillWidth: true }
                            RowLayout {
                                LabButton { onActiveFocusChanged: if(activeFocus) history.positionViewAtIndex(index,ListView.Contain); text: details.visible?"Hide details":"Show details"; onClicked: details.visible=!details.visible }
                                LabButton { onActiveFocusChanged: if(activeFocus) history.positionViewAtIndex(index,ListView.Contain); text: "Export this attempt…"; visible: !historyAll; onClicked: {exportAttemptId=modelData.id;attemptExport.open()} }
                                LabButton { onActiveFocusChanged: if(activeFocus) history.positionViewAtIndex(index,ListView.Contain); text: "Open this lab"; visible: historyAll; onClicked: window.openLab(modelData.labKey,this) }
                            }
                            LabText { id: details; visible: false; text: modelData.details; Layout.fillWidth: true }
                        }
                    }
                }
                RowLayout {
                    visible: !historyAll
                    LabButton { text: "Previous"; enabled: v.historyPage>0; onClicked: controller.historyPage(-1) }
                    LabText { text: "Page " + (v.historyPage+1) + " · " + v.historyCount + " retained prior attempts" }
                    LabButton { text: "Next"; enabled: (v.historyPage+1)*25<v.historyCount; onClicked: controller.historyPage(1) }
                }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            LabText { objectName: "statusText"; text: v.page===1 ? v.message : v.transferMessage || v.catalogNotice || (v.page===0 ? "Choose a scenario to begin or resume." : v.historyWarnings || "History preserves drafts, hints, and submissions."); Layout.fillWidth: true; font.pixelSize: 12; color: colors.muted; maximumLineCount: 3; elide: Text.ElideRight }
            LabButton { text: "Retry save"; visible: v.canRetry; onClicked: controller.retrySave() }
        }
    }
    Dialog {
        id: resumeLibraryDialog; objectName: "resumeLibraryDialog"
        anchors.centerIn: parent; width: Math.min(620,window.width-40)
        height: Math.min(430,window.height-40); modal: true
        title: "Restore and resume"
        contentItem: InsetScrollView {
            LabText { Layout.fillWidth: true; text: "Restore this exact lab version to the Library and continue the selected attempt. Progress, drafts, mode and pinned content are kept. Any current lab drafts will be saved." }
            LabText { Layout.fillWidth: true; text: "Select a saved attempt:"; visible: window.resumeChoices.length>1 }
            ButtonGroup { id: resumeGroup }
            Repeater {
                model: window.resumeChoices
                delegate: RadioButton {
                    required property var modelData
                    required property int index
                    objectName: "resume-choice-"+index
                    Layout.fillWidth: true; ButtonGroup.group: resumeGroup
                    checked: window.resumeIndex===index
                    onClicked: window.resumeIndex=index
                    text: modelData.mode+" · v"+modelData.version+" · "+modelData.id.slice(0,8)+"\nStarted "+modelData.started
                    contentItem: LabText { text: parent.text; leftPadding: parent.indicator.width+parent.spacing; wrapMode: Text.Wrap }
                }
            }
            LabText { Layout.fillWidth: true; text: window.resumeChoices.length ? "Attempts ended by Reset or mode changes remain available in History; they are not resumed." : "No resumable attempt is available. Close this dialog and refresh the Library." }
        }
        footer: DialogButtonBox {
            LabButton { id: cancelLibraryResume; objectName: "cancelLibraryResume"; text: "Cancel"; onClicked: resumeLibraryDialog.reject() }
            LabButton {
                objectName: "confirmLibraryResume"; text: "Restore and resume"
                enabled: window.resumeIndex>=0 && window.resumeIndex<window.resumeChoices.length
                onClicked: {
                    if(controller.restoreAndResume(window.resumeKey,window.resumeChoices[window.resumeIndex].id,true)) resumeLibraryDialog.accept()
                    else resumeLibraryDialog.reject()
                }
            }
        }
        onOpened: cancelLibraryResume.forceActiveFocus()
        onClosed: Qt.callLater(function(){ if(v.page===1) { if(linux) linuxWork.focusTerminal(); else mission.forceActiveFocus() } else showHiddenControl.forceActiveFocus() })
    }
    Dialog {
        id: removeLibraryDialog; objectName: "removeLibraryDialog"
        anchors.centerIn: parent; width: Math.min(620,window.width-40); modal: true
        title: "Remove this imported version from Library?"
        height: Math.min(430,window.height-40)
        contentItem: InsetScrollView {
            LabText {
                Layout.fillWidth: true
                text: (window.removalEntry.metadata ? window.removalEntry.metadata.title : "")+" · v"+(window.removalEntry.version || "")
                font.bold: true
            }
            LabText {
                Layout.fillWidth: true
                text: "The exact pack, current attempt, drafts, completed results and history are retained. Use Show hidden / removed to restore it before practicing again. History remains viewable without restoring. Reimporting the same pack will not undo removal. Other versions are unaffected. Nothing is permanently deleted."
            }
        }
        footer: DialogButtonBox {
            LabButton { id: cancelLibraryRemoval; objectName: "cancelLibraryRemoval"; text: "Cancel"; onClicked: removeLibraryDialog.reject() }
            LabButton { objectName: "confirmLibraryRemoval"; text: "Remove from active Library"; onClicked: removeLibraryDialog.accept() }
        }
        onOpened: cancelLibraryRemoval.forceActiveFocus()
        onAccepted: controller.setLibraryState(window.removalEntry.labKey,'removed',true)
        onClosed: Qt.callLater(function(){ showHiddenControl.forceActiveFocus() })
    }
    FileDialogs.FileDialog {
        id: backupProfileDialog; objectName: "backupProfileFileDialog"; title: "Save a new personal profile backup"
        fileMode: FileDialogs.FileDialog.SaveFile; defaultSuffix: "llbackup"
        nameFilters: ["Learning Lab profile backup (*.llbackup)"]
        onAccepted: { controller.backupProfile(selectedFile.toString()); profileResult.open() }
        onRejected: Qt.callLater(function(){ window.restoreFocus() })
    }
    FileDialogs.FileDialog {
        id: restoreArchiveDialog; objectName: "restoreProfileFileDialog"; title: "Choose a profile backup to validate"
        nameFilters: ["Learning Lab profile backup (*.llbackup)"]
        onAccepted: { restoreArchive=selectedFile.toString(); restoreParentDialog.open() }
        onRejected: Qt.callLater(function(){ window.restoreFocus() })
    }
    FileDialogs.FolderDialog {
        id: restoreParentDialog; title: "Choose where to create a NEW restored profile folder"
        onAccepted: {
            if(controller.previewRestore(restoreArchive,selectedFolder.toString())) restorePreview.open()
            else profileResult.open()
        }
        onRejected: { controller.cancelRestore(); Qt.callLater(function(){ window.restoreFocus() }) }
    }
    Dialog {
        id: restorePreview; objectName: "restoreProfilePreview"
        anchors.centerIn: parent; width: Math.min(640,window.width-40); height: Math.min(480,window.height-40)
        modal: true; title: "Restore into a new profile?"
        contentItem: ProfileTransferView {
            id: profilePreviewScroll; objectName: "profilePreviewScroll"
            details: v.profilePreviewDetails; fieldPrefix: "preview"
        }
        footer: DialogButtonBox {
            LabButton { id: cancelProfileRestore; objectName: "cancelProfileRestore"; text: "Cancel"; onClicked: restorePreview.reject() }
            LabButton { objectName: "confirmProfileRestore"; text: "Restore new profile"; enabled: v.restoreReady; onClicked: restorePreview.accept() }
        }
        onOpened: cancelProfileRestore.forceActiveFocus()
        onRejected: controller.cancelRestore()
        onAccepted: { controller.confirmRestore(true); profileResult.open() }
        onClosed: Qt.callLater(function(){ window.restoreFocus() })
    }
    Dialog {
        id: profileResult; objectName: "profileResult"
        anchors.centerIn: parent; width: Math.min(640,window.width-40); height: Math.min(360,window.height-40)
        modal: true; title: "Profile backup / restore"; standardButtons: Dialog.Ok
        contentItem: ProfileTransferView {
            id: profileResultScroll; objectName: "profileResultScroll"
            details: v.profileResultDetails; fieldPrefix: "result"
        }
        onClosed: Qt.callLater(function(){ window.restoreFocus() })
    }
    AuthoringDialog { id: authoringPanel; workflow: controller.authoring; onClosed: createLabButton.forceActiveFocus() }
    FileDialogs.FileDialog { id: importDialog; objectName: "importDialog"; title: "Import a data-only scenario"; nameFilters: ["Learning Lab scenarios (*.lab.json)","JSON files (*.json)"]; onAccepted: controller.importPack(selectedFile.toString()) }
    FileDialogs.FileDialog { id: exportDialog; title: "Export scenario only"; fileMode: FileDialogs.FileDialog.SaveFile; defaultSuffix: "lab.json"; nameFilters: ["Learning Lab scenarios (*.lab.json)"]; onAccepted: controller.exportScenario(selectedFile.toString()) }
    FileDialogs.FileDialog { id: attemptExport; title: "Export personal attempt history"; fileMode: FileDialogs.FileDialog.SaveFile; defaultSuffix: "attempt.json"; nameFilters: ["Personal attempt (*.attempt.json)"]; onAccepted: controller.exportAttempt(selectedFile.toString(),exportAttemptId) }
    Dialog {
        id: switchDialog; objectName: "switchDialog"; anchors.centerIn: parent; width: Math.min(560,window.width-40); modal: true
        title: "Keep drafts and switch labs?"
        contentItem: LabText { text: "The current attempt and pending edits will be saved. Returning resumes the same attempt; nothing is applied or discarded." }
        footer: DialogButtonBox {
            LabButton { id: cancelSwitch; objectName: "cancelSwitch"; text: "Cancel"; onClicked: switchDialog.reject() }
            LabButton { objectName: "confirmSwitch"; text: "Keep drafts and switch"; onClicked: switchDialog.accept() }
        }
        onOpened: cancelSwitch.forceActiveFocus()
        onAccepted: { if(pendingPage===2) controller.viewHistory(pendingLab,true); else controller.selectLab(pendingLab,true) }
        onClosed: window.restoreFocus()
    }
    Dialog {
        id: restartDialog; objectName: "restartDialog"; anchors.centerIn: parent; width: Math.min(560,window.width-40); modal: true
        title: pendingMode===v.mode ? "Reset this scenario?" : "Start a fresh " + pendingMode + " attempt?"
        contentItem: LabText { text: "Archive the current attempt, including drafts, pending commands, hints, and submissions. Start from the initial state. Assisted work will not be relabeled unassisted." }
        footer: DialogButtonBox {
            LabButton { id: cancelRestart; objectName: "cancelRestart"; text: "Cancel"; onClicked: restartDialog.reject() }
            LabButton { objectName: "confirmRestart"; text: "Archive and start fresh"; onClicked: restartDialog.accept() }
        }
        onOpened: cancelRestart.forceActiveFocus()
        onAccepted: { controller.restart(pendingMode); reviewing=false }
        onClosed: window.restoreFocus()
    }
    Dialog {
        id: submitDialog; objectName: "submitDraftDialog"; anchors.centerIn: parent; width: Math.min(560,window.width-40); modal: true
        title: "Submit applied state with drafts pending?"
        contentItem: LabText { text: "Your draft changes will be retained but excluded from this submission. Cancel to review and Apply them first." }
        footer: DialogButtonBox {
            LabButton { id: cancelSubmit; objectName: "cancelSubmit"; text: "Cancel"; onClicked: submitDialog.reject() }
            LabButton { objectName: "confirmSubmit"; text: "Submit applied state"; onClicked: submitDialog.accept() }
        }
        onOpened: cancelSubmit.forceActiveFocus()
        onAccepted: {controller.submit();reviewing=true}
        onClosed: window.restoreFocus()
    }
    Dialog {
        id: failedSave; anchors.centerIn: parent; width: Math.min(560,window.width-40); modal: true; title: "Progress has not been saved"
        contentItem: LabText { text: "Changes remain in memory. Cancel and use Retry save after fixing storage access. Discard closes the window without saving those changes." }
        standardButtons: Dialog.Cancel | Dialog.Discard
        onDiscarded: {discardFailedSave=true;window.close()}
    }
}
