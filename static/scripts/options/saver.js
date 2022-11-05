/* ************************************************************************** */
/*                                                                            */
/*                                                        ::::::::            */
/*   saver.js                                           :+:    :+:            */
/*                                                     +:+                    */
/*   By: fbes <fbes@student.codam.nl>                 +#+                     */
/*                                                   +#+                      */
/*   Created: 2022/10/16 02:22:25 by fbes          #+#    #+#                 */
/*   Updated: 2022/11/05 14:09:04 by fbes          ########   odam.nl         */
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

// save button event listener
document.getElementById('save-btn').addEventListener('click', function(ev) {
	console.log('Saving user settings:', mod_user_settings);

	// convert the modified user settings to a FormData object
	const formData = new FormData();
	for (const key in mod_user_settings) {
		formData.append(key, mod_user_settings[key]);
	}

	// send modified user settings to server
	const saveReq = new XMLHttpRequest();
	saveReq.open('POST', window.location.pathname + '/save');
	saveReq.addEventListener('load', function() {
		console.log('Save request response:', this.responseText);
		try {
			const response = JSON.parse(this.responseText);
			if (response.status === 'success') {
				// overwrite local user settings
				user_settings = JSON.parse(JSON.stringify(mod_user_settings));

				// send modified user settings to extension
				const iSettingsChangedEvent = new Event('iSettingsChanged', { detail: { old_settings: user_settings, new_settings: mod_user_settings } } );
				document.dispatchEvent(iSettingsChangedEvent);

				// update UI
				hideSaveButton();
			}
			else {
				console.error('Error while saving user settings:', response.message);
				alert('Error while saving user settings: ' + response.message);
			}
		}
		catch (err) {
			console.error('Error while saving user settings:', err);
			alert('Error while saving user settings: ' + err);
		}
	});
	saveReq.addEventListener('error', function(err) {
		console.error('Error while saving user settings:', err);
		alert('Error while saving user settings: ' + err);
	});
	saveReq.send(formData);
});

// add margin to last option container when scrollbar is present
function addWhitespaceOnScrollbar() {
	const main = document.querySelector('main');
	const lastOptionContainer = document.querySelector('.option-container:last-child');
	if (!lastOptionContainer) {
		return false;
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
