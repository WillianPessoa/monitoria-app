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

  const dialogTriggers = document.querySelectorAll('[data-dialog-open]');
  dialogTriggers.forEach(function(trigger){
    const targetId = trigger.getAttribute('data-dialog-open');
    const dialog = document.getElementById(targetId);
    if(!dialog) return;
    trigger.addEventListener('click', function(){
      if(typeof dialog.showModal === 'function'){
        dialog.showModal();
      }
    });
  });

  const dialogClose = document.querySelectorAll('[data-dialog-close]');
  dialogClose.forEach(function(button){
    const dialog = button.closest('dialog');
    if(!dialog) return;
    button.addEventListener('click', function(){
      dialog.close();
    });
  });

  const toggleAll = document.getElementById('toggle-all');
  if(toggleAll){
    toggleAll.addEventListener('change', function(){
      const checkboxes = document.querySelectorAll('input[name="alunos_ids"]');
      checkboxes.forEach(function(cb){
        cb.checked = toggleAll.checked;
      });
    });
  }

  const contatoTipo = document.querySelector('[data-contact-type]');
  const contatoInput = document.querySelector('[data-contact-input]');

  function formatPhone(value){
    const digits = value.replace(/\D/g, '').slice(0, 11);
    const ddd = digits.slice(0, 2);
    const part1 = digits.slice(2, 7);
    const part2 = digits.slice(7, 11);
    let formatted = '';
    if(ddd.length){
      formatted += '(' + ddd;
      if(ddd.length === 2){
        formatted += ') ';
      }
    }
    if(part1.length){
      formatted += part1;
    }
    if(part2.length){
      formatted += '-' + part2;
    }
    return formatted;
  }

  function applyContactMask(){
    if(!contatoTipo || !contatoInput){
      return;
    }
    if(contatoTipo.value === 'celular'){
      contatoInput.value = formatPhone(contatoInput.value);
    }
  }

  function deleteDigitAtCursor(input){
    const value = input.value;
    const cursor = input.selectionStart || 0;
    const digits = value.replace(/\D/g, '').split('');
    if(digits.length === 0){
      return;
    }

    let digitIndex = 0;
    for(let i = 0; i < value.length && i < cursor; i += 1){
      if(/\d/.test(value[i])){
        digitIndex += 1;
      }
    }

    if(digitIndex <= 0){
      digits.shift();
    }else{
      digits.splice(digitIndex - 1, 1);
    }

    input.value = formatPhone(digits.join(''));
    const nextCursor = Math.min(input.value.length, cursor - 1);
    input.setSelectionRange(nextCursor, nextCursor);
  }

  if(contatoTipo && contatoInput){
    contatoTipo.addEventListener('change', function(){
      contatoInput.value = '';
      contatoInput.placeholder = contatoTipo.value === 'celular'
        ? '(DDD) xxxxx-xxxx'
        : 'email@exemplo.com';
      applyContactMask();
    });

    contatoInput.addEventListener('input', function(){
      if(contatoTipo.value === 'celular'){
        contatoInput.value = formatPhone(contatoInput.value);
      }
    });

    contatoInput.addEventListener('keydown', function(event){
      if(contatoTipo.value !== 'celular'){
        return;
      }
      if(event.key === 'Backspace'){
        const cursor = contatoInput.selectionStart || 0;
        const value = contatoInput.value;
        if(cursor <= 4 || value[cursor - 1] === ')' || value[cursor - 1] === ' '){
          event.preventDefault();
          deleteDigitAtCursor(contatoInput);
        }
      }
    });

    applyContactMask();
  }

  const voteGrid = document.querySelector('.vote-grid');
  if(voteGrid){
    voteGrid.addEventListener('change', function(){
      const checked = voteGrid.querySelectorAll('input[name="opcao_ids"]:checked');
      if(checked.length > 2){
        const last = checked[checked.length - 1];
        last.checked = false;
      }
    });
  }

  const monitorVoteForm = document.querySelector('[data-monitor-vote-grid]');
  if(monitorVoteForm){
    monitorVoteForm.addEventListener('change', function(){
      const checked = monitorVoteForm.querySelectorAll('input[name="monitor_slots"]:checked');
      if(checked.length > 2){
        checked[checked.length - 1].checked = false;
      }
    });
  }
});
