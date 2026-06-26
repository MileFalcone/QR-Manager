document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('qrSearchInput');
    if (!searchInput) return;

    function filterCurrentTab() {
        const query = searchInput.value.toLowerCase().trim();
        const activePane = document.querySelector('.tab-content .tab-pane.active');
        if (!activePane) return;

        const grid = activePane.querySelector('.qr-grid');
        const placeholder = activePane.querySelector('.no-results-placeholder');
        const cards = grid.querySelectorAll('.qr-card');
        let visibleCardsCount = 0;

        cards.forEach(card => {
            const name = card.querySelector('.qr-name').textContent.toLowerCase();
            const link = card.querySelector('.qr-link').textContent.toLowerCase();
            const categories = card.querySelector('.qr-categories').textContent.toLowerCase();

            if (name.includes(query) || link.includes(query) || categories.includes(query)) {
                card.style.setProperty('display', '', 'important');
                visibleCardsCount++;
            } else {
                card.style.setProperty('display', 'none', 'important');
            }
        });

        if (visibleCardsCount === 0) {
            grid.classList.add('d-none');
            placeholder.classList.remove('d-none');
        } else {
            grid.classList.remove('d-none');
            placeholder.classList.add('d-none');
        }
    }

    searchInput.addEventListener('keyup', filterCurrentTab);

    document.querySelectorAll('#categoryTabs button').forEach(button => {
        button.addEventListener('shown.bs.tab', filterCurrentTab);
    });
});
