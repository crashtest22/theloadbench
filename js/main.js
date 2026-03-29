/**
 * The Load Bench — main.js
 * Newsletter subscribe via Beehiiv magic link
 */

(function () {
  'use strict';

  const BEEHIIV_MAGIC = 'https://magic.beehiiv.com/v1/5ad2a957-8062-45a2-9cce-375964c3f64c?email=';

  const forms = document.querySelectorAll('form[id^="subscribe-form"]');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const emailInput = form.querySelector('input[type="email"]');
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!emailInput || !emailInput.value) return;

      const email = encodeURIComponent(emailInput.value.trim());
      if (!email) return;

      // Brief feedback before redirect
      submitBtn.textContent = 'Redirecting...';
      submitBtn.disabled = true;
      emailInput.disabled = true;

      // Redirect to Beehiiv magic link with email pre-filled
      window.location.href = BEEHIIV_MAGIC + email + '&utm_source=website&utm_medium=organic&utm_campaign=theloadbench';
    });
  });

})();
