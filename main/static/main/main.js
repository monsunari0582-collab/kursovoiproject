// Загружает HTML-компонент в указанный элемент
async function loadComponent(selector, url) {
  const el = document.querySelector(selector);
  if (!el) return;

  const response = await fetch(url);
  const html = await response.text();
  el.innerHTML = html;
}

// Подсвечивает активный пункт меню по текущему URL
function setActiveNav() {
  const links = document.querySelectorAll('header nav a');
  const currentPath = window.location.pathname;

  links.forEach(link => {
    const li = link.parentElement;
    li.classList.remove('active');

    const linkPath = new URL(link.href).pathname;
    if (linkPath === currentPath) {
      li.classList.add('active');
    }
  });
}

// Бургер-меню
function initBurger() {
  const burger = document.getElementById('burger');
  const nav = document.getElementById('main-nav');
  if (!burger || !nav) return;

  burger.addEventListener('click', () => {
    nav.classList.toggle('open');
  });
}

// Добавляет класс scrolled на хедер при прокрутке
function initScrollHeader() {
  const header = document.querySelector('header');
  if (!header) return;

  const threshold = 40;

  const update = () => {
    header.classList.toggle('scrolled', window.scrollY > threshold);
  };

  window.addEventListener('scroll', update, { passive: true });
  update();
}

// Анимации появления при скролле
function initReveal() {
  const els = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (!els.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  els.forEach(el => observer.observe(el));
}

// Переключение табов расписания
function initScheduleTabs() {
  const tabs = document.querySelectorAll('.sched-tab');
  const days = document.querySelectorAll('.sched-day');
  if (!tabs.length) return;

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const day = tab.dataset.day;

      tabs.forEach(t => t.classList.remove('active'));
      days.forEach(d => d.classList.remove('active'));

      tab.classList.add('active');
      const targetDay = document.getElementById('day-' + day);
      if (targetDay) targetDay.classList.add('active');
    });
  });
}

// Запуск
async function init() {
  setActiveNav();
  initBurger();
  initScrollHeader();
  initReveal();
  initScheduleTabs();
}

init();

// ---- Тема (светлая / тёмная) ----
function initTheme() {
  const STORAGE_KEY = 'khtisport_theme';
  const root = document.documentElement;

  // Восстанавливаем сохранённую тему
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'light') root.classList.add('theme-light');

  // Создаём кнопку переключения
  const btn = document.createElement('button');
  btn.className = 'theme-toggle';
  btn.setAttribute('aria-label', 'Переключить тему');
  btn.innerHTML = `
    <i class="fa-solid fa-sun icon-sun"></i>
    <i class="fa-solid fa-moon icon-moon"></i>
  `;

  // Вставляем в шапку рядом с бургером
  const inheader = document.querySelector('.inheader');
  if (inheader) {
    const burger = document.getElementById('burger');
    if (burger) {
      inheader.insertBefore(btn, burger);
    } else {
      inheader.appendChild(btn);
    }
  }

  btn.addEventListener('click', () => {
    const isLight = root.classList.toggle('theme-light');
    localStorage.setItem(STORAGE_KEY, isLight ? 'light' : 'dark');
  });
}

initTheme();
