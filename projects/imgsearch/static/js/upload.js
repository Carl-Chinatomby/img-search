$(document).ready(function(){
    $("#spinner").hide();
    $("#format").click(function(){
        alert("Zipped folder must contain clip folders enumerated starting from 0,"+
              "such as: clip0, clip1, clip2, etc.  \n\nSimilarly, frames inside clip folders " +
              "must be named: frame0, frame1, frame2, etc" );
    });
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
