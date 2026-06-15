const navItems = [
  { href: "index.html", label: "Home", icon: "fa-home", id: "home" },
  { href: "about.html", label: "About", icon: "fa-info-circle", id: "about" },
  { href: "shop.html", label: "Shop", icon: "fa-shopping-bag", id: "shop" },
  { href: "task.html", label: "Tasks", icon: "fa-tasks", id: "task" },
];

function toggleSidebar() {
  document.getElementById("sidebarPanel")?.classList.toggle("active");
  document.getElementById("sidebarOverlay")?.classList.toggle("active");
}

function closeSidebar() {
  document.getElementById("sidebarPanel")?.classList.remove("active");
  document.getElementById("sidebarOverlay")?.classList.remove("active");
}

function buildNavLinks(activePage, inSidebar) {
  return navItems.map(item => {
    const active = item.id === activePage ? " active" : "";
    if (inSidebar) {
      return `<button class="btn btn-primary w-100 rounded-pill" onclick="location.href='${item.href}'">
        <i class="fas ${item.icon} me-2"></i>${item.label}
      </button>`;
    }
    return `<a class="navLink${active}" href="${item.href}" title="${item.label}">
      <i class="fas ${item.icon}"></i><span class="ms-1">${item.label}</span>
    </a>`;
  }).join("");
}

function buildUserDropdown(showCart) {
  const cartHtml = showCart ? `
    <li id="cartItemsDropdown">
      <span class="dropdown-item-text px-4 py-2 text-muted small">Cart is empty</span>
    </li>
    <li><hr class="dropdown-divider"></li>
    <li>
      <button class="dropdown-item fw-bold text-primary" onclick="openCartPage()">
        <i class="fas fa-shopping-cart me-2"></i>View Cart
      </button>
    </li>` : "";

  const logoutHtml = `<li id="logoutLi" style="display:none;">
    <hr class="dropdown-divider">
    <button class="dropdown-item fw-bold text-danger" onclick="logoutUser()">
      <i class="fas fa-sign-out-alt me-2"></i>Logout
    </button>
  </li>`;

  return `
    <div class="dropdown">
      <button class="btn btn-light dropdown-toggle d-flex align-items-center gap-2" type="button"
              id="userDropdown" data-bs-toggle="dropdown">
        <i class="fas fa-user-circle fs-5"></i>
      </button>
      <ul class="dropdown-menu dropdown-menu-end userDropdownMenu">
        <li id="guestLoginLi">
          <a class="dropdown-item px-4 py-3 border-bottom userHeaderBtn" href="loginsignup.html">
            <strong id="userNameDisplay">Guest</strong><br>
            <small id="userEmailDisplay" class="opacity-75">Click to login</small>
          </a>
        </li>
        <li id="userInfoLi" style="display:none;">
          <div class="dropdown-item-text px-4 py-3 border-bottom userHeaderBtn">
            <strong id="userNameDisplay2">User</strong><br>
            <small id="userEmailDisplay2" class="opacity-75">Logged in</small>
          </div>
        </li>
        ${showCart ? "<li><hr class=\"dropdown-divider\"></li>" + cartHtml : ""}
        ${logoutHtml}
      </ul>
    </div>`;
}

function initNav(activePage, options = {}) {
  const root = document.getElementById("navRoot");
  if (!root) return;

  const showCart = options.showCart === true;
  const brand = "SmartCampus";
  const cartCanvas = document.getElementById("cartCanvas");
  const cartBtn = showCart && cartCanvas ? `
    <button class="btn btn-light btn-sm me-1" data-bs-toggle="offcanvas" data-bs-target="#cartCanvas" type="button">
      <i class="fas fa-shopping-cart"></i>
      <span class="cartBadge js-cart-count" id="cartCount">0</span>
    </button>` : "";

  root.innerHTML = `
    <nav class="navbarSite">
      <div class="navbarInner">
        <button class="btn btn-light btn-sm" onclick="toggleSidebar()" aria-label="Menu">
          <i class="fas fa-bars"></i>
        </button>
        <a class="navbarBrand fw-bold ms-1" href="index.html">${brand}</a>
        <div class="navbarLinks ms-2 d-none d-md-flex">${buildNavLinks(activePage, false)}</div>
        <div class="navbarSpacer"></div>
        ${cartBtn}
        ${options.showUser !== false ? buildUserDropdown(showCart) : ""}
      </div>
    </nav>
    <div class="sidebarOverlay" id="sidebarOverlay" onclick="closeSidebar()"></div>
    <div class="sidebarPanel" id="sidebarPanel">
      <h5>Menu <span class="sidebarClose" onclick="closeSidebar()">&times;</span></h5>
      <hr>
      <div class="d-grid gap-2 mt-3">${buildNavLinks(activePage, true)}</div>
    </div>`;

  if (typeof refreshAuthUi === "function") refreshAuthUi();
  if (showCart && typeof updateCartDropdown === "function") updateCartDropdown();
}

function openCartPage() {
  if (typeof checkAuth === "function" && !checkAuth()) return;
  window.location.href = "shop.html";
}

function updateCartDropdown() {
  const cart = JSON.parse(localStorage.getItem("cart") || "[]");
  const cartCount = document.getElementById("cartCount");
  const cartItemsDropdown = document.getElementById("cartItemsDropdown");
  if (cartCount) cartCount.textContent = cart.length;
  document.querySelectorAll(".js-cart-count").forEach(el => { el.textContent = cart.length; });
  if (!cartItemsDropdown) return;
  if (cart.length === 0) {
    cartItemsDropdown.innerHTML = '<span class="dropdown-item-text px-4 py-2 text-muted small">Cart is empty</span>';
    return;
  }
  const itemsHtml = cart.slice(0, 3).map(item => `
    <div class="dropdown-item-text px-4 py-2">
      <strong>${item.name}</strong><br>
      <small class="text-muted">Qty: ${item.qty}</small>
    </div>`).join("");
  const moreHtml = cart.length > 3
    ? `<div class="dropdown-item-text px-4 py-2 text-muted small">+ ${cart.length - 3} more</div>` : "";
  cartItemsDropdown.innerHTML = itemsHtml + moreHtml;
}

document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("navRoot");
  if (root) {
    initNav(root.dataset.page || "home", {
      showCart: root.dataset.cart === "true",
      showUser: root.dataset.user !== "false",
    });
  }
});
