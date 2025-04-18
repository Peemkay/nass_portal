/**
 * Dynamic Tables JavaScript for Registration Page 5
 * Handles adding/removing rows and month-year picker functionality
 */

// Configuration for education tables
const tableConfig = {
    tertiary: {
        id: 'tertiary-education-table',
        required: true,
        fields: ['name', 'start_date', 'end_date', 'cert', 'grade', 'remarks']
    },
    secondary: {
        id: 'secondary-education-table',
        required: false,
        fields: ['name', 'start_date', 'end_date', 'cert', 'grade', 'remarks']
    },
    military: {
        id: 'military-courses-table',
        required: false,
        fields: ['name', 'start_date', 'end_date', 'cert', 'grade', 'remarks']
    }
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tables
    Object.keys(tableConfig).forEach(tableType => {
        initializeDynamicTable(tableType);
    });

    // Initialize form validation
    initializeFormValidation();
});

/**
 * Initialize a dynamic table with add/remove row functionality
 * @param {string} tableType - The type of table (tertiary, secondary, military)
 */
function initializeDynamicTable(tableType) {
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
        // Check if at least one tertiary education entry is filled
        const tertiaryConfig = tableConfig.tertiary;
        const tertiaryTable = document.getElementById(tertiaryConfig.id);

        if (tertiaryTable) {
            const nameInputs = tertiaryTable.querySelectorAll(`input[name="${tertiaryConfig.prefix || 'tertiary'}_name[]"]`);
            let hasValidEntry = false;

            nameInputs.forEach(input => {
                if (input.value.trim()) {
                    hasValidEntry = true;
                }
            });

            if (!hasValidEntry) {
                event.preventDefault();
                event.stopPropagation();

                showErrorMessage(tertiaryConfig.id, 'At least one tertiary education entry is required');
                scrollToElement(tertiaryTable);
            }
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
    const prefix = config.prefix || tableType;

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
        <td>
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

                showErrorMessage(tableId, 'At least one row is required');
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
 * @param {string} tableId - The ID of the table
 * @param {string} message - The error message to display
 */
function showErrorMessage(tableId, message) {
    const messageDiv = document.getElementById(`${tableId}-message`);
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
