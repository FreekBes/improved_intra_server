/* ************************************************************************** */
/*                                                                            */
/*                                                        ::::::::            */
/*   options2-static.js                                 :+:    :+:            */
/*                                                     +:+                    */
/*   By: fbes <fbes@student.codam.nl>                 +#+                     */
/*                                                   +#+                      */
/*   Created: 2022/10/16 02:22:25 by fbes          #+#    #+#                 */
/*   Updated: 2022/10/16 20:21:09 by fbes          ########   odam.nl         */
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

// populate option containers and the available choices (attach event listeners, set selected values, etc)
const optionContainers = document.querySelectorAll('.option-container');
for (const optionContainer of optionContainers) {
	try {
		const options = optionContainer.querySelectorAll('.option-selector .option');
		const slug = optionContainer.id;

		console.log('Found option container with slug "' + slug + '", user value is:', user_settings[slug]);

		// if the option container is structured in a choice-like manner, add event listeners to the options
		if (optionContainer.classList.contains("choice")) {
			// add event listener for each option
			for (const option of options) {
				if (option.classList.contains('disabled')) {
					continue;
				}
				option.addEventListener('click', function(ev) {
					// retrieve slug and value to set from the clicked choice
					const optionContainer = ev.currentTarget.closest('.option-container');
					const slug = optionContainer.id;
					console.log('Clicked on options choice for:', slug);
					const val = ev.currentTarget.getAttribute('data-value');
					console.log('Value to be set:', val);

					// actually set value in modified user settings
					mod_user_settings[slug] = val;

					// update UI
					const activeChoice = optionContainer.querySelector('.option.active');
					activeChoice.classList.remove('active');
					ev.currentTarget.classList.add('active');
					checkShowSaveButton();
				});
			}

			// activate the chosen option on load
			const choiceToActivate = optionContainer.querySelector('.option-selector .option[data-value="' + user_settings[slug] + '"]');
			if (choiceToActivate) {
				choiceToActivate.classList.add('active');
			}
		}

		// if the option container is structured like a regular input field, add event listeners to the actual input
		if (optionContainer.classList.contains("input")) {
			const input = optionContainer.querySelector('.input-field');

			// add event listener for input change
			input.addEventListener('input', function(ev) {
				// retrieve slug and value to set from the clicked choice
				const optionContainer = ev.currentTarget.closest('.option-container');
				const slug = optionContainer.getAttribute('data-slug');
				const val = ev.currentTarget.value.trim();

				// actually set value in modified user settings
				mod_user_settings[slug] = val;

				// update UI
				checkShowSaveButton();
			});

			// set current value on load
			input.value = user_settings[slug];
		}

		// add a link to each option container to the top right corner of the element, for easy sharing with other students
		const link = document.createElement('a');
		link.classList.add('option-link');
		link.href = '#' + slug;
		link.innerText = '#';
		link.setAttribute('title', 'Link to this option');
		optionContainer.appendChild(link);
	}
	catch (err) {
		console.error('Error while setting up option container with slug "' + slug + '":', err);
	}
}

// save button event listener
document.getElementById('save-btn').addEventListener('click', function(ev) {
	console.log('Saving user settings:', mod_user_settings);

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
	saveReq.send();
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
