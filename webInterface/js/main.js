var wsAddress = "ws://localhost:8090/"
var websocket = null
var map = new Map();
var editor = new Editor();
var runningState = "STOP"

function wsConnect() {
    websocket = new WebSocket(wsAddress);
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt) {
    console.log("connected\n");
}

function onClose(evt){
    console.log("disconnected\n");
}

function onMessage(evt){
    //console.log("response: " + evt.data + '\n');
    message = JSON.parse(evt.data)
    if(message.function == "getMapElements")
        displayMapElements(message.data)
    else if(message.function == "getMapBackground")
        displayMapBackground(message.data)
    else if(message.function == "getDynamicElements")
        displayDynamicElements(message.data)
    else if(message.function == "getFileContent")
        updateFileContent(message.data)
    else if(message.function == "getCallableElements")
        displayCallableElements(message.data)
    else if(message.function == "getOutputLines")
        displayOutputLines(message.data)
    else if(message.function == "getFileList")
        displayFileList(message.data)
    else
        console.log(message)
}

function onError(evt){
    console.log('error: ' + evt.data + '\n');
    websocket.close();
}

function doSend(message) {
    //console.log("sent: " + message + '\n');
    websocket.send(message);
}

function doDisconnect() {
    websocket.close();
}

function displayFileList(files){
    $("#fileSelector").html("")
    for(var i=0;i<files.length;i++){
        var str = "<option value='"+files[i]+"'>"+files[i]+"</option>"
        $("#fileSelector").append(str)
    }
}

function openFile(file){
    if(file == ''){
        file = $("#fileSelector").val()
    }
    sendFileContentRequest(file)
}

function displayOutputLines(messages){
    for(var i=0;i<messages.length;i++){
        $("#logOutput").append(messages[i])
    }
    if(messages.length)
        $("#logOutput").scrollTop($("#logOutput")[0].scrollHeight);
}

function displayMapElements(elements){
    for(var i=0;i<elements.length;i++){
        var elem = elements[i]
        map.addMapElement(elem)
    }
    var diff = $(map.mapElementList).not(elements).get();
    for(var i=0;i<diff.length;i++){
        map.removeMapElement(diff[i])
    }
    map.drawMapElement()
}

function displayDynamicElements(elements){
    for(var i=0;i<elements.length;i++){
        var elem = elements[i]
        map.addDynamicElement(elem)
    }
    var diff = $(map.dynamicElementList).not(elements).get();
    for(var i=0;i<diff.length;i++){
        map.removeDynamicElement(diff[i])
    }
    map.drawDynamicElement()
}

function getCallableElementId(objectName, functionName){
    var str = "callableFunction_"+objectName+"_"+functionName
    return str
}

function sendCallableFunctionCall(object, func){
    request = {'object':object,
                'function':func,
                'arguments':[]}
    var funcId = getCallableElementId(object, func)
    var arguments = $("#"+funcId+" input[type='text']");
    for(var a=0;a<arguments.length;a++){
        request.arguments.push($("#"+arguments[a].id).val())
    }
    doSend("callObjectFunction "+JSON.stringify(request))
}

function displayCallableElements(elements){
    console.log(elements)
    for(var i=0;i<elements.length;i++){
        var elem = elements[i]
        var objId = "callableObject_" + elem.object
        if($("#"+objId).length)
            continue
        var str = "<div class='callableObject' id='"+objId+"'><span class='callableObjectName'>"+elem.object+"</span></div>"
        $("#callableObjectsContainer").append(str)
        for(var k=0;k<elem.functions.length;k++){
            var func = elem.functions[k]
            var funcId = getCallableElementId(elem.object, func.name)
            str = "<div class='callableFunction' id='"+funcId+"'>"
            str += "<span class='callableFunctionName'>"+func.name+"</span>"
            str += "<button class='callableFunctionButton' onclick='sendCallableFunctionCall(\""+elem.object+"\",\""+func.name+"\")'>Send</button>"
            str += "</div>"
            $("#"+objId).append(str)
            for(var a=0;a<func.arguments.length;a++){
                var arg = func.arguments[a]
                var argId = funcId+arg
                str = "<div class='callableArgument'>"
                str += "<input class='callableArgumentInput' type='text' id='"+argId+"' required>"
                str += "<label class='callableArgumentLabel' for='"+argId+"'>"+arg+"</label>"
                str += "</div>"
                $("#"+funcId).append(str)
            }
        }

    }
}

function displayMapBackground(path){
    if(path != ""){
        map.background = path
    }
}

function requestMapElements(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getMapElements");
    setTimeout(requestMapElements,1000)
}

function requestDynamicElements(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getDynamicElements");
    setTimeout(requestDynamicElements,100)
}

function requestMapBackground(){
    if(map.background == ""){
        if(websocket.readyState == WebSocket.OPEN)
            doSend("getMapBackground");
        setTimeout(requestMapBackground,1000)
    }
}

function requestCallableElements(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getCallableElements")
    setTimeout(requestCallableElements,1000)
}

function requestOutputLines(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getOutputLines")
    setTimeout(requestOutputLines,300)
}

function updateFileContent(data){
    if(data.content != "")
        editor.updateFileContent(data.path, data.content)
}


function sendFileSaveRequest(path, content){
    var data = {"path": path
                ,"content": content
                };
    doSend("setFileContent "+JSON.stringify(data))
}

function sendFileContentRequest(path){
    doSend("getFileContent "+path)
}

function sendRunningParameters(){
    var settings = {"mapFilePath": $("#mapFilePath").val()
                    ,"robotFilePath": $("#robotFilePath").val()
                    ,"objectiveFilePath": $("#objectiveFilePath").val()
                    ,"robotConnected": $("#robotConnectedSelection").is(':checked')
                    };
    localStorage.setItem("mapFilePath",settings.mapFilePath);
    localStorage.setItem("robotFilePath",settings.robotFilePath);
    localStorage.setItem("objectiveFilePath",settings.objectiveFilePath);
    doSend("setRunningParameters "+JSON.stringify(settings))
}

function loadRunningParametersFromCache(){
    var mapStr = localStorage.getItem("mapFilePath");
    if(mapStr != null)
        $("#mapFilePath").val(mapStr)
    var objectiveStr = localStorage.getItem("objectiveFilePath");
    if(objectiveStr != null)
        $("#objectiveFilePath").val(objectiveStr)
    var robotStr = localStorage.getItem("robotFilePath");
    if(robotStr != null)
        $("#robotFilePath").val(robotStr)
}

function setPlayButtonText(){
    var text = "Play"
    if(runningState == "PLAY")
        text = "Stop"
    else if(!$("#robotConnectedSelection").is(':checked'))
        text = "Simulate"
    $("#AIPlayButton").text(text)
}

function onPlayButtonClicked(){
    if(runningState == "STOP"){
        runningState = "PLAY"
        for(var i=0;i<map.mapElementList.length;){
            map.removeMapElement(map.mapElementList[i])
        }
        for(var i=0;i<map.dynamicElementList.length;){
            map.removeDynamicElement(map.dynamicElementList[i])
        }
        setPlayButtonText()
        $("#ManualPlayButton").attr('disabled','disabled');
        $("#AIPlayButton").css("background-color", "#e84118");
        $("#ManualPlayButton").css("background-color", "#718093");
        sendRunningParameters()
    }
    else if(runningState == "PLAY"){
        runningState = "STOP"
        $("#ManualPlayButton").removeAttr('disabled');
        $("#AIPlayButton").css("background-color", "#4cd137");
        $("#ManualPlayButton").css("background-color", "#4cd137");
        setPlayButtonText()
    }
    doSend("setRunningState "+runningState)
}

function onManualPlayButtonClicked(){
    if(runningState == "STOP"){
        runningState = "MANUAL"
        for(var i=0;i<map.mapElementList.length;){
            map.removeMapElement(map.mapElementList[i])
        }
        for(var i=0;i<map.dynamicElementList.length;){
            map.removeDynamicElement(map.dynamicElementList[i])
        }
        $("#ManualPlayButton").text("Stop")
        $("#AIPlayButton").attr('disabled','disabled');
        $("#ManualPlayButton").css("background-color", "#e84118");
        $("#AIPlayButton").css("background-color", "#718093");
        sendRunningParameters()
    }
    else if(runningState == "MANUAL"){
        runningState = "STOP"
        $("#ManualPlayButton").text("Manual")
        $("#AIPlayButton").removeAttr('disabled');
        $("#ManualPlayButton").css("background-color", "#4cd137");
        $("#AIPlayButton").css("background-color", "#4cd137");
        setPlayButtonText()
    }
    doSend("setRunningState "+runningState)
}

function onLoadFileButtonClicked(){
    doSend("getFileList")
    sendFileContentRequest($("#mapFilePath").val())
    sendFileContentRequest($("#robotFilePath").val())
    sendFileContentRequest($("#objectiveFilePath").val())
}

function onSaveFileButtonClicked(){
    var files = editor.getFilesToSave()
    for(var i=0;i<files.length;i++)
        sendFileSaveRequest(files[i].path, files[i].content)
    //sendFileSaveRequest($("#mapFilePath").val(), getFileEditorContent($("#mapFilePath").val()))
    //sendFileSaveRequest($("#robotFilePath").val(), getFileEditorContent($("#robotFilePath").val()))
    //sendFileSaveRequest($("#objectiveFilePath").val(), getFileEditorContent($("#objectiveFilePath").val()))
}

$(document).keydown(function(e) {
    var key = undefined;
    var possible = [ e.key, e.keyIdentifier, e.keyCode, e.which ];
    while (key === undefined && possible.length > 0)
        key = possible.pop();
    if (key && (key == '115' || key == '83' ) && (e.ctrlKey || e.metaKey) && !(e.altKey)){
        e.preventDefault();
        onSaveFileButtonClicked();
        return false;
    }
    return true;
});

$(document).ready(function(){
    wsConnect()
    setPlayButtonText()
    setTimeout(requestMapElements,800)
    setTimeout(requestDynamicElements,500)
    setTimeout(requestMapBackground,300)
    setTimeout(requestCallableElements,1000)
    setTimeout(requestOutputLines, 100)
    loadRunningParametersFromCache()
});