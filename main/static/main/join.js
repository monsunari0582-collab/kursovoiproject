// ── Переключение вкладок ──
const pereklyuchateli = document.querySelectorAll('.pereklyuchatel');
const formy = document.querySelectorAll('.forma');
const uspeh = document.getElementById('ekran-uspeha');

pereklyuchateli.forEach(tab => {
  tab.addEventListener('click', () => {
    pereklyuchateli.forEach(t => { t.classList.remove('aktivny'); t.setAttribute('aria-selected', 'false'); });
    formy.forEach(f => f.classList.remove('aktivny'));
    uspeh.classList.remove('aktivny');
    tab.classList.add('aktivny');
    tab.setAttribute('aria-selected', 'true');
    document.getElementById('forma-' + tab.dataset.tab).classList.add('aktivny');
  });
});

// ── Показ/скрытие пароля ──
document.querySelectorAll('.knopka-glaz').forEach(btn => {
  btn.addEventListener('click', () => {
    const input = document.getElementById(btn.dataset.target);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
      input.type = 'text';
      icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
      input.type = 'password';
      icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
  });
});

// ── Маска телефона ──
const poleTelefona = document.getElementById('telefon');
poleTelefona.addEventListener('input', () => {
  let v = poleTelefona.value.replace(/\D/g, '');
  if (v.startsWith('8')) v = '7' + v.slice(1);
  if (!v.startsWith('7')) v = '7' + v;
  v = v.slice(0, 11);
  let rezultat = '+7';
  if (v.length > 1) rezultat += ' (' + v.slice(1, 4);
  if (v.length >= 4) rezultat += ') ' + v.slice(4, 7);
  if (v.length >= 7) rezultat += '-' + v.slice(7, 9);
  if (v.length >= 9) rezultat += '-' + v.slice(9, 11);
  poleTelefona.value = rezultat;
});

// ── Проверка полей ──
function pokazatOshibku(id, pokazat) {
  const obertka = document.getElementById(id);
  if (!obertka) return;
  obertka.classList.toggle('s-oshibkoy', pokazat);
}

function proveritEmail(znachenie) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(znachenie); }
function proveritTelefon(znachenie) { return znachenie.replace(/\D/g, '').length === 11; }

// ── Отправка формы входа ──
document.getElementById('forma-login').addEventListener('submit', e => {
  e.preventDefault();
  const email = document.getElementById('email-vhod').value.trim();
  const parol = document.getElementById('parol-vhod').value;
  let vsePoryadke = true;

  pokazatOshibku('obertka-email-vhod', !proveritEmail(email));
  pokazatOshibku('obertka-parol-vhod', !parol);
  if (!proveritEmail(email) || !parol) vsePoryadke = false;

  if (vsePoryadke) {
    // >>> Здесь Django POST запрос на login <<<
    pokazatUspeh('Вы вошли!', 'Добро пожаловать в KHTISPORT');
  }
});

// ── Отправка формы регистрации ──
document.getElementById('forma-register').addEventListener('submit', e => {
  e.preventDefault();
  const imya    = document.getElementById('imya').value.trim();
  const email   = document.getElementById('email-reg').value.trim();
  const telefon = document.getElementById('telefon').value;
  const parol   = document.getElementById('parol-reg').value;
  const parol2  = document.getElementById('parol-reg2').value;
  const soglasie = document.getElementById('checkbox-soglasie').checked;
  let vsePoryadke = true;

  pokazatOshibku('obertka-imya',       !imya);
  pokazatOshibku('obertka-email-reg',  !proveritEmail(email));
  pokazatOshibku('obertka-telefon',    !proveritTelefon(telefon));
  pokazatOshibku('obertka-parol-reg',  parol.length < 8);
  pokazatOshibku('obertka-parol-reg2', parol !== parol2);

  if (!imya || !proveritEmail(email) || !proveritTelefon(telefon) || parol.length < 8 || parol !== parol2 || !soglasie) vsePoryadke = false;

  if (vsePoryadke) {
    // >>> Здесь Django POST запрос на register <<<
    pokazatUspeh('Аккаунт создан!', 'Добро пожаловать в семью KHTISPORT');
  }
});

function pokazatUspeh(zagolovok, tekst) {
  formy.forEach(f => f.classList.remove('aktivny'));
  pereklyuchateli.forEach(t => t.style.display = 'none');
  document.querySelector('.vhod-logo').style.marginBottom = '16px';
  document.getElementById('uspeh-zagolovok').textContent = zagolovok;
  document.getElementById('uspeh-tekst').textContent = tekst;
  uspeh.classList.add('aktivny');
}
