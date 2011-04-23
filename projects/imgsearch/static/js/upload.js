$(document).ready(function(){
    $("#spinner").hide();
    $("#sub").click(function(){
        if($("#img").val() == '' && $("#vid").val() == ''){
            alert("Must select an image or video to upload!");
        }
        else if ($("#title").val() == '' || $("#texta").val() == ''){
            alert("Must provide both title and description!");
        }
        else {
            $("#spinner").show();
            $("#i").submit();
        }
    });
});
