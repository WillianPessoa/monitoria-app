document.addEventListener('DOMContentLoaded', function(){
  const toggle = document.querySelector('.menu-toggle');
  const links = document.querySelector('.nav-links');
  if(toggle && links){
    toggle.addEventListener('click', function(){
      links.classList.toggle('show');
      const expanded = links.classList.contains('show');
      toggle.setAttribute('aria-expanded', expanded);
    });

    document.addEventListener('click', function(e){
      if(!links.classList.contains('show')) return;
      if(e.target.closest('.nav-wrap') || e.target.closest('.menu-toggle')) return;
      links.classList.remove('show');
      toggle.setAttribute('aria-expanded', 'false');
    });

    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape'){
        links.classList.remove('show');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Theme toggle
  const themeBtn = document.querySelector('.theme-toggle');
  const root = document.documentElement;
  const saved = localStorage.getItem('monitoria:theme');
  if(saved) root.setAttribute('data-theme', saved);

  if(themeBtn){
    themeBtn.addEventListener('click', function(){
      const current = root.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('monitoria:theme', next);
      themeBtn.setAttribute('aria-pressed', next === 'dark' ? 'false' : 'true');
    });
  }
});
