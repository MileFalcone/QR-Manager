function showToast(message, category) {
    category = category || 'info';
    var container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        container.id = 'toastContainer';
        document.body.appendChild(container);
    }

    var icons = {
        success: 'bi-check-circle-fill',
        danger: 'bi-x-circle-fill',
        error: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill'
    };
    var icon = icons[category] || icons.info;

    var toast = document.createElement('div');
    toast.className = 'toast-notification toast-' + category;
    toast.innerHTML =
        '<span class="toast-icon"><i class="bi ' + icon + '"></i></span>' +
        '<span class="toast-text">' + message + '</span>' +
        '<button class="toast-close" onclick="dismissToast(this.parentElement)">&times;</button>';

    container.appendChild(toast);

    setTimeout(function() {
        dismissToast(toast);
    }, 4500);
}

function dismissToast(toast) {
    if (!toast || toast.classList.contains('toast-out')) return;
    toast.classList.add('toast-out');
    setTimeout(function() {
        if (toast.parentElement) toast.parentElement.removeChild(toast);
    }, 350);
}
