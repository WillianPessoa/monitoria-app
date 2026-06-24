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

  const voteForms = document.querySelectorAll('form[data-max-select]');
  voteForms.forEach(function(form){
    const max = parseInt(form.getAttribute('data-max-select') || '2', 10);
    const inputName = form.querySelector('input[name="monitor_slots"]')
      ? 'monitor_slots'
      : 'opcao_ids';
    form.addEventListener('change', function(event){
      const target = event.target;
      if(!target || target.name !== inputName){
        return;
      }
      if(!target.checked){
        return;
      }
      const checked = Array.from(form.querySelectorAll('input[name="' + inputName + '"]:checked'));
      if(checked.length > max){
        const toUncheck = checked.find(function(item){
          return item !== target;
        });
        if(toUncheck){
          toUncheck.checked = false;
        }else{
          target.checked = false;
        }
      }
    });
  });

  const voteToggleForms = document.querySelectorAll('form[data-vote-toggle]');
  voteToggleForms.forEach(function(form){
    const hasVote = form.getAttribute('data-has-vote') === 'true';
    const submitBtn = form.querySelector('[data-vote-submit]');
    const checkboxes = form.querySelectorAll('input[name="opcao_ids"]');
    if(!submitBtn || !checkboxes.length){
      return;
    }

    if(hasVote){
      submitBtn.type = 'button';
      submitBtn.textContent = 'Alterar voto';
      checkboxes.forEach(function(cb){
        cb.disabled = true;
      });
    }

    submitBtn.addEventListener('click', function(event){
      if(!hasVote){
        return;
      }
      if(submitBtn.getAttribute('data-editing') === 'true'){
        return;
      }
      event.preventDefault();
      checkboxes.forEach(function(cb){
        cb.disabled = false;
      });
      submitBtn.type = 'submit';
      submitBtn.textContent = 'Salvar';
      submitBtn.setAttribute('data-editing', 'true');
    });
  });

  const profileConfig = document.querySelector('[data-profile-config]');
  if(profileConfig){
    const form = profileConfig.closest('form') || profileConfig;
    const cargaSelect = form.querySelector('[data-carga-horaria]');
    const modoLabel = form.querySelector('[data-modo-2h-label]');
    const modoSelect = form.querySelector('select[data-modo-2h]');
    const grid1h = form.querySelector('[data-grid-1h]');
    const grid2h = form.querySelector('[data-grid-2h]');
    const actions = form.querySelector('[data-profile-actions]');
    const cancelBtn = form.querySelector('[data-profile-cancel]');
    const saveBtn = form.querySelector('[data-profile-save]');

    if(cargaSelect && modoLabel && modoSelect && grid1h && grid2h && actions && cancelBtn && saveBtn){
      const initialCarga = cargaSelect.value;
      const initialModo = modoSelect.value;

      function setGridVisibility(mode){
        if(mode === '2h'){
          grid1h.hidden = true;
          grid2h.hidden = false;
          disableGrid(grid1h);
          enableGrid(grid2h);
        }else{
          grid1h.hidden = false;
          grid2h.hidden = true;
          enableGrid(grid1h);
          disableGrid(grid2h);
        }
      }

      function disableGrid(grid){
        grid.querySelectorAll('input[name="slots"]').forEach(function(cb){
          cb.disabled = true;
        });
      }

      function enableGrid(grid){
        grid.querySelectorAll('input[name="slots"]').forEach(function(cb){
          cb.disabled = false;
        });
      }

      function clearCheckboxes(){
        form.querySelectorAll('input[name="slots"]').forEach(function(cb){
          cb.checked = false;
        });
      }

      function restoreCheckboxes(){
        form.querySelectorAll('input[name="slots"]').forEach(function(cb){
          cb.checked = cb.getAttribute('data-initial') === 'true';
        });
      }

      function update2hOverlaps(){
        grid2h.querySelectorAll('input[name="slots"]').forEach(function(cb){
          cb.disabled = false;
        });
      }

      function toggleModeSelect(){
        const carga = cargaSelect.value;
        modoLabel.hidden = (carga !== '2');
      }

      function showActions(){
        actions.hidden = false;
        saveBtn.hidden = true;
      }

      function resetActions(){
        actions.hidden = true;
        saveBtn.hidden = false;
      }

      function applySelection(resetChecks){
        const carga = cargaSelect.value;
        const modo = modoSelect.value;
        toggleModeSelect();
        if(carga === '2' && modo === 'CONSECUTIVAS'){
          setGridVisibility('2h');
        }else{
          setGridVisibility('1h');
        }
        if(resetChecks){
          clearCheckboxes();
        }
        update2hOverlaps();
        showActions();
      }

      cargaSelect.addEventListener('change', function(){
        if(cargaSelect.value === '1'){
          modoSelect.value = 'CONSECUTIVAS';
        }
        applySelection(true);
      });

      modoSelect.addEventListener('change', function(){
        applySelection(true);
      });

      grid2h.addEventListener('change', function(){
        update2hOverlaps();
      });

      applySelection(false);

      cancelBtn.addEventListener('click', function(){
        cargaSelect.value = initialCarga;
        modoSelect.value = initialModo;
        toggleModeSelect();
        if(initialCarga === '2' && initialModo === 'CONSECUTIVAS'){
          setGridVisibility('2h');
        }else{
          setGridVisibility('1h');
        }
        restoreCheckboxes();
        update2hOverlaps();
        resetActions();
      });
    }
  }
});
