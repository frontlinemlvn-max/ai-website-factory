(function () {
  "use strict";

  document.documentElement.classList.add("js");

  const menuButton = document.querySelector("[data-menu-button]");
  const menuPanel = document.querySelector("[data-menu-panel]");

  function setMenu(open, restoreFocus) {
    if (!menuButton || !menuPanel) return;

    menuButton.setAttribute("aria-expanded", String(open));
    menuPanel.dataset.open = String(open);

    const label = menuButton.querySelector("[data-menu-label]");
    if (label) label.textContent = open ? "Close menu" : "Menu";
    if (restoreFocus) menuButton.focus();
  }

  if (menuButton && menuPanel) {
    setMenu(false, false);

    menuButton.addEventListener("click", function () {
      setMenu(menuButton.getAttribute("aria-expanded") !== "true", false);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && menuButton.getAttribute("aria-expanded") === "true") {
        setMenu(false, true);
      }
    });

    window.addEventListener("resize", function () {
      if (window.matchMedia("(min-width: 60rem)").matches) setMenu(false, false);
    });
  }

  const form = document.querySelector("[data-consultation-form]");
  if (!form) return;

  const errorSummary = document.querySelector("[data-error-summary]");
  const errorList = document.querySelector("[data-error-list]");
  const successPanel = document.querySelector("[data-success-panel]");
  const startAgainButton = document.querySelector("[data-start-again]");
  const previewSubmit = form.querySelector("[data-preview-submit]");
  const message = form.querySelector("#message");
  const characterCount = document.querySelector("[data-character-count]");
  let submissionAttempted = false;

  const fields = {
    name: form.querySelector("#preferred-name"),
    email: form.querySelector("#email"),
    phone: form.querySelector("#phone"),
    message: message,
    contactMethod: Array.from(form.querySelectorAll('input[name="contact-method"]')),
    category: form.querySelector("#inquiry-category"),
    acknowledgement: form.querySelector("#acknowledgement")
  };

  function methodValue() {
    const selected = fields.contactMethod.find(function (field) { return field.checked; });
    return selected ? selected.value : "";
  }

  function updateConditionalRequirements() {
    const method = methodValue();
    fields.email.required = method === "email";
    fields.phone.required = method === "phone";
  }

  function setFieldError(field, messageText) {
    const error = document.getElementById(field.id + "-error");
    field.setAttribute("aria-invalid", "true");
    if (error) {
      error.textContent = messageText;
      error.hidden = false;
    }
  }

  function clearFieldError(field) {
    const error = document.getElementById(field.id + "-error");
    field.removeAttribute("aria-invalid");
    if (error) {
      error.textContent = "";
      error.hidden = true;
    }
  }

  function setGroupError(groupName, controls, messageText) {
    const error = document.getElementById(groupName + "-error");
    controls.forEach(function (control) {
      control.setAttribute("aria-invalid", "true");
    });
    if (error) {
      error.textContent = messageText;
      error.hidden = false;
    }
  }

  function clearGroupError(groupName, controls) {
    const error = document.getElementById(groupName + "-error");
    controls.forEach(function (control) { control.removeAttribute("aria-invalid"); });
    if (error) {
      error.textContent = "";
      error.hidden = true;
    }
  }

  function validEmail(value) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  }

  function validPhone(value) {
    return /^[0-9+().\-\s]{7,30}$/.test(value);
  }

  function validateForm(showErrors) {
    const errors = [];
    const method = methodValue();
    updateConditionalRequirements();

    clearFieldError(fields.name);
    clearFieldError(fields.email);
    clearFieldError(fields.phone);
    clearFieldError(fields.message);
    clearGroupError("contact-method", fields.contactMethod);
    clearFieldError(fields.category);
    clearFieldError(fields.acknowledgement);

    if (!fields.name.value.trim()) {
      errors.push({ field: fields.name, message: "Enter your preferred name." });
    }

    if (!method) {
      errors.push({ field: fields.contactMethod[0], group: "contact-method", controls: fields.contactMethod, message: "Choose a preferred contact method." });
    }

    if (method === "email") {
      if (!fields.email.value.trim()) {
        errors.push({ field: fields.email, message: "Enter an email address." });
      } else if (!validEmail(fields.email.value.trim())) {
        errors.push({ field: fields.email, message: "Enter an email address in the format name@example.com." });
      }
    }

    if (method === "phone") {
      if (!fields.phone.value.trim()) {
        errors.push({ field: fields.phone, message: "Enter a phone number." });
      } else if (!validPhone(fields.phone.value.trim())) {
        errors.push({ field: fields.phone, message: "Enter a phone number using numbers and common phone symbols." });
      }
    }

    if (!fields.category.value) {
      errors.push({ field: fields.category, message: "Choose a general inquiry category." });
    }

    if (fields.message.value.length > 500) {
      errors.push({ field: fields.message, message: "Reduce your general message to 500 characters or fewer." });
    }

    if (!fields.acknowledgement.checked) {
      errors.push({ field: fields.acknowledgement, message: "Confirm that you understand this is a non-sending pilot." });
    }

    if (showErrors) {
      errors.forEach(function (item) {
        if (item.group) {
          setGroupError(item.group, item.controls, item.message);
        } else {
          setFieldError(item.field, item.message);
        }
      });
    }

    return errors;
  }

  function updateErrorSummary(errors, moveFocus) {
    errorList.replaceChildren();

    errors.forEach(function (item) {
      const listItem = document.createElement("li");
      const link = document.createElement("a");
      link.href = "#" + item.field.id;
      link.textContent = item.message;
      listItem.appendChild(link);
      errorList.appendChild(listItem);
    });

    errorSummary.hidden = errors.length === 0;
    if (errors.length && moveFocus) errorSummary.focus();
  }

  function updateCharacterCount() {
    if (!message || !characterCount) return;
    characterCount.textContent = String(message.value.length) + " of 500 characters";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    submissionAttempted = true;

    const errors = validateForm(true);
    if (errors.length) {
      updateErrorSummary(errors, true);
      return;
    }

    errorSummary.hidden = true;
    form.reset();
    updateConditionalRequirements();
    updateCharacterCount();
    form.hidden = true;
    successPanel.hidden = false;
    successPanel.focus();
  });

  form.addEventListener("input", function () {
    updateCharacterCount();
    if (submissionAttempted) updateErrorSummary(validateForm(true), false);
  });

  form.addEventListener("change", function () {
    updateConditionalRequirements();
    if (submissionAttempted) updateErrorSummary(validateForm(true), false);
  });

  if (startAgainButton) {
    startAgainButton.addEventListener("click", function () {
      successPanel.hidden = true;
      form.hidden = false;
      submissionAttempted = false;
      errorSummary.hidden = true;
      fields.name.focus();
    });
  }

  if (previewSubmit) previewSubmit.disabled = false;
  updateConditionalRequirements();
  updateCharacterCount();
})();
