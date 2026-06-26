document.addEventListener('DOMContentLoaded', function() {
    const hiddenInput = document.getElementById('category_ids');
    const tagsContainer = document.getElementById('selected-categories-tags');
    const selectedLabel = document.getElementById('selected-categories-label');

    if (!hiddenInput && !tagsContainer) return;

    let selectedCategories = [];

    function getCategoryName(id) {
        const checkbox = document.querySelector(`.category-checkbox[value="${id}"]`);
        if (checkbox) {
            const label = checkbox.closest('.category-option').querySelector('.form-check-label');
            return label ? label.textContent.trim() : null;
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

        selectedLabel.textContent = `Выбрано: ${selectedCategories.length} категорий`;
        selectedLabel.className = '';

        selectedCategories.forEach(catId => {
            const categoryName = getCategoryName(catId);
            if (categoryName) {
                const tag = document.createElement('span');
                tag.className = 'selected-tag';
                tag.innerHTML = `
                    ${categoryName}
                    <span class="remove-tag" data-id="${catId}">&times;</span>
                `;
                tagsContainer.appendChild(tag);

                tag.querySelector('.remove-tag').addEventListener('click', function(e) {
                    e.stopPropagation();
                    removeCategory(this.dataset.id);
                });
            }
        });
    }

    function updateHiddenInput() {
        if (hiddenInput) {
            hiddenInput.value = selectedCategories.join(',');
        }
    }

    function addCategory(id) {
        if (!selectedCategories.includes(id)) {
            selectedCategories.push(id);
            updateHiddenInput();
            updateTagsDisplay();
            const checkbox = document.querySelector(`.category-checkbox[value="${id}"]`);
            if (checkbox) checkbox.checked = true;
        }
    }

    function removeCategory(id) {
        selectedCategories = selectedCategories.filter(catId => catId !== id);
        updateHiddenInput();
        updateTagsDisplay();
        const checkbox = document.querySelector(`.category-checkbox[value="${id}"]`);
        if (checkbox) checkbox.checked = false;
    }

    document.querySelectorAll('.category-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                addCategory(this.value);
            } else {
                removeCategory(this.value);
            }
        });
    });

    const searchInput = document.getElementById('categorySearch');
    const categoryItems = document.querySelectorAll('.category-option');
    const noResults = document.getElementById('noCategoryResults');

    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            let hasVisible = false;

            categoryItems.forEach(item => {
                const label = item.querySelector('.form-check-label');
                const text = label ? label.textContent.toLowerCase() : '';
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                    hasVisible = true;
                } else {
                    item.style.display = 'none';
                }
            });

            if (noResults) noResults.classList.toggle('d-none', hasVisible);
        });
    }

    const clearBtn = document.getElementById('clearCategories');
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            selectedCategories = [];
            updateHiddenInput();
            updateTagsDisplay();
            document.querySelectorAll('.category-checkbox').forEach(cb => cb.checked = false);
        });
    }

    if (hiddenInput && hiddenInput.value) {
        const initialCategories = hiddenInput.value.split(',').filter(id => id);
        initialCategories.forEach(id => {
            if (id && !selectedCategories.includes(id)) {
                selectedCategories.push(id);
                const checkbox = document.querySelector(`.category-checkbox[value="${id}"]`);
                if (checkbox) checkbox.checked = true;
            }
        });
        updateTagsDisplay();
    }

    document.querySelectorAll('.category-checkbox:checked').forEach(cb => {
        if (!selectedCategories.includes(cb.value)) {
            selectedCategories.push(cb.value);
        }
    });
    updateTagsDisplay();
});
