let currentUser = null;

function getSessionUser() {
  try {
    const raw = sessionStorage.getItem("currentUserData");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function setSessionUser(user) {
  currentUser = user;
  sessionStorage.setItem("isAuthenticated", "true");
  sessionStorage.setItem("currentUser", user.email);
  sessionStorage.setItem("currentUserData", JSON.stringify(user));
}

function clearSessionUser() {
  currentUser = null;
  sessionStorage.clear();
}

function refreshAuthUi() {
  const user = getSessionUser();
  const guestLi = document.getElementById("guestLoginLi");
  const userLi = document.getElementById("userInfoLi");
  const logoutLi = document.getElementById("logoutLi");
  if (!guestLi) return;

  if (user) {
    guestLi.style.display = "none";
    if (userLi) userLi.style.display = "block";
    if (logoutLi) logoutLi.style.display = "block";
    const nameEl = document.getElementById("userNameDisplay2");
    const emailEl = document.getElementById("userEmailDisplay2");
    if (nameEl) nameEl.textContent = user.name;
    if (emailEl) emailEl.textContent = user.email;
  } else {
    guestLi.style.display = "block";
    if (userLi) userLi.style.display = "none";
    if (logoutLi) logoutLi.style.display = "none";
  }
}

async function signupUser(name, email, password) {
  const user = await apiPost("/api/auth/signup", { name, email, password });
  setSessionUser(user);
  return user;
}

async function loginUser(email, password) {
  const user = await apiPost("/api/auth/login", { email, password });
  setSessionUser(user);
  return user;
}

function logoutUser() {
  clearSessionUser();
  refreshAuthUi();
  showToast("Logged out");
  if (window.location.pathname.includes("shop")) {
    setTimeout(() => { window.location.href = "index.html"; }, 800);
  } else {
    location.reload();
  }
}

function checkAuth() {
  if (!sessionStorage.getItem("isAuthenticated")) {
    showToast("Please log in first");
    setTimeout(() => { window.location.href = "loginsignup.html"; }, 600);
    return false;
  }
  return true;
}

function bindAuthForms() {
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPassword").value;
      try {
        const user = await loginUser(email, password);
        showToast("Welcome back, " + user.name);
        loginForm.reset();
        setTimeout(() => { window.location.href = "index.html"; }, 800);
      } catch (err) {
        alert("Invalid email or password");
      }
    });
  }

  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("signupName").value.trim();
      const email = document.getElementById("signupEmail").value.trim();
      const password = document.getElementById("signupPassword").value;
      const confirm = document.getElementById("signupConfirmPassword").value;
      if (password !== confirm) {
        alert("Passwords do not match");
        return;
      }
      try {
        await signupUser(name, email, password);
        showToast("Account created successfully");
        signupForm.reset();
        setTimeout(() => { window.location.href = "index.html"; }, 800);
      } catch (err) {
        alert(err.message || "Signup failed");
      }
    });
  }
}

function showAuthTab(tab) {
  document.querySelectorAll(".authTabBtn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.tab === tab);
  });
  document.getElementById("loginFormWrap").style.display = tab === "login" ? "block" : "none";
  document.getElementById("signupFormWrap").style.display = tab === "signup" ? "block" : "none";
}

document.addEventListener("DOMContentLoaded", () => {
  currentUser = getSessionUser();
  refreshAuthUi();
  bindAuthForms();
});
