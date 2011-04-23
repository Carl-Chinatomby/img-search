$(document).ready(function(){
    $("#image").hide();
    $("#spinner").hide();
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
        
        if ($("#left").is(":checked") && $("#img_file").val() == ''){
            alert("Need to specify a file to search by!");
        }
        else if ($("#search_box").val() == '' && $("#img_file").val() == ''){
            alert("Please specify at least on search parameter!");
            return;
        }
        else {  
            $("#spinner").show();
            $("#txt").submit();
        }
    });

});
