var Editor = class {
    constructor() {
        this.fileEditors = []
    }

    getFileId(file){
        return "fileEditor_"+file.replace(/\//g,"_").replace(/\\/g,"_").replace(/\./g,"_")
    }

    getFileEditorContent(path){
        for(var i=0;i<this.fileEditors.length;i++){
            if(this.fileEditors[i].path == path){
                return this.fileEditors[i].editor.getValue()
            }
        }
    }

    getFilesToSave(){
        var output = []
        for(var i=0;i<this.fileEditors.length;i++){
            output.push({'path':this.fileEditors[i].path, 'content':this.fileEditors[i].editor.getValue()})
        }
        return output
    }

    updateFileContent(path, content){
        var id = this.getFileId(path)
        var editor = null
        for(var i=0;i<this.fileEditors.length;i++){
            if(this.fileEditors[i].path == path){
                editor = this.fileEditors[i].editor
            }
        }
        if(editor == null){
            var str = "<pre id='"+id+"' class='fileEditor'></pre>"
            $("#fileEditorContainer").append(str)
            editor = ace.edit(id);
            this.fileEditors.push({"path":path,"editor":editor})
        }
        editor.setTheme("ace/theme/cobalt");
        if(path.includes(".xml"))
            editor.session.setMode("ace/mode/xml");
        if(path.includes(".py"))
            editor.session.setMode("ace/mode/python");
        if(path.includes(".html"))
            editor.session.setMode("ace/mode/html");
        if(path.includes(".js"))
            editor.session.setMode("ace/mode/javascript");
        if(path.includes(".css"))
            editor.session.setMode("ace/mode/css");
        editor.setValue(content, -1)
        this.updateFileSelectionTabs(this.fileEditors.length-1)
        this.showFileTab(this.fileEditors.length-1)
    }

    showFileTab(index){
        for(var i=0;i<this.fileEditors.length;i++){
            if(i == index)
                $("#"+this.getFileId(this.fileEditors[i].path)).css( "display", "block" );
            else
                $("#"+this.getFileId(this.fileEditors[i].path)).css( "display", "none" );
        }
    }

    updateFileSelectionTabs(){
        $("#fileEditorTabContainer").html("")
        for(var i=0;i<this.fileEditors.length;i++){
            var str = "<button class='tabButton' onclick='editor.showFileTab("+i+");'>"+this.fileEditors[i].path+"</button>";
            $("#fileEditorTabContainer").append(str)
        }
    }

}
