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

// ── Отправка формы входа — только валидация, форма сабмитится нативно ──
document.getElementById('forma-login').addEventListener('submit', e => {
  const email = document.getElementById('email-vhod').value.trim();
  const parol = document.getElementById('parol-vhod').value;

  const emailErr = !proveritEmail(email);
  const parolErr = !parol;
  pokazatOshibku('obertka-email-vhod', emailErr);
  pokazatOshibku('obertka-parol-vhod', parolErr);

  if (emailErr || parolErr) {
    e.preventDefault(); // блокируем только если есть ошибки
  }
  // иначе — форма уходит на сервер сама
});

// ── Отправка формы регистрации — только валидация, форма сабмитится нативно ──
document.getElementById('forma-register').addEventListener('submit', e => {
  const imya    = document.getElementById('imya').value.trim();
  const email   = document.getElementById('email-reg').value.trim();
  const telefon = document.getElementById('telefon').value;
  const parol   = document.getElementById('parol-reg').value;
  const parol2  = document.getElementById('parol-reg2').value;
  const soglasie = document.getElementById('checkbox-soglasie').checked;

  const imyaErr   = !imya;
  const emailErr  = !proveritEmail(email);
  const telErr    = !proveritTelefon(telefon);
  const parolErr  = parol.length < 8;
  const parol2Err = parol !== parol2;

  pokazatOshibku('obertka-imya',       imyaErr);
  pokazatOshibku('obertka-email-reg',  emailErr);
  pokazatOshibku('obertka-telefon',    telErr);
  pokazatOshibku('obertka-parol-reg',  parolErr);
  pokazatOshibku('obertka-parol-reg2', parol2Err);

  if (imyaErr || emailErr || telErr || parolErr || parol2Err || !soglasie) {
    e.preventDefault(); // блокируем только если есть ошибки
  }
  // иначе — форма уходит на сервер сама
});

// ── Выбор роли ──
document.querySelectorAll('.rol-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.rol-btn').forEach(b => b.classList.remove('aktivny'));
    btn.classList.add('aktivny');
    document.getElementById('vybranaya-rol').value = btn.dataset.rol;
  });
});
