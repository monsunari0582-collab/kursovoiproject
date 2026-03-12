// ============================================================
// РАСПИСАНИЕ — schedule.js
// ============================================================

// ---- Переключение дней ----
document.querySelectorAll('.sched-tab:not([data-day="all"])').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.sched-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sched-day').forEach(d => {
      d.classList.remove('active');
      d.style.display = '';
    });

    tab.classList.add('active');
    const day = document.getElementById('day-' + tab.dataset.day);
    if (day) day.classList.add('active');

    currentSport = 'all';
    document.querySelectorAll('.sport-filter').forEach(f => f.classList.remove('active'));
    document.querySelector('.sport-filter[data-sport="all"]')?.classList.add('active');
    applyFilter();
  });
});

// ---- Кнопка "Все" ----
function showAllDays() {
  document.querySelectorAll('.sched-tab').forEach(t => t.classList.remove('active'));
  document.querySelector('[data-day="all"]')?.classList.add('active');

  // Показать все дни одновременно
  document.querySelectorAll('.sched-day').forEach(d => {
    d.classList.add('active');
    d.style.display = '';
  });

  currentSport = 'all';
  document.querySelectorAll('.sport-filter').forEach(f => f.classList.remove('active'));
  document.querySelector('.sport-filter[data-sport="all"]')?.classList.add('active');
  applyFilterAll();
}

// ---- Фильтр по виду спорта ----
let currentSport = 'all';

document.querySelectorAll('.sport-filter').forEach(btn => {
  btn.addEventListener('click', () => {
    currentSport = btn.dataset.sport;
    document.querySelectorAll('.sport-filter').forEach(f => f.classList.remove('active'));
    btn.classList.add('active');

    const allActive = document.querySelector('[data-day="all"]')?.classList.contains('active');
    allActive ? applyFilterAll() : applyFilter();
  });
});

function applyFilter() {
  const activeDay = document.querySelector('.sched-day.active');
  if (!activeDay) return;
  activeDay.querySelectorAll('.sched-card').forEach(card => {
    card.style.display = (currentSport === 'all' || card.dataset.sport === currentSport) ? '' : 'none';
  });
}

function applyFilterAll() {
  document.querySelectorAll('.sched-day').forEach(day => {
    let hasVisible = false;
    day.querySelectorAll('.sched-card').forEach(card => {
      const show = currentSport === 'all' || card.dataset.sport === currentSport;
      card.style.display = show ? '' : 'none';
      if (show) hasVisible = true;
    });
    // Скрыть день если в нём нет совпадений
    day.style.display = hasVisible ? '' : 'none';
  });
}

// ---- Автоскрытие сообщений ----
document.querySelectorAll('.schedule-msg').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity 400ms, transform 400ms';
    msg.style.opacity = '0';
    msg.style.transform = 'translateY(10px)';
    setTimeout(() => msg.remove(), 400);
  }, 3500);
});