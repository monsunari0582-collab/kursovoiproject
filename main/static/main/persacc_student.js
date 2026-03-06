/**
 * persacc_student.js
 * Логика страницы личного кабинета студента KHTISPORT
 * Подключается ПОСЛЕ main.js (инициализация header, burger, scroll уже выполнена)
 */

// ---- Редактирование профиля ----

function initProfileEdit() {
  const editBtn   = document.getElementById('editProfileBtn');
  const cancelBtn = document.getElementById('cancelEditBtn');
  const form      = document.getElementById('profileForm');
  const actions   = document.getElementById('profileFormActions');
  if (!editBtn || !form) return;

  const inputs = form.querySelectorAll('input');

  function enableEdit() {
    inputs.forEach(inp => inp.removeAttribute('disabled'));
    actions.style.display = 'flex';
    editBtn.style.display = 'none';
    // Фокус на первое поле
    inputs[0]?.focus();
  }

  function disableEdit() {
    inputs.forEach(inp => inp.setAttribute('disabled', ''));
    actions.style.display = 'none';
    editBtn.style.display = '';
    // Сбрасываем значения (если отмена)
    form.reset ? form.reset() : null;
  }

  editBtn.addEventListener('click', enableEdit);
  cancelBtn?.addEventListener('click', disableEdit);
}

// ---- Подтверждение отмены записи ----

function initCancelEnrollment() {
  const btns = document.querySelectorAll('.persacc__cancel-btn');
  if (!btns.length) return;

  btns.forEach(btn => {
    // Если НЕ используется HTMX — обрабатываем вручную
    if (btn.hasAttribute('hx-post')) return; // HTMX сам управляет

    btn.addEventListener('click', () => {
      const id = btn.dataset.id;
      if (!id) return;

      const confirmed = window.confirm('Отменить запись на тренировку?');
      if (!confirmed) return;

      fetch(`/cancel-enrollment/${id}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCsrfToken(),
          'Content-Type': 'application/json',
        },
      })
        .then(res => {
          if (res.ok) {
            // Анимированно убираем карточку
            const card = btn.closest('.persacc__enroll-card');
            if (card) {
              card.style.transition = 'opacity 300ms ease, transform 300ms ease';
              card.style.opacity = '0';
              card.style.transform = 'translateX(12px)';
              setTimeout(() => card.remove(), 320);
            }
            updateEnrollCount(-1);
          } else {
            alert('Не удалось отменить запись. Попробуйте ещё раз.');
          }
        })
        .catch(() => alert('Ошибка соединения.'));
    });
  });
}

// ---- Уменьшает счётчик записей в статистике ----

function updateEnrollCount(delta) {
  const statNums = document.querySelectorAll('.persacc__stat-num');
  // Первый стат — «Записей»
  if (statNums[0]) {
    const current = parseInt(statNums[0].textContent, 10) || 0;
    const next = Math.max(0, current + delta);
    animateCounter(statNums[0], current, next, 400);
  }
}

// Плавная анимация числа
function animateCounter(el, from, to, duration) {
  const start = performance.now();
  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3); // cubic ease-out
    el.textContent = Math.round(from + (to - from) * ease);
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

// ---- Счётчики при первом появлении (IntersectionObserver) ----

function initStatCounters() {
  const statNums = document.querySelectorAll('.persacc__stat-num');
  if (!statNums.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.textContent, 10) || 0;
      animateCounter(el, 0, target, 700);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });

  statNums.forEach(el => observer.observe(el));
}

// ---- CSRF-токен из куки ----

function getCsrfToken() {
  const name  = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [key, val] = cookie.trim().split('=');
    if (key === name) return decodeURIComponent(val);
  }
  return '';
}

// ---- Уведомление (flash) ----

function showFlash(message, type = 'success') {
  let flash = document.getElementById('persacc-flash');
  if (!flash) {
    flash = document.createElement('div');
    flash.id = 'persacc-flash';
    Object.assign(flash.style, {
      position: 'fixed',
      bottom: '32px',
      right: '32px',
      background: type === 'success' ? 'rgba(137,28,28,0.95)' : 'rgba(60,60,60,0.95)',
      color: 'white',
      padding: '14px 22px',
      borderRadius: '12px',
      fontSize: '14px',
      fontFamily: 'inherit',
      boxShadow: '0 8px 28px rgba(0,0,0,0.4)',
      border: '1px solid rgba(232,119,119,0.25)',
      zIndex: '9999',
      transition: 'opacity 300ms ease, transform 300ms ease',
      opacity: '0',
      transform: 'translateY(12px)',
    });
    document.body.appendChild(flash);
  }

  flash.textContent = message;
  flash.style.opacity = '1';
  flash.style.transform = 'translateY(0)';

  clearTimeout(flash._timer);
  flash._timer = setTimeout(() => {
    flash.style.opacity = '0';
    flash.style.transform = 'translateY(12px)';
  }, 3000);
}

// ---- Обработка успешной отправки форм (если нет Django messages) ----

function initFormFeedback() {
  // Форма профиля
  const profileForm = document.getElementById('profileForm');
  profileForm?.addEventListener('submit', (e) => {
    // Django обработает редирект; при желании можно interceptить через fetch
    // Здесь просто показываем flash до перезагрузки
    sessionStorage.setItem('persacc_flash', 'Профиль успешно обновлён');
  });

  // Flash из sessionStorage после перезагрузки
  const storedFlash = sessionStorage.getItem('persacc_flash');
  if (storedFlash) {
    sessionStorage.removeItem('persacc_flash');
    setTimeout(() => showFlash(storedFlash), 400);
  }
}

// ---- Запуск ----

function initPersacc() {
  initProfileEdit();
  initCancelEnrollment();
  initStatCounters();
  initFormFeedback();
}

// main.js уже вызывает init() синхронно, поэтому ждём DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPersacc);
} else {
  initPersacc();
}
