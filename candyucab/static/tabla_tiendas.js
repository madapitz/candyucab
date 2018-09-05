$('document').ready(function () {
   $.getJSON("/nombre_tienda", function (result) {
       $.each(result, function (i, field) {
           $.each(field, function (j, campo) {
               $('#cuerpot').append(
               "<tr id="+"t"+campo[3] +">" +
               "<td><a class='tabla_link' href='/inventario/"+campo[3]+"/"+campo[0]+"'>" + campo[0] +"</td>"+
               "<td>" + campo[1] +"</td>"+
               "<td>" + campo[2] +"</td>"+
               "</tr>"
           );
           });
       });
   });
});