function setupTableSearch(inputId, tableBodyId, columnsCount) {
    const searchInput = document.getElementById(inputId);
    const tableBody = document.getElementById(tableBodyId);
    if (!searchInput || !tableBody) return;

    let noResultsRow = tableBody.querySelector('.no-results-row');
    if (!noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row d-none';
        noResultsRow.innerHTML = `<td colspan="${columnsCount}" class="text-center py-4 text-muted">Ничего не найдено</td>`;
        tableBody.appendChild(noResultsRow);
    }

    searchInput.addEventListener('keyup', function() {
        const value = this.value.toLowerCase().trim();
        const rows = tableBody.querySelectorAll('tr:not(.no-data-row):not(.no-results-row)');
        const noDataRow = tableBody.querySelector('.no-data-row');

        if (noDataRow && !noDataRow.classList.contains('d-none') && value === '') return;

        let hasMatches = false;

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(value)) {
                row.style.display = '';
                hasMatches = true;
            } else {
                row.style.display = 'none';
            }
        });

        if (value !== '') {
            if (noDataRow) noDataRow.style.display = 'none';
            if (hasMatches) {
                noResultsRow.classList.add('d-none');
            } else {
                noResultsRow.classList.remove('d-none');
            }
        } else {
            noResultsRow.classList.add('d-none');
            if (noDataRow) noDataRow.style.display = '';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupTableSearch('tableSearch', 'tableBody', 6);
    setupTableSearch('usersSearch', 'usersTableBody', 5);
    setupTableSearch('catSearch', 'catTableBody', 3);
});
