// factory-demo — SVTIVA Lifestyle
// Progressive-enhancement JS: mobile nav toggle + contact form validation/states.
// FAQ accordion needs no JS — it uses native <details>/<summary>.

(function () {
  'use strict';

  function initNavToggle() {
    var toggle = document.querySelector('.nav-toggle');
    var nav = document.getElementById('primary-nav');
    if (!toggle || !nav) return;

    toggle.addEventListener('click', function () {
      var isOpen = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(isOpen));
      toggle.textContent = isOpen ? 'Close' : 'Menu';
    });

    nav.addEventListener('click', function (event) {
      if (event.target.tagName === 'A' && window.matchMedia('(max-width: 1023px)').matches) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = 'Menu';
      }
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        nav.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.textContent = 'Menu';
        toggle.focus();
      }
    });
  }

  // NOTE: No real form backend is configured yet (contact-form provider is
  // still an open decision — see architecture/ARCHITECTURE.md Section 11 and
  // design/UI-UX-SPEC.md Section 2). This handler performs real client-side
  // validation and real interaction states, but the "submission" itself is
  // simulated. Wire this to the chosen provider (e.g. Netlify Forms /
  // Formspree) before any real launch.
  function initContactForm() {
    var form = document.getElementById('contact-form');
    if (!form) return;

    var statusEl = document.getElementById('form-status');
    var successEl = document.getElementById('form-success');
    var submitBtn = form.querySelector('button[type="submit"]');

    function setFieldError(field, message) {
      var wrapper = field.closest('.form-field');
      var errorEl = wrapper.querySelector('.error-message');
      if (message) {
        wrapper.classList.add('has-error');
        if (errorEl) errorEl.textContent = message;
        field.setAttribute('aria-invalid', 'true');
      } else {
        wrapper.classList.remove('has-error');
        if (errorEl) errorEl.textContent = '';
        field.removeAttribute('aria-invalid');
      }
    }

    function validateField(field) {
      if (!field.hasAttribute('required') && field.value.trim() === '') return true;

      if (field.type === 'email') {
        var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(field.value.trim())) {
          setFieldError(field, 'Enter a valid email address.');
          return false;
        }
      }

      if (field.hasAttribute('required') && field.value.trim() === '') {
        var label = field.closest('.form-field').querySelector('label');
        var name = label ? label.textContent.replace('(required)', '').trim() : 'This field';
        setFieldError(field, name + ' is required.');
        return false;
      }

      setFieldError(field, null);
      return true;
    }

    var fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(function (field) {
      field.addEventListener('blur', function () {
        validateField(field);
      });
    });

    form.addEventListener('submit', function (event) {
      event.preventDefault();

      var allValid = true;
      fields.forEach(function (field) {
        if (!validateField(field)) allValid = false;
      });

      if (!allValid) {
        statusEl.textContent = 'Please fix the highlighted fields and try again.';
        statusEl.setAttribute('data-state', 'error');
        var firstError = form.querySelector('.has-error input, .has-error select, .has-error textarea');
        if (firstError) firstError.focus();
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';
      statusEl.textContent = 'Sending your message...';
      statusEl.setAttribute('data-state', 'submitting');

      // Simulated network delay standing in for the real form-provider call.
      window.setTimeout(function () {
        form.hidden = true;
        statusEl.textContent = '';
        statusEl.removeAttribute('data-state');
        successEl.hidden = false;
        successEl.setAttribute('tabindex', '-1');
        successEl.focus();
      }, 700);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initNavToggle();
    initContactForm();
  });
})();
