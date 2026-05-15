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
        const input = card.querySelector('input');
        if (!input) return;

        // For labels, the click on the label will toggle the input automatically
        // We just need to update the visual state

        // Listen for changes on the input (triggered by label click or direct click)
        input.addEventListener('change', function() {
            if (this.type === 'checkbox') {
                card.classList.toggle('selected', this.checked);
            } else if (this.type === 'radio') {
                // Deselect all siblings
                const name = this.name;
                document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
                    const parentCard = radio.closest('.option-card');
                    if (parentCard) {
                        parentCard.classList.remove('selected');
                    }
                });
                card.classList.add('selected');
            }
        });

        // Also handle click on the card for areas not covered by the label
        card.addEventListener('click', function(e) {
            // If the click target is the input itself, let the native behavior handle it
            if (e.target === input) return;

            // If the click is on a label element (or inside one), the input change will fire
            // Check if we clicked on something that will trigger the input anyway
            if (e.target.tagName === 'LABEL' || e.target.closest('label')) return;

            // For clicks on other parts of the card, manually toggle
            if (input.type === 'checkbox') {
                input.checked = !input.checked;
                input.dispatchEvent(new Event('change'));
            } else if (input.type === 'radio') {
                input.checked = true;
                input.dispatchEvent(new Event('change'));
            }
        });
    });

    // Initialize selected state on page load
    document.querySelectorAll('.option-card input:checked').forEach(input => {
        const card = input.closest('.option-card');
        if (card) {
            card.classList.add('selected');
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
