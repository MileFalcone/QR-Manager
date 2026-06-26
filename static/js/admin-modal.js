function initUserSelector(container) {
    container = container || document;
    const searchInput = container.querySelector('#userSearch');
    const options = container.querySelectorAll('.user-option');
    const hiddenInput = container.querySelector('#user_id');
    const label = container.querySelector('#selected-user-label');
    const dropdownBtn = container.querySelector('#userDropdown');
    const noResults = container.querySelector('#noResults');
    const userMenu = container.querySelector('#userMenu');

    if (!searchInput || !hiddenInput) return;

    function filterUsers() {
        var query = searchInput.value.toLowerCase().trim();
        var visibleCount = 0;
        options.forEach(function(btn) {
            if (btn.dataset.username.toLowerCase().includes(query)) {
                btn.classList.remove('d-none');
                visibleCount++;
            } else {
                btn.classList.add('d-none');
            }
        });
        if (noResults) noResults.classList.toggle('d-none', visibleCount > 0);
    }

    function selectUser(id, username) {
        hiddenInput.value = id;
        label.textContent = username;
        label.classList.remove('text-muted');
        label.classList.add('fw-bold');
        options.forEach(function(btn) {
            btn.classList.remove('selected-user');
            if (btn.dataset.id == id) btn.classList.add('selected-user');
        });
        var bsDropdown = bootstrap.Dropdown.getInstance(dropdownBtn);
        if (bsDropdown) bsDropdown.hide();
    }

    searchInput.addEventListener('input', filterUsers);
    options.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            selectUser(this.dataset.id, this.dataset.username);
        });
    });
    if (dropdownBtn) {
        dropdownBtn.addEventListener('shown.bs.dropdown', function() {
            setTimeout(function() { searchInput.focus(); searchInput.select(); }, 100);
        });
        dropdownBtn.addEventListener('hidden.bs.dropdown', function() {
            searchInput.value = '';
            filterUsers();
        });
    }
    if (hiddenInput.value) {
        options.forEach(function(btn) {
            if (btn.dataset.id == hiddenInput.value) btn.classList.add('selected-user');
        });
    }
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            var visible = document.querySelectorAll('.user-option:not(.d-none)');
            if (visible.length === 1) {
                var first = visible[0];
                selectUser(first.dataset.id, first.dataset.username);
            }
        }
    });
    if (userMenu) {
        userMenu.addEventListener('click', function(e) { e.stopPropagation(); });
    }
    if (searchInput) {
        searchInput.addEventListener('click', function(e) { e.stopPropagation(); });
    }
}

function initCategorySelector(container) {
    container = container || document;
    var hiddenInput = container.querySelector('#category_ids');
    var tagsContainer = container.querySelector('#selected-categories-tags');
    var selectedLabel = container.querySelector('#selected-categories-label');

    if (!hiddenInput && !tagsContainer) return;

    var selectedCategories = [];

    function getCategoryName(id) {
        var checkbox = container.querySelector('.category-checkbox[value="' + id + '"]');
        if (checkbox) {
            var el = checkbox.closest('.category-option').querySelector('.form-check-label');
            return el ? el.textContent.trim() : null;
        }
        return null;
    }

    function updateTagsDisplay() {
        tagsContainer.innerHTML = '';
        if (selectedCategories.length === 0) {
            selectedLabel.textContent = 'Выберите категории...';
            selectedLabel.className = 'text-muted';
            return;
        }
        selectedLabel.textContent = 'Выбрано: ' + selectedCategories.length + ' категорий';
        selectedLabel.className = '';
        selectedCategories.forEach(function(catId) {
            var catName = getCategoryName(catId);
            if (catName) {
                var tag = document.createElement('span');
                tag.className = 'selected-tag';
                tag.innerHTML = catName + ' <span class="remove-tag" data-id="' + catId + '">&times;</span>';
                tagsContainer.appendChild(tag);
                tag.querySelector('.remove-tag').addEventListener('click', function(e) {
                    e.stopPropagation();
                    removeCategory(this.dataset.id);
                });
            }
        });
    }

    function updateHiddenInput() {
        if (hiddenInput) hiddenInput.value = selectedCategories.join(',');
    }

    function addCategory(id) {
        if (!selectedCategories.includes(id)) {
            selectedCategories.push(id);
            updateHiddenInput();
            updateTagsDisplay();
            var cb = container.querySelector('.category-checkbox[value="' + id + '"]');
            if (cb) cb.checked = true;
        }
    }

    function removeCategory(id) {
        selectedCategories = selectedCategories.filter(function(c) { return c !== id; });
        updateHiddenInput();
        updateTagsDisplay();
        var cb = container.querySelector('.category-checkbox[value="' + id + '"]');
        if (cb) cb.checked = false;
    }

    container.querySelectorAll('.category-checkbox').forEach(function(cb) {
        cb.addEventListener('change', function() {
            if (this.checked) addCategory(this.value);
            else removeCategory(this.value);
        });
    });

    var searchInput = container.querySelector('#categorySearch');
    var categoryItems = container.querySelectorAll('.category-option');
    var noResults = container.querySelector('#noCategoryResults');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var term = this.value.toLowerCase().trim();
            var hasVisible = false;
            categoryItems.forEach(function(item) {
                var lbl = item.querySelector('.form-check-label');
                var txt = lbl ? lbl.textContent.toLowerCase() : '';
                if (txt.includes(term)) { item.style.display = ''; hasVisible = true; }
                else { item.style.display = 'none'; }
            });
            if (noResults) noResults.classList.toggle('d-none', hasVisible);
        });
    }

    var clearBtn = container.querySelector('#clearCategories');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            selectedCategories = [];
            updateHiddenInput();
            updateTagsDisplay();
            container.querySelectorAll('.category-checkbox').forEach(function(cb) { cb.checked = false; });
        });
    }

    if (hiddenInput && hiddenInput.value) {
        var initial = hiddenInput.value.split(',').filter(function(id) { return id; });
        initial.forEach(function(id) {
            if (id && !selectedCategories.includes(id)) {
                selectedCategories.push(id);
                var cb = container.querySelector('.category-checkbox[value="' + id + '"]');
                if (cb) cb.checked = true;
            }
        });
        updateTagsDisplay();
    }

    container.querySelectorAll('.category-checkbox:checked').forEach(function(cb) {
        if (!selectedCategories.includes(cb.value)) selectedCategories.push(cb.value);
    });
    updateTagsDisplay();
}


function loadFormIntoModal(url, title, icon) {
    var modal = document.getElementById('formModal');
    var modalLabel = document.getElementById('formModalLabel');
    var modalBody = document.getElementById('formModalBody');
    var bsModal = new bootstrap.Modal(modal);

    modalLabel.textContent = title || 'Загрузка...';
    modalBody.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Загрузка...</span></div></div>';
    bsModal.show();

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function(r) {
            if (!r.ok) { throw new Error('HTTP ' + r.status); }
            return r.text();
        })
        .then(function(html) {
            var cardHeader = '<div class="text-center mb-3">' +
                '<div class="brand-icon ' + (icon || '') + '"><i class="bi ' + (icon === 'user' ? 'bi-person-plus' : icon === 'category' ? 'bi-tag' : icon === 'edit' ? 'bi-pencil-square' : icon === 'settings' ? 'bi-gear' : 'bi-qr-code-scan') + '"></i></div>' +
                '<h3>' + (title || '') + '</h3>' +
                '</div>';
            modalBody.innerHTML = cardHeader + html;
            initUserSelector(modalBody);
            initCategorySelector(modalBody);
            setupModalFormSubmit();
        })
        .catch(function(e) {
            modalBody.innerHTML = '<div class="alert alert-danger">Ошибка загрузки формы</div>';
            console.error('loadFormIntoModal error:', e);
    });
}

function runScripts(container) {
    var scripts = container.querySelectorAll('script');
    scripts.forEach(function(oldScript) {
        var newScript = document.createElement('script');
        newScript.textContent = oldScript.textContent;
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });
}

function setupModalFormSubmit() {
    var modalBody = document.getElementById('formModalBody');
    var form = modalBody.querySelector('form');
    var headerIcon = modalBody.querySelector('.brand-icon');
    var headerTitle = modalBody.querySelector('h3');
    var iconClass = headerIcon ? Array.from(headerIcon.classList).find(function(c) { return c !== 'brand-icon'; }) : '';
    var titleText = headerTitle ? headerTitle.textContent : '';

    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(form);
        var submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Сохранение...'; }

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).then(function(r) {
            return r.text().then(function(text) {
                try {
                    var data = JSON.parse(text);
                    if (data.redirect) {
                        window.location.href = data.redirect;
                        return null;
                    }
                } catch(e) {}
                return text;
            });
        }).then(function(html) {
            if (html) {
                var bi = iconClass === 'user' ? 'bi-person-plus' : iconClass === 'category' ? 'bi-tag' : iconClass === 'edit' ? 'bi-pencil-square' : iconClass === 'settings' ? 'bi-gear' : 'bi-qr-code-scan';
                var cardHeader = '<div class="text-center mb-3">' +
                    '<div class="brand-icon ' + iconClass + '"><i class="bi ' + bi + '"></i></div>' +
                    '<h3>' + titleText + '</h3>' +
                    '</div>';
                modalBody.innerHTML = cardHeader + html;
                runScripts(modalBody);
                initUserSelector(modalBody);
                initCategorySelector(modalBody);
                setupModalFormSubmit();
                if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Сохранить'; }
            }
        }).catch(function() {
            if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Сохранить'; }
            window.location.reload();
        });
    });
}
