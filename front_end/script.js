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
          location.href = 'painel.html';
          return;
        }

        if (enteredPassword === a.password) {
          sessionStorage.setItem('srsi_logged', '1');
          sessionStorage.setItem('srsi_logged_email', a.email);

          logAction(
            'Acesso institucional',
            Login realizado: ${a.email}
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
        Conta institucional criada: ${email}
      );

      sessionStorage.setItem('srsi_logged', '1');
      sessionStorage.setItem('srsi_logged_email', email);

      msg.textContent = 'Cadastro realizado! Redirecionando...';

      location.href = 'painel.html';
    });
  }

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
        Registrou e encaminhou a ocorrência ${item.id} (${item.location})
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
    printReport.onclick = () => window.print();

    renderReport();
    renderHistory();
  }

  if (page === 'comunicados.html') {
    if (!requireLogin()) return;

    renderNotices();

    noticeForm.addEventListener('submit', e => {
      e.preventDefault();

      let n = get(DB.notices);

      n.unshift({
        id: Date.now(),
        title: noticeTitle.value.trim(),
        body: noticeBody.value.trim(),
        date: new Date().toISOString(),
        archived: false
      });

      set(DB.notices, n);

      logAction(
        'Gestão',
        'Publicou comunicado: ' + noticeTitle.value.trim()
      );

      noticeForm.reset();
      renderNotices();
    });
  }


function renderOccurrenceTable() {
  const rows = get(DB.occ);

  occurrenceRows.innerHTML =
    rows.map(x =>
      `<tr>
        <td>${esc(x.id)}</td>
        <td>${esc(x.location)}</td>
        <td>${esc(x.category)}</td>
        <td>${dateFmt(x.created)}</td>
        <td><span class="badge">${esc(x.status)}</span></td>
      </tr>`
    ).join('') ||
    '<tr><td colspan="5">Nenhuma ocorrência registrada.</td></tr>';
}

function renderMap() {
  const open = get(DB.occ).filter(
    x => x.status !== 'Resolvida' && x.status !== 'Arquivada'
  );

  document.querySelectorAll('.room').forEach(b => {
    b.classList.toggle(
      'has-open',
      open.some(x => x.location === b.dataset.room)
    );
  });
}

function showRoom(room) {
  const rows = get(DB.occ).filter(x => x.location === room);

  roomTitle.textContent = room;

  roomDetails.innerHTML =
    rows.length
      ? rows.map(x =>
          `<p>
            <b>${esc(x.id)}</b> — ${esc(x.title)}
            <span class="badge">${esc(x.status)}</span><br>
            <span class="muted">
              ${esc(x.category)} • ${dateFmt(x.created)}
            </span>
          </p>`
        ).join('')
      : 'Nenhuma ocorrência registrada para este ambiente.';
}

function renderManage() {
  const q = (manageSearch.value || '').toLowerCase();
  const p = priorityFilter.value;
  const s = statusFilter.value;
  const c = categoryFilter.value;

  const rows = get(DB.occ).filter(x =>
    (!q || (x.id + x.location + x.title).toLowerCase().includes(q)) &&
    (!p || x.priority === p) &&
    (!s || x.status === s) &&
    (!c || x.category === c)
  );

  manageCards.innerHTML =
    rows.map(x =>
      `<article class="card">
        <div class="actions" style="justify-content:space-between">
          <h2>${esc(x.title)}</h2>
          <span class="badge">${esc(x.id)}</span>
        </div>

        <p class="muted">
          ${esc(x.location)} • ${esc(x.category)} • Registrada em ${dateFmt(x.created)}
        </p>

        <p>${esc(x.description)}</p>

        <p>
          <b>Anexos:</b>
          ${x.files?.length ? x.files.map(esc).join(', ') : 'Nenhum'}
        </p>

        <div class="form-grid">
          <div>
            <label>Prioridade</label>
            <select id="p-${x.id}">
              <option ${x.priority === 'Não definida' ? 'selected' : ''}>Não definida</option>
              ${['Urgente', 'Alta', 'Média', 'Baixa'].map(v =>
                <option ${x.priority === v ? 'selected' : ''}>${v}</option>
              ).join('')}
            </select>
          </div>

          <div>
            <label>Situação</label>
            <select id="s-${x.id}">
              ${['Recebida', 'Em análise', 'Em andamento', 'Resolvida', 'Não resolvida', 'Arquivada'].map(v =>
                <option ${x.status === v ? 'selected' : ''}>${v}</option>
              ).join('')}
            </select>
          </div>

          <div class="full">
            <label>Providências / atualização</label>
            <textarea id="a-${x.id}" placeholder="Descreva as medidas tomadas ou a atualização diária"></textarea>
          </div>

          <div class="full">
            <label>Justificativa (obrigatória se marcar Não resolvida)</label>
            <textarea id="j-${x.id}" placeholder="Explique por que não foi possível resolver"></textarea>
          </div>
        </div>

        <div class="actions">
          <button onclick="saveOccurrence('${x.id}')">Salvar atualização</button>
          <button class="secondary small" onclick="showHistory('${x.id}')">Ver histórico</button>
        </div>

        <div id="hist-${x.id}" class="muted" style="margin-top:10px"></div>
      </article>`
    ).join('') ||
    '<div class="card empty">Nenhuma ocorrência encontrada.</div>';
}

function saveOccurrence(id) {
  let arr = get(DB.occ);
  let x = arr.find(v => v.id === id);

  if (!x) return;

  const p = document.getElementById('p-' + id).value;
  const s = document.getElementById('s-' + id).value;
  const a = document.getElementById('a-' + id).value.trim();
  const j = document.getElementById('j-' + id).value.trim();

  if (s === 'Não resolvida' && !j) {
    alert('Informe a justificativa para uma ocorrência não resolvida.');
    return;
  }

  if (!a && !j && p === x.priority && s === x.status) {
    alert('Faça alguma alteração antes de salvar.');
    return;
  }

  x.priority = p;
  x.status = s;

  if (a) {
    x.actions.push({
      date: new Date().toISOString(),
      text: a
    });
  }

  if (j) x.justification = j;

  x.history.push({
    date: new Date().toISOString(),
    text: Prioridade: ${p}; situação: ${s}${a ? '; providências: ' + a : ''}${j ? '; justificativa: ' + j : ''}
  });

  set(DB.occ, arr);

  logAction(
    'Gestão',
    Atualizou ${id}: ${s}, prioridade ${p}
  );

  renderManage();
}

function showHistory(id) {
  const x = get(DB.occ).find(v => v.id === id);
  const el = document.getElementById('hist-' + id);

  el.innerHTML =
    (x?.history || []).map(h =>
      <p>${dateFmt(h.date)} — ${esc(h.text)}</p>
    ).join('') ||
    'Sem atualizações ainda.';
}

function filteredReports() {
  let arr = get(DB.occ);

  let period = periodEl.value;
  let loc = reportLocation.value;
  let cat = reportCategory.value;
  let st = reportStatus.value;

  let now = new Date();

  return arr.filter(x => {
    let d = new Date(x.created);
    let age = (now - d) / 86400000;

    return (
      (period === 'all' ||
        (period === 'day' && d.toDateString() === now.toDateString()) ||
        (period === 'week' && age <= 7) ||
        (period === 'month' && age <= 30)) &&
      (!loc || x.location === loc) &&
      (!cat || x.category === cat) &&
      (!st || x.status === st)
    );
  });
}

const periodEl = document.getElementById('period');

function renderReport() {
  if (!document.getElementById('reportRows')) return;

  let a = filteredReports();

  reportTotal.textContent = a.length;

  reportOpen.textContent =
    a.filter(x =>
      x.status !== 'Resolvida' && x.status !== 'Arquivada'
    ).length;

  reportDone.textContent =
    a.filter(x => x.status === 'Resolvida').length;

  reportRows.innerHTML =
    a.map(x =>
      `<tr>
        <td>${esc(x.id)}</td>
        <td>${esc(x.location)}</td>
        <td>${esc(x.category)}</td>
        <td>${esc(x.priority)}</td>
        <td>${esc(x.status)}</td>
        <td>${dateFmt(x.created)}</td>
      </tr>`
    ).join('') ||
    '<tr><td colspan="6">Nenhum resultado para os filtros.</td></tr>';
}

function exportReport() {
  let a = filteredReports();

  let head = [
    'Protocolo',
    'Local',
    'Categoria',
    'Título',
    'Prioridade',
    'Situação',
    'Data',
    'Descrição'
  ];

  let lines = [
    head,
    ...a.map(x => [
      x.id,
      x.location,
      x.category,
      x.title,
      x.priority,
      x.status,
      dateFmt(x.created),
      x.description
    ])
  ];

  let csv =
    '\uFEFF' +
    lines.map(row =>
      row.map(v =>
        '"' + String(v ?? '').replace(/"/g, '""') + '"'
      ).join(';')
    ).join('\n');

  let blob = new Blob([csv], {
    type: 'text/csv;charset=utf-8;'
  });

  let url = URL.createObjectURL(blob);
  let link = document.createElement('a');

  link.href = url;
  link.download = 'relatorio-ocorrencias.csv';
  link.click();

  URL.revokeObjectURL(url);

  logAction('Gestão', 'Exportou relatório CSV');
}

function renderHistory() {
  historyRows.innerHTML =
    get(DB.logs).map(x =>
      `<tr>
        <td>${dateFmt(x.date)}</td>
        <td>${esc(x.sector)}</td>
        <td>${esc(x.action)}</td>
      </tr>`
    ).join('') ||
    '<tr><td colspan="3">Nenhuma atividade registrada.</td></tr>';
}

function renderNotices() {
  let n = get(DB.notices);

  noticeList.innerHTML =
    n.filter(x => !x.archived).map(x =>
      `<article class="card" style="margin-bottom:12px">
        <div class="actions" style="justify-content:space-between">
          <h3>${esc(x.title)}</h3>
          <span class="muted">${dateFmt(x.date)}</span>
        </div>

        <p>${esc(x.body)}</p>

        <div class="actions">
          <button class="secondary small" onclick="editNotice(${x.id})">Editar</button>
          <button class="warning small" onclick="archiveNotice(${x.id})">Arquivar</button>
        </div>
      </article>`
    ).join('') ||
    '<p class="empty">Nenhum comunicado publicado.</p>';

  archivedList.innerHTML =
    n.filter(x => x.archived).map(x =>
      `<article class="card" style="margin-bottom:10px">
        <h3>${esc(x.title)}</h3>
        <p>${esc(x.body)}</p>
        <button class="secondary small" onclick="restoreNotice(${x.id})">Restaurar</button>
      </article>`
    ).join('') ||
    '<p class="empty">Nenhum comunicado arquivado.</p>';
}

function editNotice(id) {
  let n = get(DB.notices);
  let x = n.find(v => v.id === id);

  if (!x) return;

  let t = prompt('Editar título:', x.title);
  if (t === null) return;

  let b = prompt('Editar mensagem:', x.body);
  if (b === null) return;

  x.title = t;
  x.body = b;

  set(DB.notices, n);

  logAction('Gestão', 'Editou comunicado: ' + t);

  renderNotices();
}

function archiveNotice(id) {
  let n = get(DB.notices);
  let x = n.find(v => v.id === id);

  if (x) {
    x.archived = true;

    set(DB.notices, n);

    logAction('Gestão', 'Arquivou comunicado: ' + x.title);

    renderNotices();
  }
}

function restoreNotice(id) {
  let n = get(DB.notices);
  let x = n.find(v => v.id === id);

  if (x) {
    x.archived = false;

    set(DB.notices, n);

    logAction('Gestão', 'Restaurou comunicado: ' + x.title);

    renderNotices();
  }
}

document.addEventListener('DOMContentLoaded', init);
