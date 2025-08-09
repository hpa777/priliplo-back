"use strict";






// Class definition
var KTProjectSettings = function () {
    var modal;
    var modalEl;

    var stepper;
    var form;
    var formSubmitButton;

    // Variables
    var stepperObj;
    var validations = [];
    var calculate = 0;

    // Private functions
    var initStepper = function () {
        $("#kt_datepicker_1").flatpickr();
        // Initialize Stepper
        stepperObj = new KTStepper(stepper);

        // Validation before going to next page
        stepperObj.on('kt.stepper.next', function (stepper) {
            // console.log('stepper.next');
            // console.log(stepper.getCurrentStepIndex());

            // Validate form before change stepper step
            var validator = validations[stepper.getCurrentStepIndex() - 1]; // get validator for currnt step

            if (validator) {
                validator.validate().then(function (status) {
                    // console.log('validated!');
                    // console.log(status);

                    if (status == 'Valid') {
                        if(stepperObj.getCurrentStepIndex() === 1) {
                            let advertiser_balance = parseFloat($('#advertiser_balance').val());
                            if (advertiser_balance > KTProjectSettings.calculate) {
                                stepper.goNext();
                                KTUtil.scrollTop();
                            } else {
                                show_message ("На балансе не достаточно средств для создания акции", "error");
                            }
                        } else {
                            stepper.goNext();
                            KTUtil.scrollTop();
                        }

                    } else {
                        Swal.fire({
                            text: "Заполните все обязательные поля",
                            icon: "error",
                            buttonsStyling: false,
                            confirmButtonText: "OK",
                            customClass: {
                                confirmButton: "btn btn-light"
                            }
                        }).then(function () {
                            KTUtil.scrollTop();
                        });
                    }
                });
            } else {
                stepper.goNext();
                KTUtil.scrollTop();
            }
        });

        // Prev event
        stepperObj.on('kt.stepper.previous', function (stepper) {
            // console.log('stepper.previous');

            stepper.goPrevious();
            KTUtil.scrollTop();
        });
    }

    /*
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
    */


    var initValidation = function () {
        // Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
        // Step 1
        validations.push(FormValidation.formValidation(
            form,
            {
                fields: {
                    quota: {
                        validators: {
                            notEmpty: {
                                message: 'Необходимо указать количество автомобилей которые вы можете принять в акцию'
                            }
                        }
                    }
                },
                plugins: {
                    trigger: new FormValidation.plugins.Trigger(),
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
                    })
                }
            }
        ));

         // Step 2
        validations.push(FormValidation.formValidation(
            form,
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
                    // Bootstrap Framework Integration
                    bootstrap: new FormValidation.plugins.Bootstrap5({
                        rowSelector: '.fv-row',
                        eleInvalidClass: '',
                        eleValidClass: ''
                    })
                }
            }
        ));
    }

    var handleForm = function () {
        formSubmitButton.addEventListener('click', function (e) {
            // Prevent default button action
            e.preventDefault();
            // Validate form before change stepper step
            var validator = validations[1]; // get validator for currnt step
            if (validator) {
                validator.validate().then(function (status) {

                    if (status == 'Valid') {
                        validator.validate().then(function (status) {
                            // Disable button to avoid multiple click
                            formSubmitButton.disabled = true;
                            // Show loading indication
                            formSubmitButton.setAttribute('data-kt-indicator', 'on');
                            form.submit();
                        });
                    } else {
                        show_message("Обнаружены ошибки заполнения.", "error", function () {
                            KTUtil.scrollTop();
                        });
                    }
                });
            }

        });
    }

    // Public methods
    return {
        init: function () {
            // modalEl = document.querySelector('#kt_modal_create_account');
            //
            // if (modalEl) {
            //     modal = new bootstrap.Modal(modalEl);
            // }

            stepper = document.querySelector('#kt_create_account_stepper');

            form = stepper.querySelector('#create_campaign_form');
            formSubmitButton = stepper.querySelector('[data-kt-stepper-action="submit"]');

            initStepper();
            initValidation();
            handleForm();
            console.log(stepper);
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
            KTProjectSettings.calculate = ((parseFloat($('#advertiser_settings_period_cost').val()) * 3) + parseFloat($('#advertiser_settings_sticking_cost').val())) * parseFloat(quota) + parseFloat($('#advertiser_settings_logo_cost').val());
        else
            KTProjectSettings.calculate = 0;

        $('.campaign_cost').text(KTProjectSettings.calculate);
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
