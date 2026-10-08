(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduce) root.classList.add('m-on');
  var PAGE = '{{PAGE}}', PREVIEW = {{PREVIEW}};
  document.querySelectorAll('[data-nav="' + PAGE + '"]').forEach(function (a) { a.setAttribute('aria-current', 'page'); });

  var hdr = document.querySelector('.hdr'), tick = false;
  addEventListener('scroll', function () { if (tick) return; tick = true; requestAnimationFrame(function () { hdr.classList.toggle('is-condensed', scrollY > 40); tick = false; }); }, { passive: true });
  var mb = document.getElementById('menuBtn'), mn = document.getElementById('mnav');
  function setMenu(o) { mb.setAttribute('aria-expanded', o); mb.setAttribute('aria-label', o ? 'Close menu' : 'Open menu'); mn.hidden = !o; }
  mb.addEventListener('click', function () { setMenu(mn.hidden); });
  mn.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !mn.hidden) { setMenu(false); mb.focus(); } });

  var form = document.querySelector('form[data-netlify]');
  if (!form) return;
  var email = form.querySelector('input[type="email"]');
  function clearErr() { var f = email.closest('.field'); f.classList.remove('bad'); var e = f.querySelector('.err'); if (e) e.remove(); email.removeAttribute('aria-invalid'); }
  email.addEventListener('input', clearErr);
  form.setAttribute('novalidate', '');
  form.addEventListener('submit', function (e) {
    var v = email.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) {
      e.preventDefault(); clearErr();
      var f = email.closest('.field'); f.classList.add('bad'); email.setAttribute('aria-invalid', 'true');
      var s = document.createElement('span'); s.className = 'err'; s.id = email.id + '-err'; s.setAttribute('role', 'alert');
      s.textContent = v ? 'That email address doesn’t look right. Check it and try again.' : 'Add your email address so we can reply.';
      f.appendChild(s); email.setAttribute('aria-describedby', s.id); email.focus();
      return;
    }
    if (!PREVIEW) return;            // live site: Netlify receives the form and shows the thank-you page
    e.preventDefault();
    var card = form.closest('.card');
    card.innerHTML = '<div class="done"><img src="img/mark.png" alt="" width="80" height="80"><h2>Thanks, we’ve got it</h2><p>Your application has been received. A member of the Tech Operators team will be in touch.</p><p class="fine">Preview only: nothing was sent.</p></div>';
    card.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' });
  });
})();
