
      let estados = document.getElementById('estados1');
      let municipios = document.getElementById('municipios1');
      let parroquias = document.getElementById('parroquias1');
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

      let estados2 = document.getElementById('estados2');
      let municipios2 = document.getElementById('municipios2');
      let parroquias2 = document.getElementById('parroquias2');
      estados2.onchange=function(){
        estado = estados2.value;
        fetch('/municipio/'+ estado).then(function(response){
          response.json().then(function(data){
            let optionHTML = '';
            optionHTML+= '<option value="seleccion">Seleccione un municipio</option>';
            for (let municipio of data.municipios){
                optionHTML+= '<option value"'+ municipio[0]+'">' + municipio[2]+'</option>';
            }
            municipios2.innerHTML = optionHTML;
            municipios2.onchange=function(){
              municipio = municipios2.value;
              estado = estados2.value;
              fetch('/parroquia/'+ municipio+ '/'+ estado).then(function(response){
                response.json().then(function(data){
                  let optionHTML = '';
                  optionHTML+= '<option value="seleccion">Seleccione una parroquia</option>';
                  for (let parroquia of data.parroquias){
                      optionHTML+= '<option value"'+ parroquia[0]+'">' + parroquia[2]+'</option>';
                  }
                  parroquias2.innerHTML = optionHTML;
            });
            });
          }
          });
          });
        }


