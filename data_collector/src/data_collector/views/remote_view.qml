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
        anchors.fill: parent


        VncItem{
            id:vncview
            Layout.fillHeight: true
            Layout.fillWidth: true
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
                text: "5900"
            }
            Item {
                Layout.fillWidth: true
            }
            Q1.Button{
                text: "连接"
                onClicked: {
                    vncview.connectToVncServer(tb_ip.text,"123456",tb_port.text)
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
