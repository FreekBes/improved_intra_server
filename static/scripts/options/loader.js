/* ************************************************************************** */
/*                                                                            */
/*                                                        ::::::::            */
/*   loader.js                                          :+:    :+:            */
/*                                                     +:+                    */
/*   By: fbes <fbes@student.codam.nl>                 +#+                     */
/*                                                   +#+                      */
/*   Created: 2022/11/05 14:08:09 by fbes          #+#    #+#                 */
/*   Updated: 2022/11/05 20:54:05 by fbes          ########   odam.nl         */
/*                                                                            */
/* ************************************************************************** */

// populate option containers and the available choices (attach event listeners, set selected values, etc)
function populateOptions(repopulate = false) {
	const optionContainers = document.querySelectorAll('.option-container');
	for (const optionContainer of optionContainers) {
		try {
			const options = optionContainer.querySelectorAll('.option-selector .option');
			const slug = optionContainer.id;

			// check if the slug exists as a key in the user_settings object
			if (!(slug in user_settings)) {
				if (slug != 'ext_version') {
					console.warn("The slug '" + slug + "' does not exist in the user_settings object");
				}
				continue;
			}

			console.log('Found option container with slug "' + slug + '", user value is:', user_settings[slug]);

			// if the option container is structured in a choice-like manner, add event listeners to the options
			if (optionContainer.classList.contains("choice")) {
				if (repopulate !== true) {
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
				}

				// activate the chosen option
				const choiceToActivate = optionContainer.querySelector('.option-selector .option[data-value="' + user_settings[slug] + '"]');
				if (choiceToActivate) {
					choiceToActivate.classList.add('active');
				}
			}

			// if the option container is structured like a regular input field, add event listeners to the actual input
			if (optionContainer.classList.contains("input")) {
				const input = optionContainer.querySelector('.input-field');

				if (repopulate !== true) {
					// add event listener for input change
					input.addEventListener('input', function(ev) {
						// retrieve slug and value to set from the clicked choice
						const optionContainer = ev.currentTarget.closest('.option-container');
						const slug = optionContainer.id;
						const val = ev.currentTarget.value.trim();

						// actually set value in modified user settings
						mod_user_settings[slug] = val;

						// update UI
						checkShowSaveButton();
					});
				}

				// set current value
				input.value = user_settings[slug];
			}

			// if the option container is structured like an image selector, add event listeners to the file input
			if (optionContainer.classList.contains("picture")) {
				const input = optionContainer.querySelector('.picture-picker');

				if (repopulate !== true) {
					// add event listener for file selection change
					input.addEventListener('change', function(ev) {
						const optionContainer = ev.currentTarget.closest('.option-container');
						const slug = optionContainer.id;
						const currentPic = optionContainer.querySelector('.current-picture');
						const futurePic = optionContainer.querySelector('.future-picture');

						if (ev.currentTarget.files.length > 0) {
							const file = ev.currentTarget.files[0];

							const reader = new FileReader();
							reader.onload = function(ev) {
								futurePic.src = ev.target.result;
								currentPic.style.display = "none";
								futurePic.style.display = "block";
								mod_user_settings[slug] = 'new_upload-' + Math.random().toString(); // update modified user settings so that save button appears
								checkShowSaveButton();
							};
							reader.onerror = function(err) {
								console.error('Error reading file:', err);
								alert('Error reading file: ' + err);
								futurePic.style.display = "none";
								if (currentPic.src.indexOf('/placeholder.png') == -1) {
									currentPic.style.display = "block";
								}
								mod_user_settings[slug] = user_settings[slug];
								checkShowSaveButton();
							};
							reader.readAsDataURL(file);
						}
						else {
							futurePic.style.display = "none";
							if (currentPic.src.indexOf('/placeholder.png') == -1) {
								currentPic.style.display = "block";
							}
							mod_user_settings[slug] = user_settings[slug];
							checkShowSaveButton();
						}
					});
				}
			}

			if (repopulate !== true) {
				// add a link to each option container to the top right corner of the element, for easy sharing with other students
				const link = document.createElement('a');
				link.classList.add('option-link');
				link.href = '#' + slug;
				link.innerText = '#';
				link.setAttribute('title', 'Link to this option');
				optionContainer.appendChild(link);
			}
		}
		catch (err) {
			console.error('Error while setting up option container with slug "' + slug + '":', err);
		}
	}
}

populateOptions();
