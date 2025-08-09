function show_message (msg, icon) {
    Swal.fire({
    html: msg,
    icon: "error",
    buttonsStyling: false,
    confirmButtonText: "Закрыть",
    customClass: {
        confirmButton: "btn btn-primary"
    }
    });
}
