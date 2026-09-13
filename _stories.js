/* story lab: ?only=key  ?step=n  ?auto=1  ?frames=Case bay,Mobile */
(function () {
  var q = new URLSearchParams(location.search);
  function inSpec(spec, i) {
    return spec.split(',').some(function (p) {
      var m = p.split('-');
      if (m.length === 1) return +m[0] === i;
      return i >= (m[0] === '' ? 0 : +m[0]) && i <= (m[1] === '' ? 99 : +m[1]);
    });
  }
  function setStep(st, i) {
    st.setAttribute('data-step', i);
    st.querySelectorAll('[data-on]').forEach(function (el) { el.classList.toggle('is-on', inSpec(el.getAttribute('data-on'), i)); });
  }
  var only = q.get('only');
  if (only) document.querySelectorAll('[data-lab]').forEach(function (s) { if (s.getAttribute('data-lab') !== only) s.remove(); });
  var frames = q.get('frames');
  if (frames) document.querySelectorAll('.lab-f').forEach(function (f) { if (frames.split(',').indexOf(f.querySelector('p').textContent.split(' · ')[0]) < 0) f.remove(); });
  var list = Array.prototype.slice.call(document.querySelectorAll('[data-story]'));
  if (q.has('step')) list.forEach(function (st) { setStep(st, Math.min(+q.get('step'), +st.getAttribute('data-steps') - 1)); });
  if (q.get('auto')) {
    var i = 0;
    setInterval(function () {
      i++;
      list.forEach(function (st) { setStep(st, i % +st.getAttribute('data-steps')); });
    }, +(q.get('auto')) > 1 ? +q.get('auto') : 2600);
  }
})();
