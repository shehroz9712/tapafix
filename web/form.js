/**
 * Field validation + OTP gate. OTP "123654" counts as verified (demo).
 */

const CORRECT_OTP = "123654";
const INPUT_DEBOUNCE_MS = 280;

/** @type {Record<string, (value: string, all: Record<string, string>) => string | null>} */
const validators = {
  fullName(value) {
    const v = value.trim();
    if (!v) return "Full name is required.";
    if (v.length < 2) return "Please enter at least 2 characters.";
    return null;
  },
  email(value) {
    const v = value.trim();
    if (!v) return "Email is required.";
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
    if (!ok) return "Enter a valid email address.";
    return null;
  },
  phone(value) {
    const v = value.trim().replace(/\s/g, "");
    if (!v) return "Phone number is required.";
    const digits = v.replace(/\D/g, "");
    if (digits.length < 10) return "Enter a valid phone number (at least 10 digits).";
    return null;
  },
  password(value) {
    if (!value) return "Password is required.";
    if (value.length < 8) return "Password must be at least 8 characters.";
    if (!/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
      return "Password must include at least one letter and one number.";
    }
    return null;
  },
  confirmPassword(value, all) {
    if (!value) return "Please confirm your password.";
    if (value !== all.password) return "Passwords do not match.";
    return null;
  },
  otp(value) {
    const v = value.trim();
    if (!v) return "Enter the verification code.";
    if (!/^\d{6}$/.test(v)) return "OTP must be exactly 6 digits.";
    return null;
  },
};

function getFormValues(form) {
  /** @type {Record<string, string>} */
  const out = {};
  for (const el of form.querySelectorAll("[data-field]")) {
    const key = el.getAttribute("data-field");
    if (key && el instanceof HTMLInputElement) out[key] = el.value;
  }
  return out;
}

function validateField(fieldName, allValues) {
  const fn = validators[fieldName];
  if (!fn) return null;
  const raw = allValues[fieldName] ?? "";
  return fn(raw, allValues);
}

function createDebounced(fn, ms) {
  let t = 0;
  return (...args) => {
    window.clearTimeout(t);
    t = window.setTimeout(() => fn(...args), ms);
  };
}

function setFieldError(fieldName, message, form) {
  const input = form.querySelector(`[data-field="${fieldName}"]`);
  const errEl = form.querySelector(`[data-error-for="${fieldName}"]`);
  if (!(input instanceof HTMLInputElement) || !(errEl instanceof HTMLElement)) return;
  errEl.textContent = message ?? "";
  const invalid = Boolean(message);
  input.setAttribute("aria-invalid", invalid ? "true" : "false");
}

/**
 * @param {HTMLFormElement} form
 * @param {{ touched: Set<string>, otpVerified: boolean }} state
 */
export function initSignupForm(form, state) {
  const otpFeedback = form.querySelector("#otp-feedback");
  const submitBtn = form.querySelector('button[type="submit"]');
  const verifyOtpBtn = form.querySelector("#verify-otp");
  const resultBanner = document.querySelector("#form-result");

  function updateSubmitEnabled() {
    if (!(submitBtn instanceof HTMLButtonElement)) return;
    submitBtn.disabled = !state.otpVerified;
  }

  function setOtpFeedback(kind, text) {
    if (!(otpFeedback instanceof HTMLElement)) return;
    otpFeedback.textContent = text;
    otpFeedback.classList.add("visible");
    otpFeedback.classList.remove("success", "error");
    if (kind === "success") otpFeedback.classList.add("success");
    else if (kind === "error") otpFeedback.classList.add("error");
    else otpFeedback.classList.remove("visible");
  }

  function clearOtpStatus() {
    state.otpVerified = false;
    if (!(otpFeedback instanceof HTMLElement)) return;
    otpFeedback.textContent = "";
    otpFeedback.classList.remove("visible", "success", "error");
    updateSubmitEnabled();
  }

  function verifyOtp() {
    const all = getFormValues(form);
    const formatErr = validateField("otp", all);
    if (formatErr) {
      state.otpVerified = false;
      setFieldError("otp", formatErr, form);
      setOtpFeedback("error", "Fix the code format before verifying.");
      updateSubmitEnabled();
      return;
    }
    const code = all.otp.trim();
    if (code === CORRECT_OTP) {
      state.otpVerified = true;
      setFieldError("otp", null, form);
      setOtpFeedback("success", "Code verified. You can submit the form.");
    } else {
      state.otpVerified = false;
      setOtpFeedback("error", "Incorrect code. Try again.");
    }
    updateSubmitEnabled();
  }

  function runFieldValidation(fieldName, showEmptyRequired = true) {
    const all = getFormValues(form);
    const msg = validateField(fieldName, all);
    if (!showEmptyRequired && !all[fieldName]?.trim() && fieldName !== "confirmPassword") {
      const onlyRequired =
        msg === "Full name is required." ||
        msg === "Email is required." ||
        msg === "Phone number is required." ||
        msg === "Password is required." ||
        msg === "Please confirm your password." ||
        msg === "Enter the verification code.";
      if (onlyRequired) {
        setFieldError(fieldName, null, form);
        return;
      }
    }
    setFieldError(fieldName, msg, form);
  }

  const debouncedValidate = createDebounced((fieldName) => {
    if (!state.touched.has(fieldName)) return;
    runFieldValidation(fieldName, false);
  }, INPUT_DEBOUNCE_MS);

  const passwordInput = form.querySelector('[data-field="password"]');
  if (passwordInput instanceof HTMLInputElement) {
    passwordInput.addEventListener("input", () => {
      if (state.touched.has("confirmPassword")) {
        debouncedValidate("confirmPassword");
      }
    });
  }

  for (const input of form.querySelectorAll("[data-field]")) {
    if (!(input instanceof HTMLInputElement)) continue;
    const fieldName = input.getAttribute("data-field");
    if (!fieldName) continue;

    input.addEventListener("blur", () => {
      state.touched.add(fieldName);
      runFieldValidation(fieldName, true);
      if (fieldName === "otp") {
        const all = getFormValues(form);
        if (state.touched.has("otp") && all.otp.trim() && /^\d{6}$/.test(all.otp.trim())) {
          verifyOtp();
        }
      }
    });

    input.addEventListener("input", () => {
      if (fieldName === "otp") clearOtpStatus();
      if (!state.touched.has(fieldName)) return;
      debouncedValidate(fieldName);
    });
  }

  if (verifyOtpBtn instanceof HTMLButtonElement) {
    verifyOtpBtn.addEventListener("click", () => {
      state.touched.add("otp");
      verifyOtp();
    });
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!(resultBanner instanceof HTMLElement)) return;

    for (const key of Object.keys(validators)) {
      state.touched.add(key);
    }
    const all = getFormValues(form);
    let hasError = false;
    for (const key of Object.keys(validators)) {
      const msg = validateField(key, all);
      setFieldError(key, msg, form);
      if (msg) hasError = true;
    }

    if (!state.otpVerified) {
      setOtpFeedback("error", "Verify your code before submitting.");
      hasError = true;
    }

    if (hasError) {
      resultBanner.classList.remove("visible", "ok");
      resultBanner.textContent = "";
      return;
    }

    resultBanner.textContent = "Form submitted successfully (demo).";
    resultBanner.classList.add("visible", "ok");
  });

  updateSubmitEnabled();
}
