document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('userSearch');
    const options = document.querySelectorAll('.user-option');
    const hiddenInput = document.getElementById('user_id');
    const label = document.getElementById('selected-user-label');
    const dropdownBtn = document.getElementById('userDropdown');
    const noResults = document.getElementById('noResults');
    const userMenu = document.getElementById('userMenu');

    if (!searchInput || !hiddenInput) return;

    function filterUsers() {
        const query = searchInput.value.toLowerCase().trim();
        let visibleCount = 0;

        options.forEach(btn => {
            const name = btn.dataset.username.toLowerCase();
            if (name.includes(query)) {
                btn.classList.remove('d-none');
                visibleCount++;
            } else {
                btn.classList.add('d-none');
            }
        });

        if (noResults) {
            noResults.classList.toggle('d-none', visibleCount > 0);
        }
    }

    function selectUser(id, username) {
        hiddenInput.value = id;
        label.textContent = username;
        label.classList.remove('text-muted');
        label.classList.add('fw-bold');

        options.forEach(btn => {
            btn.classList.remove('selected-user');
            if (btn.dataset.id == id) {
                btn.classList.add('selected-user');
            }
        });

        const bsDropdown = bootstrap.Dropdown.getInstance(dropdownBtn);
        if (bsDropdown) bsDropdown.hide();
    }

    searchInput.addEventListener('input', filterUsers);

    options.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            selectUser(this.dataset.id, this.dataset.username);
        });
    });

    if (dropdownBtn) {
        dropdownBtn.addEventListener('shown.bs.dropdown', function() {
            setTimeout(function() {
                searchInput.focus();
                searchInput.select();
            }, 100);
        });

        dropdownBtn.addEventListener('hidden.bs.dropdown', function() {
            searchInput.value = '';
            filterUsers();
        });
    }

    if (hiddenInput.value) {
        options.forEach(btn => {
            if (btn.dataset.id == hiddenInput.value) {
                btn.classList.add('selected-user');
            }
        });
    }

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const visibleOptions = document.querySelectorAll('.user-option:not(.d-none)');
            if (visibleOptions.length === 1) {
                const first = visibleOptions[0];
                selectUser(first.dataset.id, first.dataset.username);
            }
        }
    });

    if (userMenu) {
        userMenu.addEventListener('click', function(e) { e.stopPropagation(); });
    }
    searchInput.addEventListener('click', function(e) { e.stopPropagation(); });
});
