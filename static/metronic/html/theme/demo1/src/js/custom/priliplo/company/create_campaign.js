"use strict";

// Class definition
var KTProjectSettings = function () {

    // Private functions
    var handleForm = function () {
        // Init Datepicker --- For more info, please check Flatpickr's official documentation: https://flatpickr.js.org/
        $("#kt_datepicker_1").flatpickr();

        // Form validation
        var validation;
        var _form = document.getElementById('create_campaign_form');
        var submitButton = _form.querySelector('#create_campaign_form_submit');

        // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
        validation = FormValidation.formValidation(
            _form,
            {
                fields: {
                    title: {
                        validators: {
                            notEmpty: {
                                message: 'Необходимо заполнить это поле'
                            }
                        }
                    },

                    short_description: {
                        validators: {
                            notEmpty: {
                                message: 'Необходимо заполнить это поле'
                            }
                        }
                    },
                    sticker_text: {
                        validators: {
                            notEmpty: {
                                message: 'Необходимо заполнить это поле'
                            }
                        }
                    },
                    award: {
                        validators: {
                            notEmpty: {
                                message: 'Необходимо заполнить это поле'
                            }
                        }
                    },
                    quota: {
                        validators: {
                            notEmpty: {
                                message: 'Необходимо заполнить это поле'
                            }
                        }
                    },
                    end_date: {
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
                        rowSelector: '.fv-row'
                    })
                }
            }
        );

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

    $("#quota").change(function() {
        // var cost = $('#campaign_cost');
        var quota = $(this).val();
        if (quota !== '')
            var calculate = ((parseFloat($('#advertiser_settings_period_cost').val()) * 3) + parseFloat($('#advertiser_settings_sticking_cost').val())) * parseFloat(quota) + parseFloat($('#advertiser_settings_logo_cost').val());
        else
            var calculate = 0;

        $('.campaign_cost').text(calculate);
    });
    $("#quota").keyup(function(){$(this).blur(); $(this).focus();});

    $("#award").change(function() {
        var award = $(this).val();
        if (quota !== '')
            var calculate = (award * 6) + " бонусов за 84 дня";
        else
            var calculate = 0 + " бонусов за 84 дня";

        $('#award_hint_text').text(calculate);
    });
    $("#award").keyup(function(){$(this).blur(); $(this).focus();});

});
