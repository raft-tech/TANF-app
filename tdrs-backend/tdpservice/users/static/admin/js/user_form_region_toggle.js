document.addEventListener('DOMContentLoaded', function() {
    const groupSelect = document.querySelector('#id_groups');
    const regionFieldRow = document.querySelector('#id_regions').closest('.form-row, .field-box, .form-group');

    function toggleRegionField() {
        if (!groupSelect || !regionFieldRow) return;

        const selectedOptions = Array.from(groupSelect.selectedOptions).map(opt => opt.textContent.trim());
        const regionalRoles = ["Regional Staff", "Developer", "Data Analyst"];

        const hasRegionalRole = selectedOptions.some(role => regionalRoles.includes(role));

        regionFieldRow.style.display = hasRegionalRole ? '' : 'none';
    }

    if (groupSelect) {
        groupSelect.addEventListener('change', toggleRegionField);
        toggleRegionField(); // run on page load
    }
});