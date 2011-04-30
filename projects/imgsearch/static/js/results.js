$(document).ready(function(){
    
    var res = {{ histograms }};
    var data1.push(res[0]);
    var data2.push(res[1]);



    var graph = Raphael("stat", 168, 148);
    var graph2 = Raphael("stat2", 168, 148);

    var fin = function () {
        this.flag = graph.g.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
    }
    var fout = function () {
        this.flag.animate({opacity: 0}, 300, function () {this.remove();});
    }
    var fin2 = function () {
        this.flag = graph.g.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
    }
    var fout2 = function () {
        this.flag.animate({opacity: 0}, 300, function () {this.remove();});
    }

    //graph.g.text(70,10, "(Hover Over Bar Values)");
    graph.g.barchart(5, 5, 168, 158, data1, 0, {type: "sharp"}).hover(fin, fout);
    graph2.g.barchart(5, 5, 168, 158, data2, 0, {type: "sharp"}).hover(fin2, fout2);
});


