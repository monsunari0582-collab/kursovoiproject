// ============================================================
// КАБИНЕТ ТРЕНЕРА — persacc_coach.js
// ============================================================

// ---- Табы ----
document.querySelectorAll('.coach-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.coach-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.coach-section').forEach(s => s.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab)?.classList.add('active');
  });
});

// ---- Дни недели ----
document.querySelectorAll('.coach-week__day:not(.coach-week__day--all)').forEach(day => {
  day.addEventListener('click', () => {
    document.querySelectorAll('.coach-week__day').forEach(d => d.classList.remove('active'));
    document.querySelectorAll('.coach-slots').forEach(s => s.classList.remove('active'));
    day.classList.add('active');
    document.getElementById('slots-' + day.dataset.day)?.classList.add('active');
  });
});

function showAllSessions() {
  document.querySelectorAll('.coach-week__day').forEach(d => d.classList.remove('active'));
  document.querySelectorAll('.coach-slots').forEach(s => s.classList.remove('active'));
  document.querySelector('[data-day="all"]')?.classList.add('active');
  document.getElementById('slots-all')?.classList.add('active');
}

// ---- Модалки ----
function openModal(id) {
  document.getElementById(id)?.classList.add('open');
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}

function closeModalOnOverlay(e, id) {
  if (e.target === e.currentTarget) closeModal(id);
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.coach-modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
});

// ---- Переключатель разово / еженедельно / ежедневно ----
function setRepeatMode(mode) {
  document.getElementById('repeat_mode').value = mode;

  document.querySelectorAll('.coach-repeat-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });

  const blockOnce    = document.getElementById('block-once');
  const blockWeekly  = document.getElementById('block-weekly');
  const blockWeekday = document.getElementById('block-weekday');
  const repeatModeVal = document.getElementById('repeat_mode_val');

  if (blockOnce)   blockOnce.style.display   = mode === 'once'   ? '' : 'none';
  if (blockWeekly) blockWeekly.style.display  = mode !== 'once'   ? '' : 'none';

  // При ежедневном — скрываем выбор конкретного дня недели
  if (blockWeekday) blockWeekday.style.display = mode === 'weekly' ? '' : 'none';
  if (repeatModeVal) repeatModeVal.value = mode === 'daily' ? 'daily' : 'weekly';

  // required
  const dateFrom = document.querySelector('[name="date_from"]');
  const date     = document.querySelector('[name="date"]');
  if (dateFrom) dateFrom.required = mode !== 'once';
  if (date)     date.required     = mode === 'once';
}


function openEditModal(id, sport, location, date, time, duration, maxPlaces) {
  const form = document.getElementById('editSessionForm');
  form.action = `/coach/session/${id}/edit/`;

  document.getElementById('edit_sport').value      = sport;
  // location может быть <select> или <input>
  const locEl = document.getElementById('edit_location');
  if (locEl) locEl.value = location;
  document.getElementById('edit_date').value       = date;
  document.getElementById('edit_time').value       = time;
  document.getElementById('edit_duration').value   = duration;
  document.getElementById('edit_max_places').value = maxPlaces;

  openModal('modal-edit-session');
}

// ---- Toast ----
function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  const text  = document.getElementById('toast-text');
  if (!toast || !text) return;

  text.textContent = msg;
  toast.querySelector('i').className = isError
    ? 'fa-solid fa-triangle-exclamation'
    : 'fa-solid fa-circle-check';
  toast.style.borderColor = isError
    ? 'rgba(239,68,68,0.3)'
    : 'rgba(34,197,94,0.3)';

  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// ---- Удалить тренировку (AJAX) ----
function deleteSession(sessionId, btn) {
  if (!confirm('Удалить тренировку? Все записи на неё тоже будут удалены.')) return;

  getCsrfToken().then(csrf => {
    fetch(`/coach/session/${sessionId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        const slot = document.getElementById('session-' + sessionId);
        if (slot) {
          slot.style.transition = 'opacity 300ms, transform 300ms';
          slot.style.opacity = '0';
          slot.style.transform = 'translateX(14px)';
          setTimeout(() => slot.remove(), 300);
        }
        showToast('Тренировка удалена');
      }
    })
    .catch(() => showToast('Ошибка при удалении', true));
  });
}

// ---- Исключить ученика (AJAX) ----
function removeStudent(studentId, btn) {
  if (!confirm('Исключить ученика? Все его записи на ваши тренировки будут удалены.')) return;

  getCsrfToken().then(csrf => {
    fetch(`/coach/student/${studentId}/remove/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        const card = btn.closest('.coach-student');
        if (card) {
          card.style.transition = 'opacity 300ms, transform 300ms';
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          setTimeout(() => card.remove(), 300);
        }
        showToast('Ученик исключён');
      }
    })
    .catch(() => showToast('Ошибка', true));
  });
}

// ---- Поиск учеников ----
const studentSearch = document.getElementById('student-search');
if (studentSearch) {
  studentSearch.addEventListener('input', function () {
    const q = this.value.toLowerCase();
    document.querySelectorAll('.coach-student').forEach(card => {
      const name = card.dataset.name ?? '';
      card.style.display = name.includes(q) ? '' : 'none';
    });
  });
}

// ---- Получить CSRF-токен ----
function getCsrfToken() {
  return Promise.resolve(
    document.querySelector('[name=csrfmiddlewaretoken]')?.value ?? ''
  );
}

// ---- Автоскрытие сообщений Django ----
document.querySelectorAll('.coach-msg').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity 400ms';
    msg.style.opacity = '0';
    setTimeout(() => msg.remove(), 400);
  }, 4000);
});