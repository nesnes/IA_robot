var Map = class {
    constructor() {
        this.mapElementList = []
        this.dynamicElementList = []
        this.background = ""
    }


    removeDynamicElement(elem){
        var ids = ["mapElem_"+elem.id
        , "mapElem_"+"shape_"+elem.id
        , "mapElem_"+"circle_"+elem.id]

        for(var i=0;i<ids.length;i++)
            if($("#"+ids[i]).length)
                $("#"+ids[i]).remove()

        for(var i=0;i<this.dynamicElementList.length;i++)
            if(this.dynamicElementList[i].id == elem.id){
                this.dynamicElementList.splice(i,1)
                break
            }
    }

    addDynamicElement(elem){
        for(var i=0;i<this.dynamicElementList.length;i++)
            if(this.dynamicElementList[i].id == elem.id){
                this.dynamicElementList.splice(i,1)
                break
            }
        this.dynamicElementList.push(elem)
    }

    removeMapElement(elem){
        var ids = ["mapElem_"+elem.id
        , "mapElem_"+"avoid_"+elem.id
        , "mapElem_"+"shape_"+elem.id
        , "mapElem_"+"accessCircle_"+elem.id
        , "mapElem_"+"accessLine_"+elem.id]

        for(var i=0;i<ids.length;i++)
            if($("#"+ids[i]).length)
                $("#"+ids[i]).remove()

        for(var i=0;i<this.mapElementList.length;i++)
            if(this.mapElementList[i].id == elem.id){
                this.mapElementList.splice(i,1)
                break
            }
    }

    addMapElement(elem){
        for(var i=0;i<this.mapElementList.length;i++)
            if(this.mapElementList[i].id == elem.id){
                this.mapElementList.splice(i,1)
                break
            }
        this.mapElementList.push(elem)
    }

    drawMapElement(){
        if(this.background != "")
            this.drawImage(this.background, "mapBackground")
        for(var i=0;i<this.mapElementList.length;i++)
            if(this.mapElementList[i].avoidShape)
                this.drawShape(this.mapElementList[i].avoidShape, "avoid_"+this.mapElementList[i].id, 0.15)
        for(var i=0;i<this.mapElementList.length;i++)
            if(this.mapElementList[i].shape)
                this.drawShape(this.mapElementList[i].shape, "shape_"+this.mapElementList[i].id, 0.9)
        for(var i=0;i<this.mapElementList.length;i++)
            if(this.mapElementList[i].accessPoint){
                //add circle
                this.drawShape({"type":"circle"
                ,"name":""
                ,"x": this.mapElementList[i].accessPoint.x1
                ,"y": this.mapElementList[i].accessPoint.y1
                ,"radius":"35"
                ,"color":"white"
                }, "accessCircle_"+this.mapElementList[i].id)
                //draw line
                this.drawShape(this.mapElementList[i].accessPoint, "accessLine_"+this.mapElementList[i].id)
            }
        this.drawDynamicElement()
    }

    drawDynamicElement(){
        for(var i=0;i<this.dynamicElementList.length;i++)
            if(this.dynamicElementList[i].shape){
                var stokeWidth = -1;
                var opacity = 0.6;
                if(this.dynamicElementList[i].shape.name == "robot"){
                    var x1 = this.dynamicElementList[i].shape.x1
                    var x2 = this.dynamicElementList[i].shape.x2
                    var y1 = this.dynamicElementList[i].shape.y1
                    var y2 = this.dynamicElementList[i].shape.y2
                    var x =Math.max(x1,x2)-Math.min(x1,x2)
                    var y =Math.max(y1,y2)-Math.min(y1,y2)
                    var size =  Math.sqrt(Math.pow(x,2)+Math.pow(y,2))
                    this.drawShape({"type":"circle"
                    ,"name":""
                    ,"x": x1
                    ,"y": y1
                    ,"radius":size
                    ,"color":"white"
                    }, "circle_"+this.dynamicElementList[i].id)
                    stokeWidth = 100;
                    opacity=1;
                }
                this.drawShape(this.dynamicElementList[i].shape, "shape_"+this.dynamicElementList[i].id, opacity, stokeWidth)
            }
    }

    drawImage(path, id){
        var svg = document.createElementNS("http://www.w3.org/2000/svg", "image");
        svg.setAttribute('href', path);
        svg.setAttribute('x', 0);
        svg.setAttribute('y', 0);
        svg.setAttribute('width', 3000);
        svg.setAttribute('height', 2000);
        svg.id = id;
        if($("#"+id).length)
            $("#"+id).remove()
        $("#liveMap").prepend(svg)
    }

    drawShape(shape, id, opacity=1, strokeWidth=-1){
        var id = "mapElem_"+id
        var svg = null
        if(shape.type == "circle"){
            svg = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            svg.setAttribute('cx', shape.x);
            svg.setAttribute('cy', shape.y);
            svg.setAttribute('r', shape.radius);
            svg.setAttribute('opacity', opacity);
            if(strokeWidth==-1) strokeWidth = 2;
            svg.setAttribute('style', "stroke-width:"+strokeWidth+"; stroke:#000000; fill:"+shape.color+";");
        }
        if(shape.type == "rect"){
            svg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            svg.setAttribute('x', shape.x);
            svg.setAttribute('y', shape.y);
            svg.setAttribute('width', shape.width);
            svg.setAttribute('height', shape.height);
            svg.setAttribute('opacity', opacity);
            if(strokeWidth==-1) strokeWidth = 2;
            svg.setAttribute('style', "stroke-width:"+strokeWidth+"; stroke:#000000; fill:"+shape.color+";");
        }
        if(shape.type == "line"){
            svg = document.createElementNS("http://www.w3.org/2000/svg", "line");
            svg.setAttribute('x1', shape.x1);
            svg.setAttribute('y1', shape.y1);
            svg.setAttribute('x2', shape.x2);
            svg.setAttribute('y2', shape.y2);
            svg.setAttribute('opacity', opacity);
            if(strokeWidth==-1) strokeWidth = 10;
            svg.setAttribute('style', "stroke-width:"+strokeWidth+"; stroke:"+shape.color+";");
        }
        if(shape.type == "poly"){
            svg = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            var str=""
            for(var p=0;p<shape.points.length;p++){
                str += shape.points[p].x + "," + shape.points[p].y
                if(p<shape.points.length-1)
                    str += " "
            }
            svg.setAttribute('points', str);
            svg.setAttribute('opacity', opacity);
            if(strokeWidth==-1) strokeWidth = 2;
            svg.setAttribute('style', "stroke-width:"+strokeWidth+"; stroke:#000000; fill:"+shape.color+";");
        }
        if(svg){
            svg.id = id;
            if($("#"+id).length)
                $("#"+id).remove()
            $("#liveMap").append(svg)
        }
    }
}