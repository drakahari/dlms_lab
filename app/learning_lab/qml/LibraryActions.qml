import QtQuick
import QtQuick.Controls

LabButton {
    id: control
    required property var entry
    property bool readOnly: false
    property bool hasHistory: false
    property var viewport
    signal choose(string action)
    text: "Actions ▾"
    Accessible.name: "Actions for " + (entry.title || entry.metadata.title) + " version " + entry.version
    onClicked: menu.open()
    onActiveFocusChanged: if(activeFocus && viewport) viewport.ensureVisible(control)
    Menu {
        id: menu
        property bool acted: false
        onOpened: acted=false
        MenuItem {
            objectName: control.objectName + "Visibility"
            text: control.entry.libraryState==='active' ? (control.entry.builtIn ? "Hide from Library" : "Remove from Library…") : "Restore to Library"
            enabled: !control.readOnly
            onTriggered: { menu.acted=true; control.choose(control.entry.libraryState==='active' ? (control.entry.builtIn ? 'hide' : 'remove') : 'restore') }
        }
        MenuItem {
            objectName: control.objectName + "History"
            text: "View saved history"; enabled: control.hasHistory
            onTriggered: { menu.acted=true; control.choose('history') }
        }
        onClosed: if(!acted) Qt.callLater(function(){ if(control && control.visible) control.forceActiveFocus() })
    }
}
