$(document).ready(function(){
    $("#image").hide();
    $("#left").click(function(){
        if( $("#left").is(":checked") ){
            $("#image").show("slow");
        }
        else {
            $("#image").hide("slow");
        }
    });
    $("#right").click(function(){
        if( $("#right").is(":checked") ){
            $("#image").hide("slow");
        }
        else {
            $("#image").show("slow");
        }
    });

    $("#sub").click(function(){
       
    });

});
