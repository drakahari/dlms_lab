import QtQuick
import QtQuick.Controls

LabScrollView {
    id: panel; objectName: "topologyPanel"
    required property var v
    required property QtObject controller
    clip: true
    contentWidth: v.topologyNodes.length * 190 + 16
    contentHeight: 144 + v.topologySegments.length * 32
    Item {
        width: panel.contentWidth; height: panel.contentHeight
        Canvas {
            id: links; anchors.fill: parent
            property var nodes: v.topologyNodes
            onNodesChanged: requestPaint()
            onWidthChanged: requestPaint()
            onPaint: {
                var ctx = getContext("2d"); ctx.reset(); ctx.lineWidth=2
                for (var s=0;s<v.topologySegments.length;s++) {
                    var segment=v.topologySegments[s]; var y=120+s*32; var xs=[]
                    for(var i=0;i<v.topologyNodes.length;i++) if(v.topologyNodes[i].segments.indexOf(segment)>=0) xs.push(99+i*190)
                    ctx.strokeStyle = s%2 ? v.palette.success : v.palette.accent
                    for(var j=0;j<xs.length;j++) { ctx.beginPath();ctx.moveTo(xs[j],91);ctx.lineTo(xs[j],y);ctx.stroke() }
                    if(xs.length) { ctx.beginPath();ctx.moveTo(xs[0],y);ctx.lineTo(xs[xs.length-1],y);ctx.stroke() }
                }
            }
        }
        Repeater {
            model: v.topologyNodes
            LabButton {
                required property var modelData; required property int index
                objectName: "device-"+modelData.id
                x: 12+index*190; y: 12; width: 174; height: 80
                text: modelData.id + "\n" + modelData.addresses
                highlighted: v.selected === modelData.id
                Accessible.name: modelData.id + " " + modelData.role + "; select to inspect"
                onClicked: controller.selectDevice(modelData.id)
                onActiveFocusChanged: if(activeFocus) panel.contentItem.contentX=Math.max(0,x+width-panel.availableWidth)
            }
        }
        Repeater {
            model: v.topologySegments
            LabText { required property string modelData; required property int index; x: 14; y: 124+index*32; text: modelData; color: v.palette.muted; font.pixelSize: 12 }
        }
    }
}
