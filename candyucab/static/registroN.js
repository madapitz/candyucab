let estados = document.getElementById('estados');
let municipios = document.getElementById('municipios');
let parroquias = document.getElementById('parroquias');
estados.onchange=function(){
  estado = estados.value;
  fetch('/municipio/'+ estado).then(function(response){
    response.json().then(function(data){
      let optionHTML = '';
      optionHTML+= '<option value="seleccion">Seleccione un municipio</option>';
      for (let municipio of data.municipios){
          optionHTML+= '<option value"'+ municipio[0]+'">' + municipio[2]+'</option>';
      }
      municipios.innerHTML = optionHTML;
      municipios.onchange=function(){
        municipio = municipios.value;
        estado = estados.value;
        fetch('/parroquia/'+ municipio+ '/'+ estado).then(function(response){
          response.json().then(function(data){
            let optionHTML = '';
            optionHTML+= '<option value="seleccion">Seleccione una parroquia</option>';
            for (let parroquia of data.parroquias){
                optionHTML+= '<option value"'+ parroquia[0]+'">' + parroquia[2]+'</option>';
            }
            parroquias.innerHTML = optionHTML;
          });
          });
        }
    });

    });
  }
