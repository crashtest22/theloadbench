/**
 * The Load Bench — main.js
 * Newsletter subscribe via Beehiiv API v2
 * Publication: pub_5ad2a957-8062-45a2-9cce-375964c3f64c
 */

(function () {
  'use strict';

  const BEEHIIV_PUB_ID = 'pub_5ad2a957-8062-45a2-9cce-375964c3f64c';
  const BEEHIIV_API_KEY = 'gP2TGGMWI5GBFTgkGPWG6J6iVOCysjLVmbxQL9XCzU04RDPezRQVRYcNrvPJyNy5';
  const BEEHIIV_URL = 'https://api.beehiiv.com/v2/publications/' + BEEHIIV_PUB_ID + '/subscriptions';

  const forms = document.querySelectorAll('form[id^="subscribe-form"]');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      const emailInput = form.querySelector('input[type="email"]');
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!emailInput || !emailInput.value) return;

      const email = emailInput.value.trim();
      if (!email) return;

      emailInput.disabled = true;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Subscribing...';

      fetch(BEEHIIV_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + BEEHIIV_API_KEY
        },
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
        if (res.ok || res.status === 200 || res.status === 201) {
          submitBtn.textContent = '✓ You\'re in!';
          submitBtn.style.backgroundColor = '#16a34a';
          emailInput.value = '';

          const successMsg = form.nextElementSibling;
          if (successMsg && successMsg.classList.contains('form-success')) {
            successMsg.classList.add('visible');
          }
        } else {
          return res.json().then(function(data) {
            throw new Error(data.message || 'Subscription failed');
          });
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
