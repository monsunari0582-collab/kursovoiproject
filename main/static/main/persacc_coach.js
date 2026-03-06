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
document.querySelectorAll('.coach-week__day').forEach(day => {
  day.addEventListener('click', () => {
    document.querySelectorAll('.coach-week__day').forEach(d => d.classList.remove('active'));
    day.classList.add('active');
  });
});

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

// ---- Toast ----
function showToast(msg) {
  const toast = document.getElementById('toast');
  const text  = document.getElementById('toast-text');
  if (!toast || !text) return;
  text.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// ---- Удалить тренировку ----
function deleteSession(btn) {
  const slot = btn.closest('.coach-slot');
  if (!slot) return;
  slot.style.transition = 'opacity 300ms, transform 300ms';
  slot.style.opacity = '0';
  slot.style.transform = 'translateX(14px)';
  setTimeout(() => slot.remove(), 300);
  showToast('Тренировка удалена');
}

// ---- Удалить ученика ----
function deleteStudent(btn) {
  const card = btn.closest('.coach-student');
  if (!card) return;
  card.style.transition = 'opacity 300ms, transform 300ms';
  card.style.opacity = '0';
  card.style.transform = 'scale(0.95)';
  setTimeout(() => card.remove(), 300);
  showToast('Ученик удалён');
}

// ---- Поиск учеников ----
const studentSearch = document.getElementById('student-search');
if (studentSearch) {
  studentSearch.addEventListener('input', function () {
    const q = this.value.toLowerCase();
    document.querySelectorAll('.coach-student').forEach(card => {
      const name = card.querySelector('.coach-student__name')?.textContent.toLowerCase() ?? '';
      card.style.display = name.includes(q) ? '' : 'none';
    });
  });
}

// ---- Фильтр по секции ----
const studentFilter = document.getElementById('student-filter');
if (studentFilter) {
  studentFilter.addEventListener('change', function () {
    const val = this.value;
    document.querySelectorAll('.coach-student').forEach(card => {
      card.style.display = (val === 'all' || card.dataset.section === val) ? '' : 'none';
    });
  });
}