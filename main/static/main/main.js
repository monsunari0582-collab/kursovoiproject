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

// Запуск
async function init() {
  setActiveNav();
  initBurger();
  initScrollHeader();
  initReveal();
}

init();