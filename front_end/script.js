const DB = {
  accounts: 'srsi_accounts',
  legacyAccount: 'srsi_account',
  occ: 'srsi_occurrences',
  logs: 'srsi_logs',
  notices: 'srsi_notices',
  sector: 'srsi_sector'
};

const MAX_ACCOUNTS = 10;

const ACCOUNT_ROLES = [
  'Diretor',
  'Secretaria',
  ...Array(8).fill('Aluno')
];

function assignRoles(list) {
  return list.map((a, i) => ({
    ...a,
    role: ACCOUNT_ROLES[i] || 'Aluno'
  }));
}

function allAccounts() {
  let list = get(DB.accounts, null);

  if (!Array.isArray(list)) {
    const old = get(DB.legacyAccount, null);
    list = old ? [old] : [];
  }

  const updated = assignRoles(list);

  if (JSON.stringify(updated) !== JSON.stringify(list)) {
    set(DB.accounts, updated);
  }

  return updated;
}

function saveAccounts(list) {
  set(DB.accounts, assignRoles(list));
}

const get = (k, def = []) => {
  try {
    return JSON.parse(localStorage.getItem(k)) ?? def;
  } catch {
    return def;
  }
};

const set = (k, v) =>
  localStorage.setItem(k, JSON.stringify(v));

const esc = s =>
  String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }[c]));

const dateFmt = d =>
  new Date(d).toLocaleString('pt-BR');

function logAction(sector, action) {
  let logs = get(DB.logs);

  logs.unshift({
    date: new Date().toISOString(),
    sector,
    action
  });

  set(DB.logs, logs.slice(0, 300));
}

function account() {
  const email = (
    sessionStorage.getItem('srsi_logged_email') || ''
  ).toLowerCase();

  return allAccounts().find(
    a => a.email.toLowerCase() === email
  ) || null;
}

function requireLogin() {
  if (!account() || !sessionStorage.getItem('srsi_logged')) {
    location.href = 'index2.html';
    return false;
  }

  return true;
}

function logout() {
  sessionStorage.removeItem('srsi_logged');
  sessionStorage.removeItem('srsi_logged_email');
  location.href = 'index2.html';
}

function init() {
  const page = location.pathname.split('/').pop();

  if (page === 'index2.html' || page === '') {
    const f = document.getElementById('loginForm');

    const demoEmail = 'teste.escola@gmail.com';
    const demoPassword = 'Escola12345';

    const fill = document.getElementById('fillDemo');

    if (fill) {
      fill.addEventListener('click', () => {
        f.email.value = demoEmail;
        f.senha.value = demoPassword;

        document.getElementById('loginMsg').textContent =
          'Dados de demonstração preenchidos. Clique em Entrar no sistema.';
      });
    }

    if (f) {
      f.addEventListener('submit', e => {
        e.preventDefault();

        const msg = document.getElementById('loginMsg');

        const enteredEmail = f.email.value.trim().toLowerCase();
        const enteredPassword = f.senha.value;

        let list = allAccounts();

        let a = list.find(
          x => x.email.toLowerCase() === enteredEmail
        );

        if (
          !a &&
          enteredEmail === demoEmail &&
          enteredPassword === demoPassword
        ) {
          if (list.length >= MAX_ACCOUNTS) {
            msg.textContent =
              'O limite de 10 contas já foi atingido. Use uma das contas cadastradas.';
            return;
          }

          a = {
            school: 'Escola de Demonstração',
            email: demoEmail,
            owner: 'Usuário de teste',
            password: demoPassword,
            role: ACCOUNT_ROLES[list.length] || 'Aluno',
            status: 'aprovada',
            created: new Date().toISOString(),
            demo: true
          };

          list.push(a);
          saveAccounts(list);

          logAction(
            'Sistema',
            'Conta fictícia de demonstração criada'
          );
        }

        if (!a) {
          msg.textContent =
            'E-mail não cadastrado. Faça o cadastro institucional ou confira os dados.';
          return;
        }

        if (a.status !== 'aprovada') {
          msg.textContent =
            'Cadastro aguardando validação institucional. O acesso ainda não foi liberado.';
          return;
        }

        if (enteredPassword === a.password) {
          sessionStorage.setItem('srsi_logged', '1');
          sessionStorage.setItem('srsi_logged_email', a.email);

          logAction(
            'Acesso institucional',
            `Login realizado: ${a.email}`
          );

          location.href = 'painel.html';
        } else {
          msg.textContent =
            'Senha incorreta. Confira a senha e tente novamente.';
        }
      });
    }
  }

  if (page === 'registro.html') {
    const f = document.getElementById('registerForm');

    f?.addEventListener('submit', e => {
      e.preventDefault();

      const msg = document.getElementById('registerMsg');
      let list = allAccounts();

      if (list.length >= MAX_ACCOUNTS) {
        msg.textContent =
          'Limite atingido: o sistema permite no máximo 10 contas.';
        return;
      }

      const email = f.regEmail.value.trim().toLowerCase();

      if (list.some(a => a.email.toLowerCase() === email)) {
        msg.textContent =
          'Este e-mail já está cadastrado. Utilize outro e-mail.';
        return;
      }

      if (f.regPass.value !== f.regConfirm.value) {
        msg.textContent = 'As senhas não correspondem.';
        return;
      }

      if (f.regPass.value.length < 8) {
        msg.textContent =
          'A senha precisa ter pelo menos 8 caracteres.';
        return;
      }

      const assignedRole =
        ACCOUNT_ROLES[list.length] || 'Aluno';

      list.push({
        school: f.school.value.trim(),
        email,
        owner: f.owner.value.trim(),
        password: f.regPass.value,
        role: assignedRole,
        status: 'aprovada',
        created: new Date().toISOString()
      });

      saveAccounts(list);

      logAction(
        'Configuração inicial',
        `Conta institucional criada: ${email}`
      );

      sessionStorage.setItem('srsi_logged', '1');
      sessionStorage.setItem('srsi_logged_email', email);

      msg.textContent = 'Cadastro realizado! Redirecionando...';

      location.href = 'painel.html';
    });
  }

  if (page === 'recuperar.html') {
    document.getElementById('recoverForm')?.addEventListener('submit', e => {
      e.preventDefault();

      const a = allAccounts().find(
        x => x.email.toLowerCase() ===
        recoverEmail.value.trim().toLowerCase()
      );

      document.getElementById('recoverMsg').textContent =
        a
          ? 'Solicitação identificada. No sistema real, um link de redefinição será enviado ao e-mail institucional.'
          : 'Não foi encontrado cadastro com esse e-mail neste navegador.';
    });
  }

  if (page === 'painel.html') {
    if (!requireLogin()) return;

    const a = account();
    const o = get(DB.occ);

    schoolTitle.textContent =
      (a?.school || 'Instituição') + ' • Visão geral';

    total.textContent = o.length;

    pending.textContent =
      o.filter(x =>
        ['Recebida', 'Em análise'].includes(x.status)
      ).length;

    progress.textContent =
      o.filter(x => x.status === 'Em andamento').length;

    done.textContent =
      o.filter(x => x.status === 'Resolvida').length;

    const rows = get(DB.logs).slice(0, 12);

    activityRows.innerHTML =
      rows.map(x =>
        `<tr>
          <td>${dateFmt(x.date)}</td>
          <td>${esc(x.sector)}</td>
          <td>${esc(x.action)}</td>
        </tr>`
      ).join('') ||
      '<tr><td colspan="3">Nenhuma atividade registrada.</td></tr>';

    const ac = account();

    validationStatus.textContent =
      'Status do cadastro: ' + (ac?.status || 'não cadastrado');

    approveDemo.onclick = () => {
      if (!ac) return;

      ac.status = 'aprovada';

      saveAccounts(
        allAccounts().map(x =>
          x.email === ac.email ? ac : x
        )
      );

      validationStatus.textContent =
        'Status do cadastro: aprovada (simulação)';

      logAction(
        'Validação institucional',
        'Validação simulada para fins de demonstração'
      );
    };
  }

  if (page === 'ocorrencias.html') {
    if (!requireLogin()) return;

    renderOccurrenceTable();

    occurrenceForm.addEventListener('submit', e => {
      e.preventDefault();

      const files = [...attachments.files].map(f => f.name);

      const item = {
        id: 'OCO-' + Date.now().toString(36).toUpperCase(),
        location: location.value,
        category: category.value,
        title: title.value.trim(),
        description: description.value.trim(),
        files,
        created: new Date().toISOString(),
        priority: 'Não definida',
        status: 'Recebida',
        actions: [],
        history: []
      };

      let arr = get(DB.occ);

      arr.unshift(item);
      set(DB.occ, arr);

      logAction(
        'Secretaria',
        `Registrou e encaminhou a ocorrência ${item.id} (${item.location})`
      );

      occurrenceMsg.textContent =
        'Ocorrência registrada! Protocolo: ' + item.id;

      occurrenceForm.reset();

      renderOccurrenceTable();
    });
  }

  if (page === 'mapa.html') {
    if (!requireLogin()) return;

    renderMap();

    document.querySelectorAll('.room').forEach(b =>
      b.addEventListener('click', () => {
        document.querySelectorAll('.room').forEach(x =>
          x.classList.remove('selected')
        );

        b.classList.add('selected');
        showRoom(b.dataset.room);
      })
    );
  }

  if (page === 'gestao.html') {
    if (!requireLogin()) return;

    [
      'manageSearch',
      'priorityFilter',
      'statusFilter',
      'categoryFilter'
    ].forEach(id =>
      document.getElementById(id).addEventListener('input', renderManage)
    );

    renderManage();
  }

  if (page === 'relatorios.html') {
    if (!requireLogin()) return;

    applyReport.onclick = renderReport;
    exportCsv.onclick = exportReport;
