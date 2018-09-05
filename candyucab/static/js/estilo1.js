$(document).ready(function () {
   $(".closebtn").on("click", function () {
       $("#myNav").css('width', '0%');
   });

   $(".open_btn").on("click", function () {
      $("#myNav").css('width', '100%');
   });

   $(".entrada").on("click", function () {
      $("#id01").css('display', 'block');
   });

   $(".close").on("click", function () {
       $("#id01").css('display', 'none');
   });

    $(".registro").on("click", function () {
        $("#id02").css('display', 'block');
    });

    $(".close2").on("click", function () {
        $("#id02").css('display', 'none');
    });

});
