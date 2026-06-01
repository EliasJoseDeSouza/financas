// Sidebar
function openSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('overlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('active');
  document.body.style.overflow = '';
}

// Close sidebar on ESC
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeSidebar();
});

// Auto-hide flash messages
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// Animate KPI values on load
document.querySelectorAll('.kpi-value').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(10px)';
  el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
});
window.addEventListener('load', () => {
  document.querySelectorAll('.kpi-value').forEach((el, i) => {
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, 100 + i * 80);
  });
  document.querySelectorAll('.top-item-bar').forEach((el, i) => {
    const target = el.style.width;
    el.style.width = '0';
    setTimeout(() => { el.style.width = target; }, 400 + i * 60);
  });
});
