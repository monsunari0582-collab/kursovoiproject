// ============================================================
// РАСПИСАНИЕ — schedule.js  (растягивающиеся блоки по времени)
// ============================================================

(function () {
  'use strict';

  const HOUR_START  = 10;
  const HOUR_END    = 21;
  const HOUR_PX     = 60;  // высота одного часа в пикселях
  const HOURS       = Array.from({ length: HOUR_END - HOUR_START }, (_, i) => HOUR_START + i);
  const WEEKDAYS_RU = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
  const MONTHS_RU   = ['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек'];

  const rawDataEl = document.getElementById('schedule-data');
  if (!rawDataEl) return;

  let allSessions = [];
  try {
    allSessions = JSON.parse(rawDataEl.textContent || '[]');
  } catch (e) {
    console.error('schedule-data parse error', e);
    return;
  }

  allSessions.forEach(s => {
    s._dateObj = new Date(s.date + 'T' + s.time + ':00');
    const h = s._dateObj.getHours();
    const m = s._dateObj.getMinutes();
    s._startMin    = (h - HOUR_START) * 60 + m;  // минуты от начала таблицы
    s._durationMin = s.duration || 60;
  });

  let currentSport    = 'all';
  let currentLocation = document.querySelector('.location-filter.active')?.dataset.location ?? 'all';
  let weekOffset      = 0;
  let activeTooltipEl = null;

  function startOfToday() {
    const d = new Date(); d.setHours(0,0,0,0); return d;
  }
  function addDays(d, n) {
    const r = new Date(d); r.setDate(r.getDate() + n); return r;
  }
  function sameDate(a, b) {
    return a.getFullYear() === b.getFullYear() &&
           a.getMonth()    === b.getMonth()    &&
           a.getDate()     === b.getDate();
  }
  function fmt2(n) { return String(n).padStart(2, '0'); }
  function isoDate(d) {
    return `${d.getFullYear()}-${fmt2(d.getMonth()+1)}-${fmt2(d.getDate())}`;
  }
  function minToPx(min) { return (min / 60) * HOUR_PX; }
  function getWeekDays() {
    const today = startOfToday();
    return Array.from({ length: 7 }, (_, i) => addDays(today, weekOffset * 7 + i));
  }
  function filteredSessions() {
    return allSessions.filter(s => {
      const sportOk    = currentSport    === 'all' || s.sport    === currentSport;
      const locationOk = currentLocation === 'all' || s.location === currentLocation;
      return sportOk && locationOk;
    });
  }

  // Вычисляет конечное время тренировки
  function endTime(s) {
    const totalMin = s._dateObj.getHours() * 60 + s._dateObj.getMinutes() + s._durationMin;
    return `${fmt2(Math.floor(totalMin / 60) % 24)}:${fmt2(totalMin % 60)}`;
  }

  const container = document.getElementById('scheduleGridContainer');
  if (!container) return;

  function render() {
    const days        = getWeekDays();
    const today       = startOfToday();
    const sessions    = filteredSessions();
    const totalHeight = HOURS.length * HOUR_PX;

    const rangeLabel = `${days[0].getDate()} ${MONTHS_RU[days[0].getMonth()]} — ` +
                       `${days[6].getDate()} ${MONTHS_RU[days[6].getMonth()]} ${days[6].getFullYear()}`;

    let html = `
      <div class="week-nav reveal">
        <button class="week-nav__btn" id="prevWeek" ${weekOffset <= 0 ? 'disabled' : ''}>&#8592;</button>
        <button class="week-nav__today" id="toToday">Сегодня</button>
        <span class="week-nav__label">${rangeLabel}</span>
        <button class="week-nav__btn" id="nextWeek">&#8594;</button>
      </div>
      <div class="schedule-grid-wrap reveal">
    `;

    // ── Шапка ──
    html += `<div class="sg-header"><div class="sg-header__time-col"></div>`;
    days.forEach(day => {
      const isToday = sameDate(day, today);
      html += `
        <div class="sg-header__day ${isToday ? 'sg-header__day--today' : ''}">
          <span class="sg-col-header__weekday">${WEEKDAYS_RU[day.getDay()]}</span>
          <span class="sg-col-header__date">${day.getDate()}</span>
          <span class="sg-col-header__month">${MONTHS_RU[day.getMonth()]}</span>
        </div>`;
    });
    html += `</div>`;

    // ── Тело ──
    html += `<div class="sg-body">`;

    // Метки времени
    html += `<div class="sg-time-col">`;
    HOURS.forEach(hour => {
      html += `<div class="sg-time-label" style="height:${HOUR_PX}px">${fmt2(hour)}:00</div>`;
    });
    html += `</div>`;

    // Колонки дней
    days.forEach(day => {
      const isToday     = sameDate(day, today);
      const dayIso      = isoDate(day);
      const daySessions = sessions.filter(s => s.date === dayIso);

      html += `<div class="sg-day-col ${isToday ? 'sg-day-col--today' : ''}" style="height:${totalHeight}px">`;

      // Линии часов
      HOURS.forEach((_, i) => {
        html += `<div class="sg-hour-line" style="top:${i * HOUR_PX}px"></div>`;
        // Линия получаса (пунктир)
        html += `<div class="sg-half-line" style="top:${i * HOUR_PX + HOUR_PX / 2}px"></div>`;
      });

      // События
      daySessions.forEach(s => {
        const topPx    = minToPx(s._startMin);
        const heightPx = Math.max(minToPx(s._durationMin), 24);
        const endStr   = endTime(s);
        const startStr = `${fmt2(s._dateObj.getHours())}:${fmt2(s._dateObj.getMinutes())}`;
        const coach    = s.coach_name || 'Тренер не назначен';
        const isFull   = s.is_full;

        // Адаптируем контент под высоту блока
        const isTiny  = heightPx < 40;   // только время
        const isShort = heightPx < 68;   // время + вид спорта

        html += `
          <div class="sg-event sg-event--${s.sport}"
               role="button" tabindex="0"
               style="top:${topPx}px; height:${heightPx}px;"
               data-session-id="${s.id}"
               data-sport="${s.sport}"
               data-sport-name="${s.sport_name}"
               data-time="${startStr}"
               data-end-time="${endStr}"
               data-date="${day.getDate()} ${MONTHS_RU[day.getMonth()]}"
               data-coach="${coach}"
               data-coach-id="${s.coach_id || ''}"
               data-location="${s.location || ''}"
               data-enrolled="${s.enrolled_count}"
               data-max="${s.max_places}"
               data-duration="${s.duration}"
               data-is-full="${isFull ? '1' : '0'}"
               data-enrolled-me="${s.enrolled_me ? '1' : '0'}"
          >
            <span class="sg-event__time">${startStr}–${endStr}</span>
            ${!isTiny ? `<span class="sg-event__sport">${s.sport_name}</span>` : ''}
            ${!isShort ? `
              <span class="sg-event__coach"><i class="fa-solid fa-user"></i>${coach}</span>
              <div class="sg-event__meta">
                <span class="sg-event__badge"><i class="fa-solid fa-users"></i>${s.enrolled_count}/${s.max_places}</span>
                ${isFull ? '<span class="sg-event__full-badge">мест нет</span>' : ''}
              </div>` : ''}
          </div>`;
      });

      html += `</div>`; // .sg-day-col
    });

    html += `</div></div>`; // .sg-body .schedule-grid-wrap

    container.innerHTML = html;

    document.getElementById('prevWeek')?.addEventListener('click', () => {
      if (weekOffset > 0) { weekOffset--; render(); }
    });
    document.getElementById('nextWeek')?.addEventListener('click', () => { weekOffset++; render(); });
    document.getElementById('toToday')?.addEventListener('click', () => { weekOffset = 0; render(); });

    container.querySelectorAll('.sg-event').forEach(el => {
      el.addEventListener('click', e => { e.stopPropagation(); openTooltip(el); });
      el.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openTooltip(el); }
      });
    });

    if (typeof initReveal === 'function') initReveal();
  }

  // ── Тултип ───────────────────────────────────────────────
  function openTooltip(el) {
    closeTooltip();
    const d          = el.dataset;
    const isFull     = d.isFull     === '1';
    const enrolledMe = d.enrolledMe === '1';
    const isAuth     = document.body.dataset.authenticated === '1';
    const userRole   = document.body.dataset.role || '';
    const userId     = document.body.dataset.userid || '';
    const isOwn      = userRole === 'coach' && String(d.coachId) === String(userId);

    let action = '';
    if (isFull) {
      action = `<span class="sg-tooltip__action sg-tooltip__action--full">Мест нет</span>`;
    } else if (!isAuth) {
      action = `<a href="/join/?next=/schedule/" class="sg-tooltip__action sg-tooltip__action--login">Войти и записаться</a>`;
    } else if (isOwn) {
      action = `<span class="sg-tooltip__action sg-tooltip__action--full">Ваша тренировка</span>`;
    } else if (enrolledMe) {
      action = `<form method="post" action="/cancel-enrollment/${d.sessionId}/">
        <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrf()}">
        <button type="submit" class="sg-tooltip__action sg-tooltip__action--cancel">Отменить запись</button>
      </form>`;
    } else {
      action = `<form method="post" action="/enroll/${d.sessionId}/">
        <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrf()}">
        <button type="submit" class="sg-tooltip__action sg-tooltip__action--enroll">Записаться</button>
      </form>`;
    }

    const tip = document.createElement('div');
    tip.className = 'sg-tooltip';
    tip.innerHTML = `
      <button class="sg-tooltip__close" aria-label="Закрыть">&#x2715;</button>
      <span class="sg-tooltip__sport sg-tooltip__sport--${d.sport}">${d.sportName}</span>
      <div class="sg-tooltip__title">${d.time}–${d.endTime} · ${d.date}</div>
      <div class="sg-tooltip__rows">
        <div class="sg-tooltip__row"><i class="fa-solid fa-user"></i><span>${d.coach}</span></div>
        <div class="sg-tooltip__row"><i class="fa-solid fa-location-dot"></i><span>${d.location || '—'}</span></div>
        <div class="sg-tooltip__row"><i class="fa-solid fa-clock"></i><span>${d.duration} мин</span></div>
        <div class="sg-tooltip__row"><i class="fa-solid fa-users"></i><span><strong>${d.enrolled}/${d.max}</strong> мест занято</span></div>
      </div>
      ${action}`;

    document.body.appendChild(tip);
    activeTooltipEl = tip;
    positionTooltip(tip, el);
    tip.querySelector('.sg-tooltip__close').addEventListener('click', closeTooltip);
  }

  function positionTooltip(tip, anchor) {
    const rect = anchor.getBoundingClientRect();
    const tipW = 270, tipH = 300, gap = 10;
    const vp   = { w: window.innerWidth, h: window.innerHeight };
    let left = rect.right + gap;
    let top  = rect.top;
    if (left + tipW > vp.w - 8) left = rect.left - tipW - gap;
    if (left < 8) left = 8;
    if (top + tipH > vp.h - 8) top = vp.h - tipH - 8;
    if (top < 8) top = 8;
    tip.style.left = left + 'px';
    tip.style.top  = top  + 'px';
  }

  function closeTooltip() {
    if (activeTooltipEl) { activeTooltipEl.remove(); activeTooltipEl = null; }
  }

  document.addEventListener('click', e => {
    if (activeTooltipEl && !activeTooltipEl.contains(e.target)) closeTooltip();
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeTooltip(); });

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  document.querySelectorAll('.location-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      currentLocation = btn.dataset.location;
      document.querySelectorAll('.location-filter').forEach(f => f.classList.remove('active'));
      btn.classList.add('active');
      closeTooltip();
      render();
    });
  });

  document.querySelectorAll('.sport-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      currentSport = btn.dataset.sport;
      document.querySelectorAll('.sport-filter').forEach(f => f.classList.remove('active'));
      btn.classList.add('active');
      closeTooltip();
      render();
    });
  });

  document.querySelectorAll('.schedule-msg').forEach(msg => {
    setTimeout(() => {
      msg.style.transition = 'opacity 400ms, transform 400ms';
      msg.style.opacity = '0';
      msg.style.transform = 'translateY(10px)';
      setTimeout(() => msg.remove(), 400);
    }, 3500);
  });

  render();
})();