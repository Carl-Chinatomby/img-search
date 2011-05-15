$(document).ready(function(){
    $("#image").hide();
    $("#video").hide();
    $("#spinner").hide();
    $("#spinner2").hide();
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

    $("#left_vid").click(function(){
        if( $("#left_vid").is(":checked") ){
            $("#video").show("slow");
        }
        else {
            $("#video").hide("slow");
        }
    });
    $("#right_vid").click(function(){
        if( $("#right_vid").is(":checked") ){
            $("#video").hide("slow");
        }
        else {
            $("#video").show("slow");
        }
    });

    $("#sub").click(function(){
        if( $("#left").is(":checked") && $("#left_vid").is(":checked")) {
            alert("Video or Image, not both!");
        }
        else if ($("#left").is(":checked") && $("#img_file").val() == ''){
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
