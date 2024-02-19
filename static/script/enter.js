const form = document.getElementById('form');
form.addEventListener('keypress', function(e) {
  if (e.keyCode === 13 && e.target.tagName !== 'TEXTAREA') {
    e.preventDefault();
  }
});