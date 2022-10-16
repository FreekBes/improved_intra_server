/* ************************************************************************** */
/*                                                                            */
/*                                                        ::::::::            */
/*   options2-static.js                                 :+:    :+:            */
/*                                                     +:+                    */
/*   By: fbes <fbes@student.codam.nl>                 +#+                     */
/*                                                   +#+                      */
/*   Created: 2022/10/16 02:22:25 by fbes          #+#    #+#                 */
/*   Updated: 2022/10/16 02:33:27 by fbes          ########   odam.nl         */
/*                                                                            */
/* ************************************************************************** */

const optionContainers = document.querySelectorAll('.option-container');
for (const optionContainer of optionContainers) {
	const options = optionContainer.querySelectorAll('.option-selector .option');
	const slug = optionContainer.id;

	// if the option container is structured in a choice-like manner, add event listeners to the options
	if (optionContainer.classList.contains("choice")) {
		// add event listener for each option
		for (const option of options) {
			option.addEventListener('click', function(ev) {
				// retrieve slug and value to set from the clicked choice
				const optionContainer = ev.currentTarget.closest('.option-container');
				const slug = optionContainer.id;
				console.log('Clicked on options choice for ', slug);
				const val = ev.currentTarget.getAttribute('data-value');
				console.log('Value to be set: ', val);

				// actually set value
				user_settings[slug] = val;

				// update UI
				const activeChoice = optionContainer.querySelector('.option.active');
				activeChoice.classList.remove('active');
				ev.currentTarget.classList.add('active');
			});
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

		// add event listener for input change
		input.addEventListener('input', function(ev) {
			// retrieve slug and value to set from the clicked choice
			const optionContainer = ev.currentTarget.closest('.option-container');
			const slug = optionContainer.getAttribute('data-slug');
			const val = ev.currentTarget.value.trim();

			// actually set value
			user_settings[slug] = val;
		});

		// set current value
		input.value = user_settings[slug];
	}
}
