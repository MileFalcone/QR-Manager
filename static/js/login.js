(function() {
    'use strict';

    const form = document.getElementById('loginForm');
    const btn = document.getElementById('loginBtn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameGroup = document.getElementById('usernameGroup');
    const passwordGroup = document.getElementById('passwordGroup');
    if (!form) return;

    /* ---- Form Fields ---- */
    usernameInput.addEventListener('input', function() {
        usernameGroup.classList.remove('error');
    });

    passwordInput.addEventListener('input', function() {
        passwordGroup.classList.remove('error');
    });

    /* ---- Test Credentials (fill only, no auto-submit) ---- */
    document.querySelectorAll('.test-credential').forEach(function(el) {
        el.addEventListener('click', function() {
            const user = this.dataset.username || '';
            const pass = this.dataset.password || '';
            if (user) {
                usernameInput.value = user;
                usernameGroup.classList.remove('error');
            }
            if (pass) {
                passwordInput.value = pass;
                passwordGroup.classList.remove('error');
            }
        });
    });

    /* ---- Submit Handler ---- */
    form.addEventListener('submit', function(e) {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();
        let hasError = false;

        if (!username) {
            usernameGroup.classList.add('error');
            hasError = true;
        } else {
            usernameGroup.classList.remove('error');
        }

        if (!password) {
            passwordGroup.classList.add('error');
            hasError = true;
        } else {
            passwordGroup.classList.remove('error');
        }

        if (hasError) {
            e.preventDefault();
            const existingAlert = document.querySelector('.alert-custom');
            if (!existingAlert) {
                const alertHtml = `
                    <div class="alert-custom alert-dismissible fade show" role="alert" style="margin-bottom: 16px;">
                        <i class="bi bi-exclamation-triangle-fill"></i>
                        <span>Заполните все поля!</span>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                form.insertAdjacentHTML('beforebegin', alertHtml);
            }
            return;
        }

        btn.classList.add('loading');
        btn.querySelector('.btn-content').innerHTML = `
            <i class="bi bi-arrow-repeat"></i>
            Вход...
        `;
        btn.disabled = true;
    });

    window.addEventListener('pageshow', function() {
        btn.classList.remove('loading');
        btn.querySelector('.btn-content').innerHTML = `
            <i class="bi bi-box-arrow-in-right"></i>
            Войти в систему
        `;
        btn.disabled = false;
    });

    if (!usernameInput.value) {
        usernameInput.focus();
    }
})();
