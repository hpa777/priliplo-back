"use strict";

// Class definition
var KTCreateAccount = function () {
	// Elements
	var modal;
	var modalEl;

	var stepper;
	var form;
	var formSubmitButton;

	// Variables
	var stepperObj;
	var validations = [];

	// Private Functions
	var initStepper = function () {
		// Initialize Stepper
		stepperObj = new KTStepper(stepper);

		// Validation before going to next page
		stepperObj.on('kt.stepper.next', function (stepper) {
			//console.log('stepper.next');

			// Validate form before change stepper step
			var validator = validations[stepper.getCurrentStepIndex() - 1]; // get validator for currnt step

			if (validator) {
				validator.validate().then(function (status) {
					// console.log('validated!');

					if (status == 'Valid') {
						stepper.goNext();

						KTUtil.scrollTop();
					} else {
						Swal.fire({
							text: "Обнаружено несколько ошибок. Попробуйте еще раз",
							icon: "error",
							buttonsStyling: false,
							confirmButtonText: "Продолжить",
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
			//console.log('stepper.previous');

			stepper.goPrevious();
			KTUtil.scrollTop();
		});

		stepperObj.on("kt.stepper.changed", function() {
			if(stepperObj.getCurrentStepIndex() === 2) {
				var account_type = document.querySelector('input[name="account_type"]:checked').value;
				var company_name_input = document.querySelector('input[name="company_name"]');
				var company_name_container = document.getElementById("company_name_container");

				if (account_type === 'client') {
					document.getElementById("name_label").textContent = "Как к вам обращаться?";
					company_name_container.classList.add("d-none");
					company_name_input.value = "-";

					validations[1].removeField('company_name')
				} else {
					document.getElementById("name_label").textContent = "Контактное лицо";
					company_name_container.classList.remove("d-none");
					company_name_input.value = "";
					validations[1].addField('company_name',{
							validators: {
								notEmpty: {
									message: 'Введите название организации'
								}
							}
						});

				}
			}
		});
	}

	var handleForm = function () {
		formSubmitButton.addEventListener('click', function (e) {
			// Prevent default button action
			e.preventDefault();

			//console.log("submit");
			// Validation before going to next page
			//stepperObj.on('kt.stepper.next', function (stepper) {
			// 	console.log('stepper.next');

				// Validate form before change stepper step
				var validator = validations[1]; // get validator for currnt step
				// console.log("1");
				if (validator) {
					validator.validate().then(function (status) {
						// console.log(2);
						if (status == 'Valid') {
							// console.log(3);

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
			//});
			// Simulate form submission
			/*			setTimeout(function() {
                            // Hide loading indication
                            formSubmitButton.removeAttribute('data-kt-indicator');

                            // Enable button
                            formSubmitButton.disabled = false;

                            // Show popup confirmation. For more info check the plugin's official documentation: https://sweetalert2.github.io/
                            Swal.fire({
                                text: "Form has been successfully submitted!",
                                icon: "success",
                                buttonsStyling: false,
                                confirmButtonText: "Ok, got it!",
                                customClass: {
                                    confirmButton: "btn btn-primary"
                                }
                            }).then(function (result) {
                                if (result.isConfirmed) {
                                    if (modal) {
                                        modal.hide(); // close modal
                                    }
                                    //form.submit(); // Submit form
                                }
                            });
                        }, 2000);  */
		});
	}

		// Expiry month. For more info, plase visit the official plugin site: https://select2.org/
		// $(form.querySelector('[name="card_expiry_month"]')).on('change', function() {
		//     // Revalidate the field when an option is chosen
		//     validations[3].revalidateField('card_expiry_month');
		// });


		var initValidation = function () {
			// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
			// Step 1
			validations.push(FormValidation.formValidation(
				form,
				{
					fields: {
						account_type: {
							validators: {
								notEmpty: {
									message: 'Нужно выбрать тип аккаунта'
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
						'company_name': {
							validators: {
								notEmpty: {
									message: 'Введите название организации'
								}
							}
						},
						'name': {
							validators: {
								notEmpty: {
									message: 'Введите как мы можем к вам обращаться'
								}
							}
						},
						'phone': {
							validators: {
								notEmpty: {
									message: 'Введите свой номер телефона'
								}
							}
						},
						'password': {
							validators: {
								notEmpty: {
									message: 'Заполните поле пароль'
								}

							}

						},
						'password_confirm': {
							validators: {
								notEmpty: {
									message: 'Пароль нужно ввести два раза'
								},
								identical: {
									compare: function () {
										return form.querySelector('[name="password"]').value;
									},
									message: 'Пароль и его подтверждение не совпадают'
								}
							}
						},
						'email': {
							validators: {
								notEmpty: {
									message: 'Заполните поле email'
								},
								emailAddress: {
									message: 'Значение не похоже на email адрес'
								}
							}
						}
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


		return {
			// Public Functions
			init: function () {
				// Elements
				modalEl = document.querySelector('#kt_modal_create_account');

				if (modalEl) {
					modal = new bootstrap.Modal(modalEl);
				}

				stepper = document.querySelector('#kt_create_account_stepper');

				form = stepper.querySelector('#kt_create_account_form');
				formSubmitButton = stepper.querySelector('[data-kt-stepper-action="submit"]');

				initStepper();
				initValidation();
				handleForm();
			},

			goLastStep: function () {
				stepperObj.goLast();
			}
		};
	}();

// On document ready
	KTUtil.onDOMContentLoaded(function () {
		KTCreateAccount.init();

		Inputmask({
			"mask": "+7(999) 999-9999"
		}).mask("#phone");

		Inputmask({
			mask: "*{1,20}[.*{1,20}][.*{1,20}][.*{1,20}]@*{1,20}[.*{2,6}][.*{1,2}]",
			greedy: false,
			onBeforePaste: function (pastedValue, opts) {
				pastedValue = pastedValue.toLowerCase();
				return pastedValue.replace("mailto:", "");
			},
			definitions: {
				"*": {
					validator: '[0-9A-Za-z!#$%&"*+/=?^_`{|}~\-]',
					cardinality: 1,
					casing: "lower"
				}
			}
		}).mask("#kt_inputmask_8");
	});

function goLastSingnUpStep () {
	KTCreateAccount.goLastStep();
}