function toast_error(text) {
    $.toast({
        heading: "Ha ocurrido un error!",
        text: text,
        icon: 'error'
    })
}

function message_success_reload(message) {
    Swal.fire({
        position: 'top-end',
        icon: 'success',
        title: message,
        showConfirmButton: false,
    })

    // Ocultar el mensaje después de 1 segundo
    setTimeout(function () {
        location.reload();
    }, 200);
}