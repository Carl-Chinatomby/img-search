$(document).ready(function(){
    $("#spinner").hide();
    $("#sub").click(function(){
        $("#spinner").show();
        
        $("#upload").css("z-index", "1");
        $("#i").submit();
    });
});
