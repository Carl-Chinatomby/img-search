$(document).ready(function(){
    
    var graph = Raphael("stat", 158, 148);
    var fin = function () {
        this.flag = graph.g.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
    }
    var fout = function () {
        this.flag.animate({opacity: 0}, 300, function () {this.remove();});
    }

    graph.g.text(70,10, "(Hover Over Bar Values)");
    graph.g.barchart(0, 0, 158, 158,[[55, 20, 13, 32, 5, 1, 2, 10,13, 32, 5, 1, 2, 10]], 0, {type: "sharp"}).hover(fin, fout);
});


