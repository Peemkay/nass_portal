/**
 * Compact Tables JavaScript for Registration Page 5
 * Handles adding/removing rows and month-year picker functionality
 */

// Configuration for education tables
const tableConfig = {
    tertiary: {
        id: 'tertiary-table',
        required: true,
        fields: ['name', 'start_date', 'end_date', 'cert', 'grade', 'remarks']
    },
    secondary: {
        id: 'secondary-table',
        required: false,
        fields: ['name', 'start_date', 'end_date', 'cert', 'grade', 'remarks']
    },
    military: {
        id: 'military-table',
        required: false,
        fields: ['name', 'start_date', 'end_date', 'cert', 'grade', 'remarks']
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tables
    Object.keys(tableConfig).forEach(tableType => {
        initializeTable(tableType);
    });
    
    // Initialize form validation
    initializeFormValidation();
    
    // Add animation to sections
    animateSections();
});

/**
 * Initialize a table with add/remove row functionality
 * @param {string} tableType - The type of table (tertiary, secondary, military)
 */
function initializeTable(tableType) {
    const config = tableConfig[tableType];
    const table = document.getElementById(config.id);
    
    if (!table) return;
    
    // Add button click handler
    const addButton = document.querySelector(`#${config.id}-add-row`);
    if (addButton) {
        addButton.addEventListener('click', () => addNewRow(tableType));
    }
    
    // Add remove button handlers to existing rows
    setupRemoveButtons(table, config.required);
    
    // Update serial numbers
    updateSerialNumbers(table);
    
    // Initialize month-year pickers
    initializeMonthYearPickers(table);
    
    // Setup date range validation
    setupDateRangeValidation(table);
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const form = document.querySelector('form.needs-validation');
    if (!form) return;
    
    form.addEventListener('submit', function(event) {
        let isValid = true;
        
        // Check if at least one tertiary education entry is filled
        const tertiaryConfig = tableConfig.tertiary;
        const tertiaryTable = document.getElementById(tertiaryConfig.id);
        
        if (tertiaryTable) {
            const nameInputs = tertiaryTable.querySelectorAll(`input[name="tertiary_name[]"]`);
            let hasValidEntry = false;
            
            nameInputs.forEach(input => {
                if (input.value.trim()) {
                    hasValidEntry = true;
                }
            });
            
            if (!hasValidEntry) {
                isValid = false;
                showErrorMessage(`${tertiaryConfig.id}-error`, 'At least one tertiary education entry is required');
                scrollToElement(tertiaryTable);
            }
        }
        
        // Check NASS information
        const nassFields = ['nass_course', 'nass_department'];
        nassFields.forEach(field => {
            const input = document.getElementById(field);
            if (input && input.required && !input.value.trim()) {
                isValid = false;
                input.classList.add('is-invalid');
                
                // Create error message if not exists
                let errorMsg = input.nextElementSibling;
                if (!errorMsg || !errorMsg.classList.contains('invalid-feedback')) {
                    errorMsg = document.createElement('div');
                    errorMsg.className = 'invalid-feedback';
                    input.parentNode.appendChild(errorMsg);
                }
                errorMsg.textContent = 'This field is required';
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
        }
    });
}

/**
 * Add a new row to the specified table
 * @param {string} tableType - The type of table (tertiary, secondary, military)
 */
function addNewRow(tableType) {
    const config = tableConfig[tableType];
    const table = document.getElementById(config.id);
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const prefix = tableType;
    
    // Create a new row
    const newRow = document.createElement('tr');
    newRow.className = 'new-row';
    
    // Create the row content
    let rowHtml = `<td class="serial-number"></td>`;
    
    // Add cells based on the fields configuration
    config.fields.forEach(field => {
        const isRequired = config.required && (field === 'name' || field === 'start_date' || field === 'end_date' || field === 'cert' || field === 'grade');
        const isDate = field === 'start_date' || field === 'end_date';
        
        if (isDate) {
            rowHtml += `
                <td>
                    <div class="monthyear-picker">
                        <input type="text" class="form-control monthyear-input" name="${prefix}_${field}[]" 
                               placeholder="MM/YYYY" ${isRequired ? 'required' : ''} pattern="^(0[1-9]|1[0-2])/[0-9]{4}$">
                    </div>
                </td>`;
        } else {
            rowHtml += `
                <td>
                    <input type="text" class="form-control" name="${prefix}_${field}[]" ${isRequired ? 'required' : ''}>
                </td>`;
        }
    });
    
    // Add action cell
    rowHtml += `
        <td class="text-center">
            <button type="button" class="btn-remove-row" title="Remove row">
                <i class="fas fa-times"></i>
            </button>
        </td>`;
    
    newRow.innerHTML = rowHtml;
    tbody.appendChild(newRow);
    
    // Setup the new row
    setupRemoveButtons(table, config.required);
    updateSerialNumbers(table);
    initializeMonthYearPickers(newRow);
    setupDateRangeValidation(newRow);
    
    // Focus the first input in the new row
    const firstInput = newRow.querySelector('input');
    if (firstInput) firstInput.focus();
}

/**
 * Setup remove buttons for all rows in a table
 * @param {HTMLElement} table - The table element
 * @param {boolean} isRequired - Whether at least one row is required
 */
function setupRemoveButtons(table, isRequired) {
    const removeButtons = table.querySelectorAll('.btn-remove-row');
    const tableId = table.id;
    
    removeButtons.forEach(button => {
        // Remove existing event listeners to prevent duplicates
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add new event listener
        newButton.addEventListener('click', function() {
            const row = this.closest('tr');
            const tbody = row.parentNode;
            const rowCount = tbody.querySelectorAll('tr').length;
            
            // Don't remove if it's the only row and the table requires at least one entry
            if (rowCount === 1 && isRequired) {
                // Clear the inputs instead of removing the row
                row.querySelectorAll('input').forEach(input => {
                    input.value = '';
                    input.classList.remove('is-valid', 'is-invalid');
                });
                
                showErrorMessage(`${tableId}-error`, 'At least one row is required');
                return;
            }
            
            // Remove the row with animation
            row.style.opacity = '0';
            row.style.transform = 'translateY(-5px)';
            row.style.transition = 'all 0.2s ease';
            
            setTimeout(() => {
                row.remove();
                updateSerialNumbers(table);
            }, 200);
        });
    });
}

/**
 * Update serial numbers for all rows in a table
 * @param {HTMLElement} table - The table element
 */
function updateSerialNumbers(table) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach((row, index) => {
        const serialCell = row.querySelector('.serial-number');
        if (serialCell) {
            serialCell.textContent = index + 1;
        }
    });
}

/**
 * Initialize month-year pickers for date inputs
 * @param {HTMLElement} container - Container to limit the scope
 */
function initializeMonthYearPickers(container) {
    const dateInputs = container.querySelectorAll('.monthyear-input');
    
    dateInputs.forEach(input => {
        // Remove existing event listeners to prevent duplicates
        const newInput = input.cloneNode(true);
        input.parentNode.replaceChild(newInput, input);
        
        // Add input mask and validation
        newInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            
            if (value.length > 6) {
                value = value.substring(0, 6);
            }
            
            if (value.length > 2) {
                // Format as MM/YYYY
                const month = value.substring(0, 2);
                const year = value.substring(2);
                
                // Validate month (01-12)
                let validMonth = parseInt(month, 10);
                if (validMonth < 1) validMonth = '01';
                if (validMonth > 12) validMonth = '12';
                validMonth = validMonth.toString().padStart(2, '0');
                
                e.target.value = `${validMonth}/${year}`;
            } else if (value.length > 0) {
                e.target.value = value;
            }
            
            // Validate the input
            validateMonthYearInput(e.target);
            
            // Check date range if this is part of a pair
            const row = e.target.closest('tr');
            if (row) {
                const startInput = row.querySelector('input[name$="_start_date[]"]');
                const endInput = row.querySelector('input[name$="_end_date[]"]');
                if (startInput && endInput && startInput.value && endInput.value) {
                    validateDateRange(startInput, endInput);
                }
            }
        });
        
        // Initial validation
        validateMonthYearInput(newInput);
    });
}

/**
 * Validate a month-year input
 * @param {HTMLInputElement} input - The input element
 */
function validateMonthYearInput(input) {
    if (!input.value) return;
    
    const regex = /^(0[1-9]|1[0-2])\/[0-9]{4}$/;
    const isValid = regex.test(input.value);
    
    if (!isValid) {
        input.classList.add('is-invalid');
        input.setCustomValidity('Please enter a valid month and year in MM/YYYY format');
    } else {
        input.classList.remove('is-invalid');
        input.setCustomValidity('');
    }
}

/**
 * Setup validation for date ranges (start date must be before end date)
 * @param {HTMLElement} container - Container to limit the scope
 */
function setupDateRangeValidation(container) {
    const rows = container.tagName === 'TR' ? [container] : container.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const startDateInput = row.querySelector('input[name$="_start_date[]"]');
        const endDateInput = row.querySelector('input[name$="_end_date[]"]');
        
        if (startDateInput && endDateInput) {
            // Validate when either input changes
            [startDateInput, endDateInput].forEach(input => {
                input.addEventListener('change', function() {
                    validateDateRange(startDateInput, endDateInput);
                });
            });
            
            // Initial validation if both have values
            if (startDateInput.value && endDateInput.value) {
                validateDateRange(startDateInput, endDateInput);
            }
        }
    });
}

/**
 * Validate that start date is before end date
 * @param {HTMLInputElement} startInput - The start date input
 * @param {HTMLInputElement} endInput - The end date input
 */
function validateDateRange(startInput, endInput) {
    if (!startInput.value || !endInput.value) return;
    
    const startParts = startInput.value.split('/');
    const endParts = endInput.value.split('/');
    
    if (startParts.length === 2 && endParts.length === 2) {
        const startDate = new Date(parseInt(startParts[1]), parseInt(startParts[0]) - 1);
        const endDate = new Date(parseInt(endParts[1]), parseInt(endParts[0]) - 1);
        
        if (startDate > endDate) {
            endInput.classList.add('is-invalid');
            endInput.setCustomValidity('End date must be after start date');
            
            // Add error message if not already present
            let errorMsg = endInput.parentNode.querySelector('.invalid-feedback');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'invalid-feedback';
                endInput.parentNode.appendChild(errorMsg);
            }
            errorMsg.textContent = 'End date must be after start date';
        } else {
            endInput.classList.remove('is-invalid');
            endInput.setCustomValidity('');
            
            // Remove error message if present
            const errorMsg = endInput.parentNode.querySelector('.invalid-feedback');
            if (errorMsg) errorMsg.remove();
        }
    }
}

/**
 * Show an error message for a table
 * @param {string} elementId - The ID of the error message element
 * @param {string} message - The error message to display
 */
function showErrorMessage(elementId, message) {
    const messageDiv = document.getElementById(elementId);
    if (!messageDiv) return;
    
    messageDiv.textContent = message;
    messageDiv.classList.add('table-error-message');
    
    // Clear the message after 3 seconds
    setTimeout(() => {
        messageDiv.textContent = '';
        messageDiv.classList.remove('table-error-message');
    }, 3000);
}

/**
 * Scroll to an element smoothly
 * @param {HTMLElement} element - The element to scroll to
 */
function scrollToElement(element) {
    if (!element) return;
    
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

/**
 * Animate sections on page load
 */
function animateSections() {
    const sections = document.querySelectorAll('.education-container, .nass-info-container');
    
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        section.style.transitionDelay = `${index * 0.1}s`;
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 100);
    });
}
