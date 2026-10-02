/* The stored theme, applied before the first paint.
 *
 * This is three lines and it would be an inline <script> on most sites. It
 * cannot be one here: both sites send `script-src 'self'` with no hash and no
 * 'unsafe-inline', so an inline block is refused by the browser and the page
 * silently keeps whatever the system asked for. A reader who had chosen light
 * on a machine set to dark got dark back on every reload, and the only sign of
 * it was a console violation nobody reads.
 *
 * It has to be a blocking script in <head>, not deferred: deferred runs after
 * the document is parsed, which is after the first paint, which is the flash
 * this exists to prevent. */
(function () {
  try {
    var t = localStorage.getItem('jj-theme');
    if (t === 'dark' || t === 'light') document.documentElement.setAttribute('data-theme', t);
  } catch (e) { /* a private window refuses storage; the media query still decides */ }
})();
