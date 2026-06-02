// ══════════════════════════════════════════════════════════════
// script.js — Controle Financeiro
// Responsável por: abrir/fechar a sidebar lateral
// ══════════════════════════════════════════════════════════════

// Guarda o estado atual da sidebar (aberta ou fechada)
let sidebarAberta = window.innerWidth > 700;

function toggleMenu() {

  sidebarAberta = !sidebarAberta;

  const sidebar   = document.getElementById('sidebar');
  const container = document.querySelector('.container');
  const topbar    = document.getElementById('topbar');

  if (window.innerWidth > 700) {
    // ── Desktop: empurra o conteúdo para o lado ──
    if (sidebarAberta) {
      sidebar.classList.remove('hidden');
      container.classList.remove('full');
      topbar.classList.remove('full');
    } else {
      sidebar.classList.add('hidden');
      container.classList.add('full');
      topbar.classList.add('full');
    }
  } else {
    // ── Celular: sidebar sobrepõe o conteúdo ──
    sidebar.classList.toggle('open', sidebarAberta);
  }

}

// Fecha sidebar ao clicar fora (celular)
document.addEventListener('click', function(e) {
  if (window.innerWidth > 700) return;

  const sidebar  = document.getElementById('sidebar');
  const menuBtn  = document.getElementById('menu-btn');

  const clicouFora = !sidebar.contains(e.target) && !menuBtn.contains(e.target);

  if (clicouFora && sidebarAberta) {
    sidebarAberta = false;
    sidebar.classList.remove('open');
  }
});
