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
            property string pre_datetime :""
            property var rect:  Qt.rect(36  , 250 , 850-36*2-1 , 850-250-185)
            property real pre_x
            property real pre_y
            onPreviewMousePress:function(e,img)
            {

                if(vncview.pre_datetime!="")
                {
                    //let content = qsTr('{"x":%1,"y":%2}')
                    //                              .arg(pre_x)
                    //                              .arg(pre_y)
                    //CppUtility.createFileAndWrite("data/"+vncview.pre_datetime+".josn",content);

                    vm.saveClickPosLabel("./data/"+vncview.pre_datetime+"_label_action.josn",pre_x,pre_y,26);

                }

                let datetime = JsEx.currentDateTimeZZZString()
                vm.save(img,CppUtility.getAppBaseDir()+ "/data/"+datetime,rect,false)

                vncview.pre_datetime = datetime
                vncview.pre_x = (e.x * vncview.frameBufferWidth / vncview.width) - rect.x
                vncview.pre_y =(e.y * vncview.frameBufferHeight / vncview.height) - rect.y
            }

            onMouseRelease:function(e,img)
            {

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
