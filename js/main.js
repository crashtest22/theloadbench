/**
 * The Load Bench — main.js
 * Newsletter subscribe via Beehiiv embedded form API
 * Publication ID: 5ad2a957-8062-45a2-9cce-375964c3f64c
 */

(function () {
  'use strict';

  const BEEHIIV_PUB_ID = '5ad2a957-8062-45a2-9cce-375964c3f64c';
  const BEEHIIV_URL = 'https://app.beehiiv.com/api/v1/publications/' + BEEHIIV_PUB_ID + '/subscriptions';

  const forms = document.querySelectorAll('form[id^="subscribe-form"]');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const emailInput = form.querySelector('input[type="email"]');
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!emailInput || !emailInput.value) return;

      const email = emailInput.value.trim();
      if (!email) return;

      // Disable inputs while processing
      emailInput.disabled = true;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Subscribing...';

      fetch(BEEHIIV_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          reactivate_existing: true,
          send_welcome_email: true,
          utm_source: 'website',
          utm_medium: 'organic',
          utm_campaign: 'theloadbench'
        })
      })
      .then(function (res) {
        if (res.ok || res.status === 201 || res.status === 200) {
          submitBtn.textContent = '✓ You\'re in!';
          submitBtn.style.backgroundColor = '#16a34a';
          emailInput.value = '';

          const successMsg = form.nextElementSibling;
          if (successMsg && successMsg.classList.contains('form-success')) {
            successMsg.classList.add('visible');
          }
        } else {
          throw new Error('Subscription failed: ' + res.status);
        }
      })
      .catch(function (err) {
        console.error('Subscribe error:', err);
        submitBtn.textContent = 'Try again';
        submitBtn.disabled = false;
        emailInput.disabled = false;
        submitBtn.style.backgroundColor = '';
      });
    });
  });

})();
