(function () {
  "use strict";

  const form = document.querySelector("[data-support-assessment]");
  if (!form) return;

  const errorSummary = document.querySelector("[data-assessment-error-summary]");
  const errorList = document.querySelector("[data-assessment-error-list]");
  const reviewPanel = document.querySelector("[data-assessment-review-panel]");
  const reviewHeading = document.querySelector("[data-assessment-review-heading]");
  const reviewContent = document.querySelector("[data-assessment-review-content]");
  const editButton = document.querySelector("[data-assessment-edit]");
  const startOverButton = document.querySelector("[data-assessment-start-over]");
  const resetPanel = document.querySelector("[data-assessment-reset-panel]");
  const clearButton = document.querySelector("[data-assessment-clear]");
  const keepButton = document.querySelector("[data-assessment-keep]");
  const reviewButton = form.querySelector("[data-assessment-review]");
  const formHeading = document.querySelector("#assessment-form-title");
  const note = form.querySelector("#assessment-note");
  const noteCount = document.querySelector("[data-assessment-note-count]");
  const limitedFields = [
    {
      field: form.querySelector("#assessment-name"),
      maximum: 80,
      message: "Reduce your preferred name to 80 characters or fewer."
    },
    {
      field: form.querySelector("#assessment-municipality"),
      maximum: 80,
      message: "Reduce your city or municipality to 80 characters or fewer."
    },
    {
      field: form.querySelector("#assessment-language"),
      maximum: 60,
      message: "Reduce your language preference to 60 characters or fewer."
    },
    {
      field: note,
      maximum: 300,
      message: "Reduce your general note to 300 characters or fewer."
    }
  ];
  let reviewAttempted = false;

  const groups = {
    assessor: Array.from(form.querySelectorAll('input[name="assessor"]')),
    topics: Array.from(form.querySelectorAll('input[name="topics"]')),
    acknowledgements: Array.from(form.querySelectorAll('input[name="acknowledgements"]'))
  };

  function selected(controls) {
    return controls.filter(function (control) { return control.checked; });
  }

  function labelFor(control) {
    return control.dataset.summaryLabel || control.value;
  }

  function setGroupError(name, controls, message) {
    const error = document.getElementById(name + "-error");
    controls.forEach(function (control) {
      control.setAttribute("aria-invalid", "true");
    });
    if (error) {
      error.textContent = message;
      error.hidden = false;
    }
  }

  function clearGroupError(name, controls) {
    const error = document.getElementById(name + "-error");
    controls.forEach(function (control) {
      control.removeAttribute("aria-invalid");
    });
    if (error) {
      error.textContent = "";
      error.hidden = true;
    }
  }

  function setFieldError(field, message) {
    const error = document.getElementById(field.id + "-error");
    field.setAttribute("aria-invalid", "true");
    if (error) {
      error.textContent = message;
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

  function validate(showErrors) {
    const errors = [];
    clearGroupError("assessor", groups.assessor);
    clearGroupError("topics", groups.topics);
    clearGroupError("acknowledgements", groups.acknowledgements);
    limitedFields.forEach(function (item) {
      clearFieldError(item.field);
    });

    if (!selected(groups.assessor).length) {
      errors.push({
        field: groups.assessor[0],
        group: "assessor",
        controls: groups.assessor,
        message: "Choose who is completing this assessment."
      });
    }

    if (!selected(groups.topics).length) {
      errors.push({
        field: groups.topics[0],
        group: "topics",
        controls: groups.topics,
        message: "Choose at least one topic to discuss."
      });
    }

    limitedFields.forEach(function (item) {
      if (item.field.value.length > item.maximum) {
        errors.push({
          field: item.field,
          message: item.message
        });
      }
    });

    if (selected(groups.acknowledgements).length !== groups.acknowledgements.length) {
      errors.push({
        field: groups.acknowledgements.find(function (control) { return !control.checked; }),
        group: "acknowledgements",
        controls: groups.acknowledgements.filter(function (control) { return !control.checked; }),
        message: "Confirm both statements before reviewing your topics."
      });
    }

    if (showErrors) {
      errors.forEach(function (item) {
        if (item.group) setGroupError(item.group, item.controls, item.message);
        else setFieldError(item.field, item.message);
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

  function addSummaryGroup(title, values) {
    if (!values.length) return;
    const section = document.createElement("section");
    const heading = document.createElement("h3");
    const list = document.createElement("ul");
    heading.textContent = title;
    values.forEach(function (value) {
      const item = document.createElement("li");
      item.textContent = value;
      list.appendChild(item);
    });
    section.append(heading, list);
    reviewContent.appendChild(section);
  }

  function valueOf(name) {
    const control = form.querySelector('[name="' + name + '"]:checked');
    return control ? labelFor(control) : "";
  }

  function valuesOf(name) {
    return Array.from(form.querySelectorAll('[name="' + name + '"]:checked')).map(labelFor);
  }

  function textValue(id) {
    const control = document.getElementById(id);
    return control && control.value.trim() ? control.value.trim() : "";
  }

  function buildSummary() {
    reviewContent.replaceChildren();
    addSummaryGroup("About this conversation", [
      valueOf("assessor"),
      textValue("assessment-name") ? "Preferred name: " + textValue("assessment-name") : "",
      valueOf("follow-up") ? "Follow-up preference: " + valueOf("follow-up") : ""
    ].filter(Boolean));
    addSummaryGroup("Area", textValue("assessment-municipality") ? [textValue("assessment-municipality")] : []);
    addSummaryGroup("Times to discuss", valuesOf("timing"));
    addSummaryGroup("Frequency to discuss", valueOf("frequency") ? [valueOf("frequency")] : []);
    addSummaryGroup("Support topics", valuesOf("topics"));
    addSummaryGroup("Communication and accessibility preferences", valuesOf("communication").concat(
      textValue("assessment-language") ? ["Language preference: " + textValue("assessment-language")] : []
    ));
    addSummaryGroup("General note", textValue("assessment-note") ? [textValue("assessment-note")] : []);
  }

  function updateNoteCount() {
    noteCount.textContent = String(note.value.length) + " of 300 characters";
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    reviewAttempted = true;
    const errors = validate(true);
    updateErrorSummary(errors, Boolean(errors.length));
    if (errors.length) return;

    buildSummary();
    form.hidden = true;
    resetPanel.hidden = true;
    reviewPanel.hidden = false;
    reviewHeading.focus();
  });

  form.addEventListener("input", function () {
    updateNoteCount();
    if (reviewAttempted) updateErrorSummary(validate(true), false);
  });

  form.addEventListener("change", function () {
    if (reviewAttempted) updateErrorSummary(validate(true), false);
  });

  editButton.addEventListener("click", function () {
    reviewPanel.hidden = true;
    resetPanel.hidden = true;
    form.hidden = false;
    formHeading.focus();
  });

  startOverButton.addEventListener("click", function () {
    resetPanel.hidden = false;
    resetPanel.focus();
  });

  keepButton.addEventListener("click", function () {
    resetPanel.hidden = true;
    startOverButton.focus();
  });

  clearButton.addEventListener("click", function () {
    form.reset();
    reviewContent.replaceChildren();
    reviewAttempted = false;
    updateErrorSummary([], false);
    updateNoteCount();
    resetPanel.hidden = true;
    reviewPanel.hidden = true;
    form.hidden = false;
    formHeading.focus();
  });

  reviewButton.disabled = false;
  updateNoteCount();
})();
