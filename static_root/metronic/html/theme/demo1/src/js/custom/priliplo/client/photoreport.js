"use strict";

// Class definition
var KTProjectSettings = function () {

    // Private functions
    var handleForm = function () {
        // Form validation
        var validation;
        var _form = document.getElementById('kt_photoreport_form');
        var submitButton = _form.querySelector('#kt_photoreport_form_submit');
        var kt_photoreport_form_hidden_id = document.getElementById('kt_photoreport_form_hidden_id');

        // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
        if (kt_photoreport_form_hidden_id) {
            validation = FormValidation.formValidation(
                _form,
                {
                    fields: {
                        odometer: {
                            validators: {
                                notEmpty: {
                                    message: 'Необходимо заполнить это поле'
                                }
                            }
                        },
                    },
                    plugins: {
                        trigger: new FormValidation.plugins.Trigger(),
                        submitButton: new FormValidation.plugins.SubmitButton(),
                        bootstrap: new FormValidation.plugins.Bootstrap5({
                            rowSelector: '.fv-row',
                        }),
                    }
                }
            );
        }
        else {
            validation = FormValidation.formValidation(
                _form,
                {
                    fields: {
                        odometer: {
                            validators: {
                                notEmpty: {
                                    message: 'Необходимо заполнить это поле'
                                }
                            }
                        },

                        photoreport_odometer: {
                            validators: {
                                notEmpty: {
                                    message: 'Необходимо заполнить это поле'
                                },
                                // file: {
                                //     extension: 'jpeg,jpg,png',
                                //     type: 'image/jpeg,image/png',
                                //     maxSize: 2097152,   // 2048 * 1024
                                //     message: 'Выбранный файл не подходит'
                                // }
                            }
                        },
                        photoreport_sticker: {
                            validators: {
                                notEmpty: {
                                    message: 'Необходимо заполнить это поле'
                                }
                            }
                        },
                    },
                    plugins: {
                        trigger: new FormValidation.plugins.Trigger(),
                        submitButton: new FormValidation.plugins.SubmitButton(),
                        //defaultSubmit: new FormValidation.plugins.DefaultSubmit(), // Uncomment this line to enable normal button submit after form validation
                        bootstrap: new FormValidation.plugins.Bootstrap5({
                            rowSelector: '.fv-row',
                            defaultMessageContainer: false,
                        }),
                        message: new FormValidation.plugins.Message({
                            clazz: 'fv-plugins-message-container invalid-feedback',
                            // container: '.error_message',
                            container: function (field, element) {
                                if (field == 'photoreport_odometer') {
                                    return document.getElementById('error_message_photoreport_odometer');
                                } else if (field == 'photoreport_sticker') {
                                    return document.getElementById('error_message_photoreport_sticker');
                                } else {
                                    return element.nextElementSibling;
                                }
                                // return FormValidation.utils.closest(element, '.fl');


                            },
                        }),
                        // icon: new FormValidation.plugins.Icon({
                        //     valid: 'fa fa-check',
                        //     invalid: 'fa fa-times',
                        //     validating: 'fa fa-refresh'
                        // }
                    }
                }
            );
        }

        submitButton.addEventListener('click', function (e) {
            e.preventDefault();

            validation.validate().then(function (status) {
                if (status == 'Valid') {
                    _form.submit();
                } else {
                    swal.fire({
                        text: "Обнаружено несколько ошибок при заполнении формы",
                        icon: "error",
                        buttonsStyling: false,
                        confirmButtonText: "OK",
                        customClass: {
                            confirmButton: "btn fw-bold btn-light-primary"
                        }
                    });
                }
            });
        });
    }

    // Public methods
    return {
        init: function () {
            handleForm();
        }
    }
}();


// On document ready
KTUtil.onDOMContentLoaded(function() {
    KTProjectSettings.init();
});
