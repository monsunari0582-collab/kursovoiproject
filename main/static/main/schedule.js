// ============================================================
// РАСПИСАНИЕ — schedule.js
// ============================================================

// ---- Переключение дней ----
document.querySelectorAll('.sched-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.sched-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sched-day').forEach(d => d.classList.remove('active'));

    tab.classList.add('active');
    const day = document.getElementById('day-' + tab.dataset.day);
    if (day) day.classList.add('active');

    // При смене дня сбросить фильтр спорта
    currentSport = 'all';
    document.querySelectorAll('.sport-filter').forEach(f => f.classList.remove('active'));
    document.querySelector('.sport-filter[data-sport="all"]')?.classList.add('active');
    applyFilter();
  });
});

// ---- Фильтр по виду спорта ----
let currentSport = 'all';

document.querySelectorAll('.sport-filter').forEach(btn => {
  btn.addEventListener('click', () => {
    currentSport = btn.dataset.sport;
    document.querySelectorAll('.sport-filter').forEach(f => f.classList.remove('active'));
    btn.classList.add('active');
    applyFilter();
  });
});

function applyFilter() {
  const activeDay = document.querySelector('.sched-day.active');
  if (!activeDay) return;

  activeDay.querySelectorAll('.sched-card').forEach(card => {
    const match = currentSport === 'all' || card.dataset.sport === currentSport;
    card.style.display = match ? '' : 'none';
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
