function show_message (msg, icon, callback_function=function(){}) {
    Swal.fire({
    html: msg,
    icon: icon,
    buttonsStyling: false,
    confirmButtonText: "Закрыть",
    customClass: {
        confirmButton: "btn btn-primary"
    }
    }).then(callback_function);
}

function show_confirm_message (msg, confirmButtonText, cancelButtonText, resultURL) {
    Swal.fire({
        title: 'Вы уверены?',
        text: msg,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        cancelButtonText: cancelButtonText,
        confirmButtonText: confirmButtonText
    }).then((result) => {
        if (result.isConfirmed) {
            top.location.href = resultURL;
        }
    });
}