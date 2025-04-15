/**
 * Enhanced Education Form JavaScript
 * Provides dynamic form functionality for education entries
 */

document.addEventListener('DOMContentLoaded', function() {
    initEducationForms();
    
    function initEducationForms() {
        // Add University Entry Button
        const addUniButton = document.getElementById('add-uni-row');
        if (addUniButton) {
            addUniButton.addEventListener('click', function() {
                addEducationEntry('uni');
            });
        }
        
        // Add Military Training Entry Button
        const addMilButton = document.getElementById('add-mil-row');
        if (addMilButton) {
            addMilButton.addEventListener('click', function() {
                addEducationEntry('mil');
            });
        }
        
        // Remove Entry Buttons
        document.querySelectorAll('.remove-entry').forEach(button => {
            button.addEventListener('click', function() {
                const entryCard = this.closest('.education-entry');
                if (entryCard) {
                    // Hide instead of remove to preserve form data
                    entryCard.classList.add('d-none');
                    
                    // Clear required fields so form can be submitted
                    entryCard.querySelectorAll('[required]').forEach(field => {
                        field.required = false;
                    });
                    
                    // Clear values
                    entryCard.querySelectorAll('input, select').forEach(field => {
                        field.value = '';
                    });
                    
                    updateEntryNumbers();
                }
            });
        });
        
        // Initialize date pickers
        initDatePickers();
        
        // Update entry numbers on load
        updateEntryNumbers();
    }
    
    function addEducationEntry(type) {
        // Find all entries of this type
        const container = document.getElementById(`${type}-education-container`);
        if (!container) return;
        
        const entries = container.querySelectorAll('.education-entry');
        
        // Find the first hidden entry
        let hiddenEntry = null;
        for (let i = 0; i < entries.length; i++) {
            if (entries[i].classList.contains('d-none')) {
                hiddenEntry = entries[i];
                break;
            }
        }
        
        if (hiddenEntry) {
            // Show the hidden entry
            hiddenEntry.classList.remove('d-none');
            
            // Make first fields required
            hiddenEntry.querySelectorAll('.form-control, .form-select').forEach(field => {
                if (field.dataset.required === 'true') {
                    field.required = true;
                }
            });
        } else {
            // Show message if max entries reached
            alert('Maximum number of entries reached.');
        }
        
        updateEntryNumbers();
    }
    
    function updateEntryNumbers() {
        // Update University entries
        updateTypeEntryNumbers('uni');
        
        // Update Military entries
        updateTypeEntryNumbers('mil');
    }
    
    function updateTypeEntryNumbers(type) {
        const container = document.getElementById(`${type}-education-container`);
        if (!container) return;
        
        const visibleEntries = Array.from(container.querySelectorAll('.education-entry')).filter(
            entry => !entry.classList.contains('d-none')
        );
        
        visibleEntries.forEach((entry, index) => {
            const numberSpan = entry.querySelector('.entry-number');
            if (numberSpan) {
                numberSpan.textContent = index + 1;
            }
        });
    }
    
    function initDatePickers() {
        // Initialize any date picker components if needed
        // This is a placeholder for future enhancements
    }
});
