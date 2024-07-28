const eliminar_con_ajax = (url) => {
    Swal.fire({
        title: '¿Estas seguro de eliminar este registro?',
        text: "No podrás revertir esto.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: '¡Sí, bórralo!'
    }).then((result) => {
        if (result.isConfirmed) {
            SendPostRequest(url).then((data) => {
                if (data.success) {
                    message_success_reload(data.message);
                } else {
                    alert(data.message);
                }
            }).catch((error) => {
                toast_error("Error en la solicitud AJAX.");
            });
        }
    });
}


// Función para hacer una solicitud POST a Django y devolver una Promesa
async function SendPostRequest(url, formData) {
    return new Promise((resolve, reject) => {
        fetch(url, {
            method: 'POST',
            body: formData,  // Utiliza el objeto FormData que incluye los archivos
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),  // Agrega el token CSRF a los encabezados
            },
        }).then((response) => {
            if (!response.ok) {
                reject('Error en la solicitud: ' + response.statusText);
            }
            return response.json();  // Parsea la respuesta JSON
        }).then((data) => {
            resolve(data);  // Resuelve la Promesa con los datos recibidos
        }).catch((error) => {
            reject('Error en la solicitud: ' + error);
        });
    });
}

async function SendGetRequest(url) {
    return new Promise((resolve, reject) => {
        fetch(url, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),  // Agrega el token CSRF a los encabezados
            },
        }).then((response) => {
            if (!response.ok) {
                reject('Error en la solicitud: ' + response.statusText);
            }
            return response.json();  // Parsea la respuesta JSON
        }).then((data) => {
            resolve(data);  // Resuelve la Promesa con los datos recibidos
        }).catch((error) => {
            reject('Error en la solicitud: ' + error);
        });
    });
}


// Función para obtener el valor de una cookie por su nombre
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return parts.pop().split(';').shift();
    }
}