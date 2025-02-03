import QtQml 2.15
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Controls 1.4 as Q1
import QtQuick.Controls.Styles 1.4
import QtQml.Models 2.12
import Qt.labs.platform 1.1 as QtPlatform
import QtQuick.Dialogs 1.3

import prismCpp 1.0
import prism_qt_ui 1.0
import viewmodels 1.0

Rectangle {
    anchors.fill: parent
    color: "lightblue"
    property var vm:Remote_viewmodel
    ColumnLayout{
        spacing: 0
        anchors.fill: parent
        VncItem{
            id:vncview
            Layout.fillHeight: true
            Layout.fillWidth: true
            property rect rect:  Qt.rect(36,255,780,416) // vnc display 设置850*850 截全图用photoshop查看每格间距26像素
            onFrameUpdate: function(img){
                vm.recognize(img,rect)
            }
            Item{
                x:36* vncview.width/vncview.frameBufferWidth
                y:255* vncview.height/vncview.frameBufferHeight
                width: (780) * vncview.width/vncview.frameBufferWidth
                height: (416) * vncview.height/vncview.frameBufferHeight
                GridLayout{
                    anchors.fill: parent
                    columnSpacing: 0
                    rowSpacing: 0
                    columns: 30
                    rows: 16
                    Repeater{
                        model:vm.mines
                        delegate: Item{
                           Layout.preferredHeight:  parent.height/16
                            Layout.preferredWidth: parent.width/30
                            property var rvm: vm.mines.getRowData(index)
                            Text {
                                anchors.fill: parent
                                verticalAlignment: Text.verticalCenter
                                horizontalAlignment: Text.horizontalCenter
                                text: Bind.create(rvm,"status") + (vm.updateCells?"":"")
                                color: "red"
                                font.bold: true
                                font.pointSize: 12
                            }
                        }
                    }
                }
            }

        }
        RowLayout{
            Layout.fillWidth: true
            Layout.fillHeight: false
            Layout.preferredHeight: 30
            Text {
                text: qsTr("ip:")
            }
            Q1.TextField{
                id:tb_ip
                text: "127.0.0.1"
            }
            Text {
                text: qsTr("port:")
            }
            Q1.TextField{
                id:tb_port
                text: "5901"
            }
            Q1.CheckBox{
                text: "保存单元格图片"
                onClicked: {
                    vm.saveCellImages = checked
                }
            }
            Item {
                Layout.fillWidth: true
            }
            Q1.Button{
                text: "连接"
                onClicked: {
                    vncview.connectToVncServer(tb_ip.text,"aaaaaaaa",tb_port.text)
                }
            }
            Q1.Button{
                text: "断开连接"
                onClicked: {
                    vncview.disconnectFromVncServer()
                }
            }
        }
    }

}
