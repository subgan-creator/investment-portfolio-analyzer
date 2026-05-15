/**
 * Onboarding Flow JavaScript
 * Handles option card selection and form interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Handle option card selection (checkboxes and radio buttons)
    initOptionCards();
});

/**
 * Initialize option card click handlers
 */
function initOptionCards() {
    const optionCards = document.querySelectorAll('.option-card');

    optionCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking directly on input
            if (e.target.tagName === 'INPUT') return;

            const input = this.querySelector('input');
            if (!input) return;

            if (input.type === 'checkbox') {
                // Toggle checkbox
                input.checked = !input.checked;
                this.classList.toggle('selected', input.checked);
            } else if (input.type === 'radio') {
                // Deselect all siblings first
                const name = input.name;
                document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
                    radio.closest('.option-card').classList.remove('selected');
                });

                // Select this one
                input.checked = true;
                this.classList.add('selected');
            }
        });

        // Also handle direct input changes
        const input = card.querySelector('input');
        if (input) {
            input.addEventListener('change', function() {
                if (this.type === 'checkbox') {
                    card.classList.toggle('selected', this.checked);
                } else if (this.type === 'radio') {
                    // Deselect all siblings
                    const name = this.name;
                    document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
                        radio.closest('.option-card').classList.remove('selected');
                    });
                    card.classList.add('selected');
                }
            });
        }
    });
}

/**
 * Validate form before submission (optional)
 */
function validateOnboardingForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    // Add custom validation here if needed
    return true;
}
