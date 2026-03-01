// ============================================================
// КАБИНЕТ ТРЕНЕРА — KHTISPORT
// ============================================================

// ---- Навигация по табам ----
const navItems = document.querySelectorAll('.cab-nav__item[data-tab]');
const sections = document.querySelectorAll('.cab-section');

navItems.forEach(item => {
  item.addEventListener('click', () => {
    const tab = item.dataset.tab;

    navItems.forEach(n => n.classList.remove('active'));
    sections.forEach(s => s.classList.remove('active'));

    item.classList.add('active');
    document.getElementById('sec-' + tab).classList.add('active');
  });
});

// ---- Дни недели ----
document.querySelectorAll('.week-day').forEach(day => {
  day.addEventListener('click', () => {
    document.querySelectorAll('.week-day').forEach(d => d.classList.remove('active'));
    day.classList.add('active');
  });
});

// ---- Модалки ----
function openModal(id) {
  document.getElementById(id).classList.add('open');
}

function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

function closeModalOnOverlay(e, id) {
  if (e.target === e.currentTarget) closeModal(id);
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
});

// ---- Toast ----
function showToast(msg) {
  const toast = document.getElementById('toast');
  document.getElementById('toast-text').textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 2800);
}

// ---- Удалить тренировку ----
function deleteSession(btn) {
  const slot = btn.closest('.sched-slot');
  slot.style.transition = 'opacity 300ms, transform 300ms';
  slot.style.opacity = '0';
  slot.style.transform = 'translateX(20px)';
  setTimeout(() => slot.remove(), 300);
  showToast('Тренировка удалена');
}

// ---- Удалить ученика ----
function deleteStudent(btn) {
  const card = btn.closest('.student-card');
  card.style.transition = 'opacity 300ms, transform 300ms';
  card.style.opacity = '0';
  card.style.transform = 'scale(0.95)';
  setTimeout(() => card.remove(), 300);
  showToast('Ученик удалён');
}

// ---- Поиск учеников ----
document.getElementById('student-search').addEventListener('input', function() {
  const q = this.value.toLowerCase();
  document.querySelectorAll('.student-card').forEach(card => {
    const name = card.querySelector('.student-card__name').textContent.toLowerCase();
    card.style.display = name.includes(q) ? '' : 'none';
  });
});

// ---- Фильтр по секции ----
document.getElementById('student-filter').addEventListener('change', function() {
  const val = this.value;
  document.querySelectorAll('.student-card').forEach(card => {
    card.style.display = (val === 'all' || card.dataset.section === val) ? '' : 'none';
  });
});
