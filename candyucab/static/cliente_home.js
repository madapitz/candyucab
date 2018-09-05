$(document).ready(function () {
   $(".closebtn").on("click", function () {
       $("#myNav").css('width', '0%');
   });

   $(".open_btn").on("click", function () {
      $("#myNav").css('width', '100%');
   });

});