var wsAddress = "ws://"+window.location.hostname+":8090/"
var websocket = null
var map = new Map();
var editor = new Editor();
var runningState = "STOP"

function wsConnect() {
   console.log("connecting...");
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
    setTimeout(function(){wsConnect();},1000);
}

function onMessage(evt){
    //console.log("response: " + evt.data + '\n');
    try{
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
    catch(e){
        console.log("Error: ", e, " in ", evt.data)
    }
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
    setTimeout(requestOutputLines,300)
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
    setTimeout(requestMapElements,3000)
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
    setTimeout(requestDynamicElements,200)
}

function getCallableElementId(objectName, functionName){
    var str = "callableFunction_"+objectName+"_"+functionName
    return str
}

var funcCallTimeout=null;
var funcCallTime=0;
function sendCallableFunctionCall(object, func, debounce=false){
    request = {'object':object,
                'function':func,
                'arguments':[]}
    if(debounce){
        if(funcCallTimeout){
            clearTimeout(funcCallTimeout);
            funcCallTimeout=null;
	}
        if(funcCallTime+1000>new Date().getTime()){
            funcCallTimeout=setTimeout(function(){sendCallableFunctionCall(object, func)},1000);
            return;
        }
        funcCallTime = new Date().getTime();
        console.log(funcCallTime, new Date().getTime())
    }
    var funcId = getCallableElementId(object, func)
    var arguments = $("#"+funcId+" input.callableArgumentInput");
    for(var a=0;a<arguments.length;a++){
        request.arguments.push($("#"+arguments[a].id).val())
    }
    console.log(request)
    doSend("callObjectFunction "+JSON.stringify(request))
}

function debounce(callback, delay){
    var timer;
    return function(){
        var args = arguments;
        var context = this;
        clearTimeout(timer);
        timer = setTimeout(function(){
            callback.apply(context, args);
        }, delay)
    }
}

function displayCallableElements(elements){
    //console.log(elements)
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
            if(!("functionUI" in func)){ 
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
            else{
                if(!("controls" in func.functionUI)){
                    console.log("Not controls in UI", func)
                    continue;
                }
                for(var a=0;a<func.functionUI.controls.length;a++){
                    var control = func.functionUI.controls[a]
                    var argId = funcId+control.arg
                    var type = ("type" in control)?control.type:"text";
                    var min = ("min" in control)?control.min:0;
                    var max = ("max" in control)?control.max:100;
                    var val = ("val" in control)?control.val:0;
                    str = "<div class='callableArgument'>"
                    str += "<input class='callableArgumentInput' type='"+type+"' id='"+argId+"' "
                    if(type=="range"){
                        str += "min='"+min+"' max='"+max+"' value='"+val+"' "
                        str += "oninput='"+argId+"_out.value = "+argId+".value;sendCallableFunctionCall(\""+elem.object+"\",\""+func.name+"\", true)' "
                    }
                    str += " required>"
                    str += "<label class='callableArgumentLabel' for='"+argId+"'>"+control.arg+"</label>"
                    if(type=="range")
                        str += "<output class='callableArgumentLabel' id='"+argId+"_out'></output>"
                    str += "</div>"
                    $("#"+funcId).append(str)
                }
            }
        }
    }
    setTimeout(requestCallableElements,3200)
}

function displayMapBackground(path){
    if(path != ""){
        map.background = path
    }
    //setTimeout(requestMapBackground,2000)
}

function requestMapElements(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getMapElements");
}

function requestDynamicElements(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getDynamicElements");
}

function requestMapBackground(){
    if(map.background == ""){
        if(websocket.readyState == WebSocket.OPEN)
            doSend("getMapBackground");
    }
}

function requestCallableElements(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getCallableElements")
}

function requestOutputLines(){
    if(websocket.readyState == WebSocket.OPEN)
        doSend("getOutputLines")
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
	setTimeout(requestMapBackground, 3000);
    }
    else if(runningState == "PLAY"){
        runningState = "STOP"
        $("#ManualPlayButton").removeAttr('disabled');
        $("#AIPlayButton").css("background-color", "#4cd137");
        $("#ManualPlayButton").css("background-color", "#4cd137");
        setPlayButtonText();
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
	setTimeout(requestMapBackground, 3000);
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

window.onbeforeunload = function() {
       return "Leave the page? Make sure that files are saved.";
};
