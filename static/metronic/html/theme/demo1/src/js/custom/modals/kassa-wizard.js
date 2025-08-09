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

	var client_phone_text = ""
	var client_balance;
	var client_id;
	var formNextbutton;

	var removeWaitIndicator = function () {
		formNextbutton.removeAttribute('data-kt-indicator');
		formNextbutton.disabled = false;
	}

	// Private Functions
	var initStepper = function () {
		// Initialize Stepper
		stepperObj = new KTStepper(stepper);

		// Validation before going to next page
		stepperObj.on('kt.stepper.next', function (stepper) {
			//console.log('stepper.next');

			formNextbutton.disabled = true;
			formNextbutton.setAttribute('data-kt-indicator', 'on');



			// Validate form before change stepper step
			var validator = validations[stepper.getCurrentStepIndex() - 1]; // get validator for currnt step

			if (validator) {
				validator.validate().then(function (status) {
					console.log(stepperObj.getCurrentStepIndex());

					if (status == 'Valid') {
						if(stepperObj.getCurrentStepIndex() === 1) {
							var phone = $('#client_phone').val();
							$.post("/kassa/step1/", {client_phone: phone}, function (data) {
								if (data.status === "ok") {
									client_phone_text = data.phone;
									$('#client_user_info').text(data.user);
									$('#client_user_balance').text(data.user_balance);
									client_balance = parseFloat(data.user_balance);
									client_id = parseInt(data.client_id);
									stepper.goNext();
									KTUtil.scrollTop();
									removeWaitIndicator();
									$('#balance_decrease').focus();
								} else {
									show_message (data.message, "error");
									removeWaitIndicator();
								}
							});
						} else if(stepperObj.getCurrentStepIndex() === 2) {
							if (parseFloat($('#balance_decrease').val()) <= client_balance) {
								// списание баллов
								$.post("/kassa/step2/", {balance_decrease: $('#balance_decrease').val(), client_id: client_id}, function (data) {
									if (data.status === "ok") {
										stepper.goNext();
										KTUtil.scrollTop();
										removeWaitIndicator();
									} else {
										show_message (data.message, "error");
										removeWaitIndicator();
									}
								});
							} else {
								show_message ("Баланс клиента меньше введенного", "error");
								removeWaitIndicator();
							}
						}
					} else {
						show_message ("Обнаружены ошибки заполнения.", "error", function () {
							KTUtil.scrollTop();
						});
						removeWaitIndicator();
					}
				});
			} else {
				stepper.goNext();
				KTUtil.scrollTop();
				removeWaitIndicator();
			}
		});

		// Prev event
		stepperObj.on('kt.stepper.previous', function (stepper) {
			//console.log('stepper.previous');
			removeWaitIndicator();
			stepper.goPrevious();
			KTUtil.scrollTop();
		});

		stepperObj.on("kt.stepper.changed", function() {
			if(stepperObj.getCurrentStepIndex() === 2)
				$('#balance_decrease').focus();
		});
	}

	var handleForm = function() {
		formSubmitButton.addEventListener('click', function (e) {
			// Prevent default button action
			e.preventDefault();

			// Disable button to avoid multiple click 
			formSubmitButton.disabled = true;

			// Show loading indication
			formSubmitButton.setAttribute('data-kt-indicator', 'on');

			$.post("/kassa/step3/", {sms_code: $('#sms_code').val(), client_id: client_id}, function (data) {
				if (data.status === "ok") {
					show_message ("Баллы успешно списаны", "success", function () {
						top.location.href = top.location.href;
					});
				} else {
					show_message (data.message, "error");

					formSubmitButton.removeAttribute('data-kt-indicator');
					formSubmitButton.disabled = false;
				}
			});

			// Simulate form submission
			/*setTimeout(function() {
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
			}, 2000);*/
		});



	}

	var initValidation = function () {
		// Init form validation rules. For more info check the FormValidation plugin's official documentation:https://formvalidation.io/
		// Step 1
		validations.push(FormValidation.formValidation(
			form,
			{
				fields: {
					client_phone: {
						validators: {
							notEmpty: {
								message: 'Нужно ввести телефон'
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
					'balance_decrease': {
						validators: {
							notEmpty: {
								message: 'Количество баллов должно быть больше 0'
							},
							numeric: {
								message: 'Количество баллов должно быть числом'
							},
							greaterThan: {
								min: 1,
								message: 'Количество баллов должно быть больше 0'
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

		// Step 3
		validations.push(FormValidation.formValidation(
			form,
			{
				fields: {
					'sms_code': {
						validators: {
							notEmpty: {
								message: 'Нужно ввести код из СМС клиента'
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
			formNextbutton = stepper.querySelector('[data-kt-stepper-action="next"]');

			initStepper();
			initValidation();
			handleForm();
		}
	};
}();

// On document ready
KTUtil.onDOMContentLoaded(function() {
    KTCreateAccount.init();

	Inputmask({
		"mask" : "+7(999) 999-9999"
	}).mask("#client_phone");
});