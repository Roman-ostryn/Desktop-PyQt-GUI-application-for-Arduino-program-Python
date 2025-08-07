import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import CoffeeController 1.0

import "controls"

ApplicationWindow {
    id: window
    width: 800
    height: 480

    // Add these properties after the window title to center the window
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    visible: true
    color: "#2c3e50"
    title: "Silvia Coffee Controller"
    
    property string currentScreen: "home"
    
    property real currentTemp: 25.0
    property real currentPressure: 0.0
    property real currentWeight: 0.0
    property string currentState: "IDLE"
    property string brewTime: "00:00"
    property bool steamActive: false
    property bool flushActive: false
    
    CoffeeController {
        id: controller
        
        onTemperatureChanged: function(temp) { window.currentTemp = temp }
        onPressureChanged: function(press) { window.currentPressure = press }
        onWeightChanged: function(wt) { window.currentWeight = wt }
        onStateChanged: function(st) { window.currentState = st }
        onBrewTimeChanged: function(time) { window.brewTime = time }
        
        onErrorOccurred: function(error) {
            errorDialog.text = error
            errorDialog.open()
        }
        
        onWarningIssued: function(warning) {
            warningDialog.text = warning
            warningDialog.open()
        }
        
        onConnectionStatusChanged: function(connected) {
            connectionStatus.connected = connected
        }
    }
    
    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: homeScreen
    }
    
    // Connection Status Indicator
    Rectangle {
        id: connectionStatus
        property bool connected: false
        //property bool connected: true
        
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 10
        width: 100
        height: 30
        radius: 15
        color: connected ? "#27ae60" : "#e74c3c"
        
        Text {
            anchors.centerIn: parent
            text: connectionStatus.connected ? "CONNECTED" : "DISCONNECTED"
            color: "white"
            font.pixelSize: 10
            font.bold: true
        }
    }
    
    // Emergency Stop Button
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.right: connectionStatus.left
        anchors.margins: 10
        width: 100
        height: 30
        radius: 20
        color: "#c0392b"
        border.color: "#ffffff"
        border.width: 2
        
        Text {
            anchors.centerIn: parent
            text: "EMERGENCY STOP"//"/n"
            color: "white"
            font.pixelSize: 10
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: controller.emergencyStop()
        }
    }
    
    // Error Dialog
    Dialog {
        id: errorDialog
        property alias text: errorText.text
        
        anchors.centerIn: parent
        width: Math.min(parent.width - 40, 400)
        height: 200
        modal: true
        
        Rectangle {
            anchors.fill: parent
            color: "#2c3e50"
            radius: 10
            border.color: "#e74c3c"
            border.width: 2
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                
                Text {
                    text: "ERROR"
                    color: "#e74c3c"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    id: errorText
                    color: "white"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Button {
                    text: "OK"
                    Material.background: "#e74c3c"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: errorDialog.close()
                }
            }
        }
    }
    
    // Warning Dialog
    Dialog {
        id: warningDialog
        property alias text: warningText.text
        
        anchors.centerIn: parent
        width: Math.min(parent.width - 40, 400)
        height: 200
        modal: true
        
        Rectangle {
            anchors.fill: parent
            color: "#2c3e50"
            radius: 10
            border.color: "#f39c12"
            border.width: 2
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                
                Text {
                    text: "WARNING"
                    color: "#f39c12"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    id: warningText
                    color: "white"
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Button {
                    text: "OK"
                    Material.background: "#f39c12"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: warningDialog.close()
                }
            }
        }
    }
    
    // Home Screen
    Component {
        id: homeScreen
        
        Rectangle {
            color: "#2c3e50"
            
            ColumnLayout {
                anchors.fill: parent
                spacing: 10
                
                Text {
                    text: "Coffee Machine Ready"
                    color: "white"
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignHCenter
                }
                
                RowLayout{
                    
                    spacing: 100
                    Layout.alignment: Qt.AlignHCenter

                    Layout.preferredWidth: parent.width*0.8

                    ColumnLayout {

                        Layout.leftMargin: 30
                        Layout.alignment: Qt.AlignLeft

                        spacing: 10
                        
                        Button {
                            text: "BREW"
                            Layout.preferredWidth: 150
                            Material.background: "#3498db"
                            enabled: connectionStatus.connected
                            onClicked: {
                                controller.startBrew()
                                stackView.push(brewScreen)
                            }
                        }
                        
                        RowLayout {
                            spacing: 10
                            Button {
                                Layout.preferredWidth: 150
                                text: "STEAM"
                                Material.background: "#e74c3c"
                                enabled: connectionStatus.connected && !window.steamActive
                                onClicked: {
                                    window.steamActive = true
                                    controller.startSteam()
                                    //stackView.push(steamScreen)
                                }
                            }
                            Button {
                                text: "STOP"
                                Material.background: "#95a5a6"
                                enabled: connectionStatus.connected
                                visible: window.steamActive
                                onClicked: {
                                    window.steamActive = false
                                    controller.stopSteam()
                                }
                            }
                        }
                        
                        RowLayout {
                            spacing: 10
                            Button {
                                Layout.preferredWidth: 150
                                text: "FLUSH"
                                Material.background: "#f39c12"
                                enabled: connectionStatus.connected && !window.flushActive
                                onClicked: {
                                    window.flushActive = true
                                    controller.startFlush()
                                    //stackView.push(flushScreen)
                                }
                            }
                            Button {
                                text: "STOP"
                                Material.background: "#95a5a6"
                                enabled: connectionStatus.connected
                                visible: window.flushActive
                                onClicked: {
                                    window.flushActive = false
                                    controller.stopFlush()
                                }
                            }
                        }
                    }

                    CircularSlider {
                        id: tempGauge
                        Layout.alignment: Qt.AlignRight
                        Layout.rightMargin: 30
                        width: 120
                        height: 120

                        minValue: 0
                        maxValue: 150
                        value: window.currentTemp
                        interactive: false
                        progressColor: "#e74c3c"
                        trackColor: "#34495e"
                        
                        startAngle: 30.0
                        endAngle: 330
                        rotation: 180
                        
                        Text {
                            anchors.centerIn: parent
                            text: window.currentTemp.toFixed(1) + "°C"
                            color: "white"
                            font.pixelSize: 16
                            font.bold: true

                            rotation: 180
                        }
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            onClicked: {
                                stackView.push(settingsScreen)
                            }
                            // Optional: Visual feedback on hover
                            onEntered: tempGauge.scale = 1.05
                            onExited: tempGauge.scale = 1.0
                        }
                    }
                }
            }
        }
    }
    
    // Brew Screen
    Component {
        id: brewScreen
        
        Rectangle {
            color: "#2c3e50"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5

                // Top-info card -----------------------------------------------------------
                Rectangle {
                    id: infoCard
                    Layout.fillWidth: true
                    height: 56
                    color: "#34495e"
                    radius: 8
                    border.color: Qt.darker("#e0e0e0", 1.5)
                    border.width: 1

                    RowLayout {
                        anchors.fill: parent
                        //anchors.margins: 8
                        anchors.leftMargin: 15
                        anchors.rightMargin: 15
                        anchors.topMargin: 1
                        anchors.bottomMargin: 1
                        
                        Button {
                            Layout.alignment : Qt.AlignLeft
                            Layout.fillHeight: true
                            text: "BACK"
                            Material.background: "#95a5a6"
                            onClicked: {
                                stackView.pop()
                                controller.stopBrew()
                            }
                        }

                        // Temperature
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.fillWidth: true
                            spacing: 10
                            Image {
                                source: "svgs/thermometer-sun.svg"
                                sourceSize: Qt.size(20, 20)
                                Layout.alignment: Qt.AlignVCenter
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                            }
                            Text {
                                text: window.currentTemp.toFixed(1) + "°C"
                                color: "#ff5252"
                                font { pixelSize: 18; bold: true }
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }

                        // Brew time
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.fillWidth: true
                            spacing: 10
                            Image {
                                source: "svgs/alarm-clock.svg"
                                sourceSize: Qt.size(20, 20)
                                Layout.alignment: Qt.AlignVCenter
                                smooth: true
                            }
                            Text {
                                text: window.brewTime
                                color: "#4caf50"
                                font { pixelSize: 18; bold: true }
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }

                        // Weight
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.fillWidth: true
                            //Layout.alignment: Qt.AlignVCenter
                            spacing: 10
                            Image {
                                source: "svgs/syringe.svg"
                                sourceSize: Qt.size(20, 20)
                                Layout.alignment: Qt.AlignVCenter
                                smooth: true
                            }
                            Text {
                                text: window.currentWeight.toFixed(1) + " g"
                                color: "#29b6f6"
                                font { pixelSize: 18; bold: true }
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }

                        RowLayout {
                            Layout.alignment: Qt.AlignRight
                            Layout.fillHeight: true

                            spacing: 10

                            Button {
                                Layout.fillHeight: true
                                //Layout.preferredWidth: 80

                                text: "BREW NOW"
                                Material.background: window.currentState === "HEATING_BREW" ? "#27ae60" : "#7f8c8d"
                                enabled: connectionStatus.connected && window.currentState === "HEATING_BREW"
                                onClicked: {
                                    // Clear charts when starting new brew
                                    coffeeChart.dataPoints = []
                                    pressureChart.dataPoints = []
                                    coffeeChart.requestPaint()
                                    pressureChart.requestPaint()
                                    controller.beginBrew()
                                }
                            }
                            Button {
                                Layout.fillHeight: true
                                Layout.preferredWidth: 80
                                text: "STOP"
                                Material.background: "#e74c3c"
                                onClicked: controller.stopBrew()
                            }
                        }
                    }
                }
                
                // Charts row
                ColumnLayout {
                    Layout.fillWidth: true
                    //Layout.fillHeight: true
                    spacing: 10
                    
                    // Coffee extraction chart
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#34495e"
                        border.color: "#7f8c8d"
                        border.width: 1
                        radius: 5
                        
                        Column {
                            anchors.fill: parent
                            anchors.margins: 5
                            
                            Text {
                                text: "Coffee (g)"
                                color: "white"
                                font.pixelSize: 12
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            
                            Canvas {
                                id: coffeeChart
                                width: parent.width
                                height: parent.height - 20
                                
                                property var dataPoints: []
                                property real maxWeight: 1
                                property real maxTime: 10
                                
                                function updateScale() {
                                    if (dataPoints.length > 0) {
                                        var maxW = 1
                                        var maxT = 10
                                        for (var i = 0; i < dataPoints.length; i++) {
                                            if (dataPoints[i].weight > maxW) maxW = dataPoints[i].weight
                                            if (dataPoints[i].time > maxT) maxT = dataPoints[i].time
                                        }
                                        maxWeight = Math.max(maxW * 1.1, 1)
                                        maxTime = Math.max(maxT * 1.1, 10)
                                    }
                                }
                                
                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)
                                    
                                    // Draw grid
                                    ctx.strokeStyle = "#7f8c8d"
                                    ctx.lineWidth = 0.5
                                    for (var i = 0; i <= 5; i++) {
                                        var y = (height / 5) * i
                                        ctx.beginPath()
                                        ctx.moveTo(0, y)
                                        ctx.lineTo(width, y)
                                        ctx.stroke()
                                    }
                                    
                                    // Draw current weight value
                                    ctx.fillStyle = "white"
                                    ctx.font = "20px Arial"
                                    ctx.fillText(window.currentWeight.toFixed(1) + " g", 5, 15)
                                    
                                    // Draw data line
                                    if (dataPoints.length > 0) {
                                        ctx.strokeStyle = "#27ae60"
                                        ctx.lineWidth = 2
                                        ctx.beginPath()
                                        
                                        for (var j = 0; j < dataPoints.length; j++) {
                                            var x = (dataPoints[j].time / maxTime) * width
                                            var y = height - (dataPoints[j].weight / maxWeight) * height
                                            
                                            if (j === 0) {
                                                ctx.moveTo(x, y)
                                            } else {
                                                ctx.lineTo(x, y)
                                            }
                                        }
                                        ctx.stroke()
                                        
                                        // Draw current point
                                        if (dataPoints.length > 0) {
                                            var lastPoint = dataPoints[dataPoints.length - 1]
                                            var lastX = (lastPoint.time / maxTime) * width
                                            var lastY = height - (lastPoint.weight / maxWeight) * height
                                            ctx.fillStyle = "#27ae60"
                                            ctx.beginPath()
                                            ctx.arc(lastX, lastY, 3, 0, 2 * Math.PI)
                                            ctx.fill()
                                        }
                                    }
                                }
                                
                                Timer {
                                    interval: 500
                                    running: window.brewTime !== "00:00"
                                    repeat: true
                                    onTriggered: {
                                        var timeSeconds = parseInt(window.brewTime.split(":")[0]) * 60 + parseInt(window.brewTime.split(":")[1])
                                        if (timeSeconds > 0) {
                                            coffeeChart.dataPoints.push({time: timeSeconds, weight: window.currentWeight})
                                            coffeeChart.updateScale()
                                            coffeeChart.requestPaint()
                                        }
                                    }
                                }
                                
                                Connections {
                                    target: window
                                    function onCurrentWeightChanged() {
                                        coffeeChart.requestPaint()
                                    }
                                }
                            }
                        }
                    }
                    
                    // Pressure chart
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: "#34495e"
                        border.color: "#7f8c8d"
                        border.width: 1
                        radius: 5
                        
                        Column {
                            anchors.fill: parent
                            anchors.margins: 5
                            
                            Text {
                                text: "Pressure (bar)"
                                color: "white"
                                font.pixelSize: 12
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            
                            Canvas {
                                id: pressureChart
                                width: parent.width
                                height: parent.height - 20
                                
                                property var dataPoints: []
                                property real maxPressure: 1
                                property real maxTime: 10
                                
                                function updateScale() {
                                    if (dataPoints.length > 0) {
                                        var maxP = 1
                                        var maxT = 10
                                        for (var i = 0; i < dataPoints.length; i++) {
                                            if (dataPoints[i].pressure > maxP) maxP = dataPoints[i].pressure
                                            if (dataPoints[i].time > maxT) maxT = dataPoints[i].time
                                        }
                                        maxPressure = Math.max(maxP * 1.1, 1)
                                        maxTime = Math.max(maxT * 1.1, 10)
                                    }
                                }
                                
                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)
                                    
                                    // Draw grid
                                    ctx.strokeStyle = "#7f8c8d"
                                    ctx.lineWidth = 0.5
                                    for (var i = 0; i <= 5; i++) {
                                        var y = (height / 5) * i
                                        ctx.beginPath()
                                        ctx.moveTo(0, y)
                                        ctx.lineTo(width, y)
                                        ctx.stroke()
                                    }
                                    
                                    // Draw current pressure value
                                    ctx.fillStyle = "white"
                                    ctx.font = "20px Arial"
                                    ctx.fillText(window.currentPressure.toFixed(1) + " bar", 5, 15)
                                    
                                    // Draw data line
                                    if (dataPoints.length > 0) {
                                        ctx.strokeStyle = "#e74c3c"
                                        ctx.lineWidth = 2
                                        ctx.beginPath()
                                        
                                        for (var j = 0; j < dataPoints.length; j++) {
                                            var x = (dataPoints[j].time / maxTime) * width
                                            var y = height - (dataPoints[j].pressure / maxPressure) * height
                                            
                                            if (j === 0) {
                                                ctx.moveTo(x, y)
                                            } else {
                                                ctx.lineTo(x, y)
                                            }
                                        }
                                        ctx.stroke()
                                        
                                        // Draw current point
                                        if (dataPoints.length > 0) {
                                            var lastPoint = dataPoints[dataPoints.length - 1]
                                            var lastX = (lastPoint.time / maxTime) * width
                                            var lastY = height - (lastPoint.pressure / maxPressure) * height
                                            ctx.fillStyle = "#e74c3c"
                                            ctx.beginPath()
                                            ctx.arc(lastX, lastY, 3, 0, 2 * Math.PI)
                                            ctx.fill()
                                        }
                                    }
                                }
                                
                                Timer {
                                    interval: 500
                                    running: window.brewTime !== "00:00"
                                    repeat: true
                                    onTriggered: {
                                        var timeSeconds = parseInt(window.brewTime.split(":")[0]) * 60 + parseInt(window.brewTime.split(":")[1])
                                        if (timeSeconds > 0) {
                                            pressureChart.dataPoints.push({time: timeSeconds, pressure: window.currentPressure})
                                            pressureChart.updateScale()
                                            pressureChart.requestPaint()
                                        }
                                    }
                                }
                                
                                Connections {
                                    target: window
                                    function onCurrentPressureChanged() {
                                        pressureChart.requestPaint()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Steam Screen
    Component {
        id: steamScreen
        
        Rectangle {
            color: "#2c3e50"
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20
                
                Text {
                    text: "Steam Mode"
                    color: "white"
                    font.pixelSize: 24
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: window.currentTemp.toFixed(1) + "°C"
                    color: "white"
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignHCenter
                }
                
                Text {
                    text: window.currentState
                    color: "white"
                    font.pixelSize: 16
                    Layout.alignment: Qt.AlignHCenter
                }
                
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 20
                    
                    Text {
                        text: "Steam heating to target temperature..."
                        color: "#f39c12"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignHCenter
                        visible: window.currentState === "HEATING_STEAM"
                    }
                    
                    Text {
                        text: "Ready for steaming!"
                        color: "#27ae60"
                        font.pixelSize: 14
                        Layout.alignment: Qt.AlignHCenter
                        visible: window.currentState === "STEAMING"
                    }
                    
                    Button {
                        text: "STOP"
                        Material.background: "#95a5a6"
                        onClicked: {
                            window.steamActive = false
                            controller.stopSteam()
                        }
                    }
                    
                    Button {
                        text: "BACK"
                        Material.background: "#95a5a6"
                        onClicked: stackView.pop()
                    }
                }
            }
        }
    }
    
    // Flush Screen
    Component {
        id: flushScreen
        
        Rectangle {
            color: "#2c3e50"
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20
                
                Text {
                    text: "Flush Mode"
                    color: "white"
                    font.pixelSize: 24
                    Layout.alignment: Qt.AlignHCenter
                }
                
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 20
                    
                    Text {
                        text: "Flushing in progress..."
                        color: "#f39c12"
                        font.pixelSize: 16
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    Button {
                        text: "STOP"
                        Material.background: "#95a5a6"
                        onClicked: {
                            window.flushActive = false
                            controller.stopFlush()
                        }
                    }
                    
                    Button {
                        text: "BACK"
                        Material.background: "#95a5a6"
                        onClicked: stackView.pop()
                    }
                }
            }
        }
    }
    /*
    // Settings Screen
    Component {
        id: settingsScreen
        
        Rectangle {
            color: "#2c3e50"
            
            ColumnLayout {
                anchors.centerIn: parent
                spacing: 20
                
                Text {
                    text: "Temperature Settings"
                    color: "white"
                    font.pixelSize: 20
                    Layout.alignment: Qt.AlignHCenter
                }
                
                RowLayout {
                    Text {
                        text: "Brew Temp:"
                        color: "white"
                    }
                    SpinBox {
                        id: brewTempSpin
                        from: 60
                        to: 110
                        value: 93
                    }
                    Text {
                        text: "°C"
                        color: "white"
                    }
                }
                
                RowLayout {
                    Text {
                        text: "Steam Temp:"
                        color: "white"
                    }
                    SpinBox {
                        id: steamTempSpin
                        from: 110
                        to: 150
                        value: 130
                    }
                    Text {
                        text: "°C"
                        color: "white"
                    }
                }
                
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: 20
                    
                    Button {
                        text: "SAVE"
                        Material.background: "#27ae60"
                        onClicked: {
                            controller.setTemperatures(brewTempSpin.value, steamTempSpin.value)
                            stackView.pop()
                        }
                    }
                    
                    Button {
                        text: "BACK"
                        Material.background: "#95a5a6"
                        onClicked: stackView.pop()
                    }
                }
            }
        }
    }
    */

    // Settings Screen ---------------------------------------------------------
    Component {
        id: settingsScreen

        Rectangle {
            color: "#2c3e50"

            /* dim background */
            Rectangle {
                anchors.fill: parent
                color: Qt.rgba(0, 0, 0, 0.35)
            }

            /* frosted-glass card */
            Rectangle {
                id: card
                anchors.centerIn: parent
                width:  Math.min(parent.width  - 40, 320)
                height: 300
                color:  Qt.rgba(1, 1, 1, 0.10)
                radius: 16
                border.color: Qt.rgba(1, 1, 1, 0.15)
                border.width: 1


                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 24
                    spacing: 24

                    /* header row */
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 20
                        Image {
                            source: "svgs/sliders-horizontal.svg"
                            sourceSize: Qt.size(24, 24)
                            smooth: true
                            fillMode: Image.PreserveAspectFit
                        }
                        Text {
                            text: "Temperature Settings"
                            color: "white"
                            font { pixelSize: 20; bold: true }
                        }
                    }

                    /* Brew temperature */
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        Text {
                            Layout.fillWidth: true

                            text: "Brew Temp:"
                            color: "white"
                            font.pixelSize: 15
                        }
                        SpinBox {
                            id: brewTempSpin
                            
                            from: 60; to: 110; value: 93
                            font.pixelSize: 14
                            Material.foreground: "#e7a49cff"
                            Material.accent: "#27ae60"
                        }
                        Text {
                            Layout.alignment: Qt.AlignRight
                            text: "°C"
                            color: "white"
                            font.pixelSize: 14
                        }
                    }

                    /* Steam temperature */
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        Text {
                            Layout.fillWidth: true

                            text: "Steam Temp:"
                            color: "white"
                            font.pixelSize: 15
                        }
                        SpinBox {
                            id: steamTempSpin
                            //Layout.fillWidth: true
                            from: 110; to: 150; value: 130
                            font.pixelSize: 14
                            Material.foreground: "#e7a49cff"
                            Material.accent: "#e74c3c"
                        }
                        Text {
                            Layout.alignment: Qt.AlignRight
                            text: "°C"
                            color: "white"
                            font.pixelSize: 14
                        }
                    }

                    /* action buttons */
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 20
                        Button {
                            text: "SAVE"
                            Material.background: "#27ae60"
                            Material.elevation: 2
                            onClicked: {
                                controller.setTemperatures(brewTempSpin.value,
                                                        steamTempSpin.value)
                                stackView.pop()
                            }
                        }
                        Button {
                            text: "BACK"
                            Material.background: "#7f8c8d"
                            Material.elevation: 2
                            onClicked: stackView.pop()
                        }
                    }
                }
            }
        }
    }
}
