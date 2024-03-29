/* ************************************************************************** */
/*                                                                            */
/*                                                        ::::::::            */
/*   saver.js                                           :+:    :+:            */
/*                                                     +:+                    */
/*   By: fbes <fbes@student.codam.nl>                 +#+                     */
/*                                                   +#+                      */
/*   Created: 2022/10/16 02:22:25 by fbes          #+#    #+#                 */
/*   Updated: 2023/03/17 22:03:30 by fbes          ########   odam.nl         */
/*                                                                            */
/* ************************************************************************** */

const saveContainer = document.getElementById('save-container');

function showSaveButton() {
	if (!saveContainer.classList.contains('show')) {
		console.log('Showing save button');
		saveContainer.classList.add('show');
		window.onbeforeunload = showUnsavedChangesWarning;
	}
	return true;
}

function hideSaveButton() {
	if (saveContainer.classList.contains('show')) {
		console.log('Hiding save button');
		saveContainer.classList.remove('show');
		window.onbeforeunload = null;
	}
	return false;
}

// function that checks if there are unsaved changes and shows the save button if so
// also returns true if shown, false if not
function checkShowSaveButton() {
	for (const [key, value] of Object.entries(mod_user_settings)) {
		if (value != user_settings[key]) {
			return showSaveButton();
		}
	}
	return hideSaveButton();
}

function showUnsavedChangesWarning() {
	return 'You have unsaved changes! Are you sure you want to leave this page? The save button is in the top left corner.';
}

function genericSaveError(err) {
	console.error('Error while saving user settings:', err);
	alert('Error while saving user settings: ' + err);
	loadingOverlay.hide();
}

// save button event listener
document.getElementById('save-btn').addEventListener('click', function(ev) {
	console.log('Saving user settings:', mod_user_settings);

	// show loading screen
	loadingOverlay.show();

	// remove all previous form errors
	const formErrors = document.querySelectorAll('.form-error');
	for (const formError of formErrors) {
		formError.remove();
	}
	const optionContainers = document.querySelectorAll('.option-container.has-error');
	for (const optionContainer of optionContainers) {
		optionContainer.classList.remove('has-error');
	}


	// convert the modified user settings to a FormData object
	const formData = new FormData();
	formData.append('ext_version', document.getElementById('ext_version_input').value);
	for (const key in mod_user_settings) {
		formData.append(key, mod_user_settings[key]);
	}
	const fileInputs = document.querySelectorAll('.option-container input[type="file"]');
	for (const fileInput of fileInputs) {
		if (fileInput.files.length > 0) {
			formData.append(fileInput.name, fileInput.files[0]);
		}
	}

	// send modified user settings to server
	const saveReq = new XMLHttpRequest();
	saveReq.open('POST', window.location.pathname + '/save');
	saveReq.addEventListener('load', function() {
		if (this.status === 413) {
			console.error('Uploaded file is too large: HTTP 413');
			// This error is generated by nginx, so there won't be a JSON to parse... Thus, we throw the error message from the front-end.
			return genericSaveError('File too large');
		}

		try {
			const response = JSON.parse(this.responseText);
			console.log('Save request response:', response);

			if (response.type === 'success') {
				// fix new_uploads in user_settings
				for (const setting_key in mod_user_settings) {
					if (mod_user_settings[setting_key].startsWith('new_upload-')) {
						console.log('Fixing new_upload for ' + setting_key + ' in mod_user_settings (was ' + mod_user_settings[setting_key] + ', now ' + response['updated_settings'][setting_key] + ')');
						mod_user_settings[setting_key] = response['updated_settings'][setting_key].toString();
					}
				}

				// overwrite local user settings (in this webpage)
				user_settings = JSON.parse(JSON.stringify(mod_user_settings));

				// send modified user settings to extension (in the format of this webpage)
				const iSettingsChangedPFEvent = new Event('iSettingsChangedPageFormat', { detail: { old_settings: user_settings, new_settings: mod_user_settings } } );
				document.dispatchEvent(iSettingsChangedPFEvent);

				// send modified user settings to extension (in the format of the server)
				const iSettingsChangedSFEvent = new Event('iSettingsChangedServerFormat', { detail: { updated_settings: response['updated_settings'] } } );
				document.dispatchEvent(iSettingsChangedSFEvent);

				// update UI
				hideSaveButton();
				populateOptions();
				loadingOverlay.hide();

				// remove all files from file inputs
				for (const fileInput of fileInputs) {
					fileInput.value = '';
				}
			}
			else {
				if ('form_errors' in response) {
					for (const [key, value] of Object.entries(response.form_errors)) {
						const optionContainer = document.querySelector('.option-container#'+key) || document.querySelector("input[name='" + key + "']").closest('.option-container');
						if (!optionContainer) {
							console.error('Option container not found for key', key);
							continue;
						}

						// mark the optioncontainer as invalid
						optionContainer.classList.add('has-error');

						// create form error element
						const formError = document.createElement('p');
						formError.classList.add('form-error');
						formError.innerText = value;

						// get the first element describing the option (either p or h4, if p does not exist it falls back to h4)
						const optionContainerLastText = optionContainer.querySelectorAll('p, h4');
						if (optionContainerLastText.length == 0) {
							console.error('Option container text element not found for key', key);
							continue;
						}

						// then try to insert the error element after this description element
						const lastOptionDescription = optionContainerLastText[optionContainerLastText.length - 1];
						if (lastOptionDescription.nextSibling) {
							optionContainer.insertBefore(formError, lastOptionDescription.nextSibling);
						}
						else {
							console.warn("Option container " + key + " has no option selector or equivalent element");
							optionContainer.appendChild(formError); // this should actually never happen
						}
					}
				}
				genericSaveError(response.message);
			}
		}
		catch (err) {
			console.log('Save request response:', this.responseText);
			genericSaveError(err);
		}
	});
	saveReq.addEventListener('error', function(err) {
		genericSaveError(err);
	});
	saveReq.send(formData);
});

// add margin to last option container when scrollbar is present
function addWhitespaceOnScrollbar() {
	const main = document.querySelector('main');
	let lastOptionContainer = document.querySelector('.option-container:last-child');
	if (!lastOptionContainer) {
		return false;
	}
	if (lastOptionContainer.id == 'ext_version') {
		lastOptionContainer = lastOptionContainer.previousElementSibling;
	}
	lastOptionContainer.style.marginBottom = '0';
	if (main.scrollHeight > main.clientHeight) {
		lastOptionContainer.style.marginBottom = '256px';
		return true;
	}
	return false;
}
window.addEventListener('resize', addWhitespaceOnScrollbar);
addWhitespaceOnScrollbar();
