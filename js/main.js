/**
 * The Load Bench — main.js
 * Minimal JS for form UX. Newsletter form wiring to Beehiiv goes here.
 */

(function () {
  'use strict';

  // Find all subscribe forms on the page
  const forms = document.querySelectorAll('form[id^="subscribe-form"]');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      // TODO: Replace action="#" with Beehiiv embed URL or API endpoint
      // For now, prevent default and show a placeholder message
      e.preventDefault();

      const emailInput = form.querySelector('input[type="email"]');
      const submitBtn = form.querySelector('button[type="submit"]');

      if (!emailInput || !emailInput.value) return;

      // Disable inputs while "processing"
      emailInput.disabled = true;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Subscribing...';

      // Simulate async — remove this block when real endpoint is wired
      setTimeout(function () {
        submitBtn.textContent = '✓ You\'re in!';
        submitBtn.style.backgroundColor = '#16a34a';
        emailInput.value = '';

        // Show a small success note below the form if one exists
        const successMsg = form.nextElementSibling;
        if (successMsg && successMsg.classList.contains('form-success')) {
          successMsg.classList.add('visible');
        }
      }, 800);
    });
  });

  // --- Beehiiv integration stub ---
  // When you're ready to wire Beehiiv:
  // 1. Go to your Beehiiv publication settings → Embed / Subscribe page
  // 2. Copy your publication ID and API endpoint
  // 3. Replace the setTimeout mock above with a fetch() call like:
  //
  // fetch('https://api.beehiiv.com/v2/publications/YOUR_PUB_ID/subscriptions', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_API_KEY' },
  //   body: JSON.stringify({ email: emailInput.value, reactivate_existing: true, send_welcome_email: true })
  // })
  // .then(res => res.json())
  // .then(data => { /* handle success */ })
  // .catch(err => { /* handle error */ });
  //
  // Or simply set form action to your Beehiiv subscribe URL and let it POST natively.

})();
