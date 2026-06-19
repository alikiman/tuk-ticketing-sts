/* ===========================================================
   TUK-STS DASHBOARD INTERACTIONS (CLEAN VERSION)
   =========================================================== */

document.addEventListener('DOMContentLoaded', function () {

  // =========================================================
  // 1. SIDEBAR TOGGLE (MOBILE)
  // =========================================================
  const shell = document.querySelector('.admin-shell');
  const toggleBtn = document.querySelector('[data-sidebar-toggle]');
  const backdrop = document.querySelector('[data-sidebar-close]');

  function closeSidebar() {
    shell?.classList.remove('sidebar-open');
    toggleBtn?.setAttribute('aria-expanded', 'false');
  }

  toggleBtn?.addEventListener('click', function () {
    const isOpen = shell.classList.toggle('sidebar-open');
    toggleBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  backdrop?.addEventListener('click', closeSidebar);


  // =========================================================
  // 2. ACTIVE SIDEBAR LINK (FIXED + CLEAN)
  // =========================================================
  const currentPath = window.location.pathname;

  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && currentPath.includes(href) && href !== '#') {
      link.classList.add('active');
    }
  });


  // =========================================================
  // 3. AUTO-HIDE ALERTS (SMOOTH FADE)
  // =========================================================
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease';
      alert.style.opacity = '0';

      setTimeout(() => alert.remove(), 400);
    }, 3000);
  });


  // =========================================================
  // 4. DELETE CONFIRMATION (GLOBAL SAFE GUARD)
  // =========================================================
  document.querySelectorAll('[data-confirm="delete"]').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const ok = confirm('Are you sure you want to delete this item? This action cannot be undone.');
      if (!ok) e.preventDefault();
    });
  });


  // =========================================================
  // 5. SIMPLE FORM VALIDATION (NO INLINE STYLING)
  // =========================================================
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function (e) {
      const requiredFields = form.querySelectorAll('[required]');
      let valid = true;

      requiredFields.forEach(field => {
        const value = field.value.trim();

        if (!value) {
          field.classList.add('input-error');
          valid = false;
        } else {
          field.classList.remove('input-error');
        }
      });

      if (!valid) {
        e.preventDefault();
        alert('Please fill all required fields.');
      }
    });
  });


  // =========================================================
  // 6. NOTIFICATION BADGE ENHANCEMENT
  // =========================================================
  const notif = document.querySelector('#notif-count');

  if (notif) {
    const count = parseInt(notif.textContent || '0');

    if (count > 0) {
      notif.classList.add('badge', 'badge-warning');
    }
  }


  // =========================================================
  // 7. SMOOTH SCROLL (INTERNAL LINKS)
  // =========================================================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));

      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });


  // =========================================================
  // 8. TABLE SEARCH (ADMIN USERS / TICKETS UX BOOST)
  // =========================================================
  document.querySelectorAll('[data-searchable-table]').forEach(table => {
    const input = document.querySelector(`[data-table-search="${table.id}"]`);

    if (!input) return;

    input.addEventListener('input', function () {
      const query = this.value.toLowerCase();

      table.querySelectorAll('tbody tr').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      });
    });
  });

});