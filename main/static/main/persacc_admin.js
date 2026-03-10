// ============================================================
// КАБИНЕТ АДМИНИСТРАТОРА — persacc_admin.js
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

// ---- Модалки ----
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
function closeModalOnOverlay(e, id) {
  if (e.target === e.currentTarget) closeModal(id);
}
document.addEventListener('keydown', e => {
  if (e.key === 'Escape')
    document.querySelectorAll('.coach-modal-overlay.open').forEach(m => m.classList.remove('open'));
});

// ---- Toast ----
function showToast(msg, isError = false) {
  const toast = document.getElementById('toast');
  const text  = document.getElementById('toast-text');
  if (!toast || !text) return;
  text.textContent = msg;
  toast.querySelector('i').className = isError
    ? 'fa-solid fa-triangle-exclamation'
    : 'fa-solid fa-circle-check';
  toast.style.borderColor = isError ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)';
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

function getCsrfToken() {
  return Promise.resolve(
    document.querySelector('[name=csrfmiddlewaretoken]')?.value ?? ''
  );
}

// ---- Поиск пользователей ----
document.getElementById('user-search')?.addEventListener('input', filterUsers);
document.getElementById('role-filter')?.addEventListener('change', filterUsers);

function filterUsers() {
  const q    = document.getElementById('user-search')?.value.toLowerCase() ?? '';
  const role = document.getElementById('role-filter')?.value ?? 'all';

  document.querySelectorAll('.admin-table-row').forEach(row => {
    const name    = row.dataset.name ?? '';
    const rowRole = row.dataset.role ?? '';
    const matchQ  = name.includes(q);
    const matchR  = role === 'all' || rowRole === role;
    row.style.display = (matchQ && matchR) ? '' : 'none';
  });
}

// ---- Поиск тренировок ----
document.getElementById('session-search')?.addEventListener('input', filterSessions);
document.getElementById('sport-filter')?.addEventListener('change', filterSessions);

function filterSessions() {
  const q     = document.getElementById('session-search')?.value.toLowerCase() ?? '';
  const sport = document.getElementById('sport-filter')?.value ?? 'all';

  document.querySelectorAll('.admin-sessions-list .coach-slot').forEach(row => {
    const text     = row.dataset.text ?? '';
    const rowSport = row.dataset.sport ?? '';
    const matchQ   = text.includes(q);
    const matchS   = sport === 'all' || rowSport === sport;
    row.style.display = (matchQ && matchS) ? '' : 'none';
  });
}

// ---- Изменить роль пользователя ----
function changeRole(userId, newRole) {
  getCsrfToken().then(csrf => {
    fetch(`/admin-panel/user/${userId}/role/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ role: newRole }),
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        showToast('Роль изменена');
        const row = document.getElementById('user-row-' + userId);
        if (row) row.dataset.role = newRole;
      } else {
        showToast(data.error || 'Ошибка', true);
      }
    })
    .catch(() => showToast('Ошибка соединения', true));
  });
}

// ---- Блокировка / разблокировка ----
function toggleBlock(userId, activate, btn) {
  const msg = activate ? 'Разблокировать пользователя?' : 'Заблокировать пользователя?';
  if (!confirm(msg)) return;

  getCsrfToken().then(csrf => {
    fetch(`/admin-panel/user/${userId}/block/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrf,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ is_active: activate }),
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        showToast(activate ? 'Пользователь разблокирован' : 'Пользователь заблокирован');
        // Обновить бейдж и кнопку
        const row = document.getElementById('user-row-' + userId);
        if (!row) return;
        const badge = row.querySelector('.admin-badge');
        if (badge) {
          badge.className = activate ? 'admin-badge admin-badge--active' : 'admin-badge admin-badge--blocked';
          badge.textContent = activate ? 'Активен' : 'Заблокирован';
        }
        // Заменить кнопку
        btn.outerHTML = activate
          ? `<button class="coach-act-btn coach-act-btn--del" title="Заблокировать" onclick="toggleBlock(${userId}, false, this)"><i class="fa-solid fa-ban"></i></button>`
          : `<button class="coach-act-btn" title="Разблокировать" onclick="toggleBlock(${userId}, true, this)"><i class="fa-solid fa-circle-check"></i></button>`;
      }
    })
    .catch(() => showToast('Ошибка', true));
  });
}

// ---- Удалить пользователя ----
function deleteUser(userId, btn) {
  if (!confirm('Удалить пользователя? Это действие нельзя отменить.')) return;

  getCsrfToken().then(csrf => {
    fetch(`/admin-panel/user/${userId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        const row = document.getElementById('user-row-' + userId);
        if (row) {
          row.style.transition = 'opacity 300ms';
          row.style.opacity = '0';
          setTimeout(() => row.remove(), 300);
        }
        showToast('Пользователь удалён');
      }
    })
    .catch(() => showToast('Ошибка', true));
  });
}

// ---- Удалить тренировку (admin) ----
function adminDeleteSession(sessionId, btn) {
  if (!confirm('Удалить тренировку?')) return;

  getCsrfToken().then(csrf => {
    fetch(`/admin-panel/session/${sessionId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        const el = document.getElementById('admin-session-' + sessionId);
        if (el) {
          el.style.transition = 'opacity 300ms, transform 300ms';
          el.style.opacity = '0';
          el.style.transform = 'translateX(14px)';
          setTimeout(() => el.remove(), 300);
        }
        showToast('Тренировка удалена');
      }
    })
    .catch(() => showToast('Ошибка', true));
  });
}

// ---- Редактировать зал ----
function openEditLocation(id, name, capacity, isActive) {
  document.getElementById('edit_loc_name').value     = name;
  document.getElementById('edit_loc_capacity').value = capacity;
  document.getElementById('edit_loc_active').value   = isActive ? '1' : '0';
  document.getElementById('editLocationForm').action = `/admin-panel/location/${id}/edit/`;
  openModal('modal-edit-location');
}

// ---- Удалить зал ----
function deleteLocation(locId, btn) {
  if (!confirm('Удалить зал?')) return;

  getCsrfToken().then(csrf => {
    fetch(`/admin-panel/location/${locId}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf },
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        const el = document.getElementById('loc-' + locId);
        if (el) {
          el.style.transition = 'opacity 300ms, transform 300ms';
          el.style.opacity = '0';
          el.style.transform = 'scale(0.95)';
          setTimeout(() => el.remove(), 300);
        }
        showToast('Зал удалён');
      }
    })
    .catch(() => showToast('Ошибка', true));
  });
}

// ---- Автоскрытие сообщений ----
document.querySelectorAll('.coach-msg').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity 400ms';
    msg.style.opacity = '0';
    setTimeout(() => msg.remove(), 400);
  }, 4000);
});
