
const DB_KEY = "sistemaSolicitacoes_v1";
const SESSION_KEY = "sistemaSessao_v1";
const demoAccount = {email:"secretaria@escola.com",password:"Escola123!",school:"Escola Exemplo",responsavel:"Administrador",approved:true};

function db(){
  let data=JSON.parse(localStorage.getItem(DB_KEY)||"null");
  if(!data){
    data={account:demoAccount,occurrences:[],messages:[],logs:[]};
    localStorage.setItem(DB_KEY,JSON.stringify(data));
  }
  return data;
}
function save(data){localStorage.setItem(DB_KEY,JSON.stringify(data));}
function currentSession(){return JSON.parse(sessionStorage.getItem(SESSION_KEY)||"null");}
function logAction(action){
  const s=currentSession(); const data=db();
  data.logs.unshift({action,sector:s?.sector||"Sistema",date:new Date().toLocaleString("pt-BR")});
  save(data);
}
function requireLogin(){
  if(!currentSession()){location.href="index2.html";return false;}
  return true;
}
function escapeHTML(value){
  return String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function statusClass(s){return String(s||"").toLowerCase().replaceAll(" ","-");}
function nav(active){
 const links=[["painel.html","Painel"],["mapa.html","Mapa da escola"],["registrar-ocorrencia.html","Registrar ocorrência"],["ocorrencias.html","Ocorrências"],["gestao.html","Gestão"],["relatorios.html","Relatórios"],["comunicados.html","Comunicados"],["historico.html","Histórico"],["atividades.html","Atividades"]];
 return `<header class="top"><div class="brand">Sistema de Registro de Solicitações</div><div class="top-right"><span id="userInfo"></span><button class="secondary small no-print" onclick="logout()">Sair</button></div></header><div class="layout"><nav class="sidebar"><div class="section-label">Menu principal</div>${links.map(([url,label])=>`<a class="${active===url?'active':''}" href="${url}">${label}</a>`).join("")}</nav>`;
}
function finishShell(active,title,subtitle,body){
 document.body.innerHTML=nav(active)+`<main class="content"><h1>${title}</h1><p class="subtitle">${subtitle}</p>${body}</main></div>`;
 const s=currentSession(); document.getElementById("userInfo").textContent=s?`${s.email} • ${s.sector}`:"";
}
function logout(){sessionStorage.removeItem(SESSION_KEY);location.href="index2.html";}
function initLogin(){
 const form=document.getElementById("loginForm");
 if(!form)return;
 form.addEventListener("submit",e=>{
   e.preventDefault();const email=document.getElementById("email").value.trim().toLowerCase();
   const password=document.getElementById("senha").value;const sector=document.getElementById("setor").value;
   const account=db().account;
   if(!account||email!==account.email.toLowerCase()||password!==account.password){
     document.getElementById("loginMsg").textContent="E-mail ou senha incorretos.";return;
   }
   if(!account.approved){document.getElementById("loginMsg").textContent="Cadastro aguardando validação institucional.";return;}
   sessionStorage.setItem(SESSION_KEY,JSON.stringify({email,sector}));
   logAction("Acesso ao sistema");location.href="painel.html";
 });
 const recovery=document.getElementById("recovery");
 if(recovery)recovery.addEventListener("click",e=>{e.preventDefault();const email=prompt("Informe o e-mail institucional cadastrado:");if(email)alert("Se o e-mail estiver cadastrado, a instituição deverá enviar as instruções de redefinição. A recuperação real exige integração com servidor.");});
}
function initRegister(){
 const form=document.getElementById("cadastroForm");if(!form)return;
 form.addEventListener("submit",e=>{
  e.preventDefault();
  const school=document.getElementById("escola").value.trim(),email=document.getElementById("email").value.trim(),responsavel=document.getElementById("responsavel").value.trim(),password=document.getElementById("senha").value,confirm=document.getElementById("confirmar").value;
  const msg=document.getElementById("registerMsg");
  if(password.length<8){msg.textContent="A senha deve ter pelo menos 8 caracteres.";return;}
  if(password!==confirm){msg.textContent="As senhas não correspondem.";return;}
  const data=db();if(data.account&&data.account.email!==demoAccount.email){msg.textContent="Já existe uma conta institucional cadastrada neste protótipo.";return;}
  data.pendingAccount={school,email,responsavel,password,approved:false,status:"Aguardando validação institucional"};
  save(data);msg.textContent="Solicitação registrada como pendente de validação institucional. A liberação real depende da confirmação da escola por um administrador.";
  form.reset();
 });
}
function makeId(){return "OC-"+new Date().getFullYear()+"-"+Math.random().toString(36).slice(2,8).toUpperCase();}
function initDashboard(){
 const total=document.getElementById("totalStat");if(!total)return;
 const items=db().occurrences;
 total.textContent=items.length;
 document.getElementById("pendingStat").textContent=items.filter(x=>x.status==="Pendente").length;
 document.getElementById("progressStat").textContent=items.filter(x=>x.status==="Em andamento").length;
 document.getElementById("resolvedStat").textContent=items.filter(x=>x.status==="Resolvida").length;
}
function initOccurrenceForm(){
 const form=document.getElementById("occurrenceForm");if(!form)return;
 const chosen=localStorage.getItem("selectedPlace");if(chosen)document.getElementById("local").value=chosen;
 form.addEventListener("submit",e=>{
  e.preventDefault();const data=db();const item={
   id:makeId(),title:document.getElementById("titulo").value.trim(),local:document.getElementById("local").value,
   category:document.getElementById("categoria").value,description:document.getElementById("descricao").value.trim(),
   priority:"Não definida",status:"Pendente",measures:"",justification:"",createdAt:new Date().toISOString(),
   createdLabel:new Date().toLocaleString("pt-BR"),forwarded:false,attachments:[...(document.getElementById("anexos").files||[])].map(f=>f.name),history:[]
  };
  item.history.push({date:item.createdLabel,sector:currentSession()?.sector||"Secretaria",action:"Ocorrência registrada"});
  data.occurrences.unshift(item);data.logs.unshift({action:`Registrou ${item.id}`,sector:currentSession()?.sector||"Secretaria",date:item.createdLabel});save(data);
  localStorage.removeItem("selectedPlace");document.getElementById("occurrenceMsg").textContent=`Ocorrência ${item.id} registrada com sucesso.`;form.reset();
 });
}
function renderOccurrences(items){
 if(!items.length)return `<div class="empty">Nenhuma ocorrência encontrada.</div>`;
 return `<div class="table-wrap"><table><thead><tr><th>Protocolo</th><th>Problema</th><th>Local</th><th>Categoria</th><th>Prioridade</th><th>Situação</th><th>Data</th></tr></thead><tbody>${items.map(o=>`<tr><td><strong>${escapeHTML(o.id)}</strong></td><td>${escapeHTML(o.title)}</td><td>${escapeHTML(o.local)}</td><td>${escapeHTML(o.category)}</td><td>${escapeHTML(o.priority)}</td><td><span class="badge ${statusClass(o.status)}">${escapeHTML(o.status)}</span></td><td>${escapeHTML(o.createdLabel)}</td></tr>`).join("")}</tbody></table></div>`;
}
function initOccurrences(){
 const target=document.getElementById("occurrenceList");if(!target)return;
 const filters=["filterLocal","filterCategory","filterDate","filterPriority","filterStatus"];
 function draw(){const d=db();let list=d.occurrences;
  const v=id=>document.getElementById(id).value;
  if(v("filterLocal"))list=list.filter(o=>o.local===v("filterLocal"));
  if(v("filterCategory"))list=list.filter(o=>o.category===v("filterCategory"));
  if(v("filterDate"))list=list.filter(o=>o.createdAt.slice(0,10)===v("filterDate"));
  if(v("filterPriority"))list=list.filter(o=>o.priority===v("filterPriority"));
  if(v("filterStatus"))list=list.filter(o=>o.status===v("filterStatus"));
  target.innerHTML=renderOccurrences(list);
 }
 filters.forEach(id=>document.getElementById(id)?.addEventListener("change",draw));draw();
}
function initManagement(){
 const target=document.getElementById("managementList");if(!target)return;
 function draw(){const list=db().occurrences;target.innerHTML=list.length?list.map(o=>`<article class="card" style="margin-bottom:14px"><div style="display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><div><strong>${escapeHTML(o.id)} — ${escapeHTML(o.title)}</strong><p class="muted">${escapeHTML(o.local)} • ${escapeHTML(o.category)} • ${escapeHTML(o.createdLabel)}</p></div><span class="badge ${statusClass(o.status)}">${escapeHTML(o.status)}</span></div><div class="form-grid" style="margin-top:14px"><div class="field"><label>Prioridade</label><select id="priority-${o.id}"><option ${o.priority==="Não definida"?"selected":""}>Não definida</option><option ${o.priority==="Baixa"?"selected":""}>Baixa</option><option ${o.priority==="Média"?"selected":""}>Média</option><option ${o.priority==="Alta"?"selected":""}>Alta</option><option ${o.priority==="Urgente"?"selected":""}>Urgente</option></select></div><div class="field"><label>Situação</label><select id="status-${o.id}">${["Pendente","Em andamento","Resolvida","Não resolvida"].map(s=>`<option ${o.status===s?"selected":""}>${s}</option>`).join("")}</select></div></div><div class="field"><label>Providências tomadas</label><textarea id="measures-${o.id}" placeholder="Descreva as medidas...">${escapeHTML(o.measures)}</textarea></div><div class="field"><label>Justificativa (quando não for possível resolver)</label><textarea id="justification-${o.id}" placeholder="Informe a justificativa...">${escapeHTML(o.justification)}</textarea></div><button class="small" onclick="saveManagement('${o.id}')">Salvar atualização</button><button class="small secondary" onclick="forwardOccurrence('${o.id}')">${o.forwarded?"Encaminhada à gestão":"Encaminhar à gestão"}</button></article>`).join(""):`<div class="empty">Ainda não existem ocorrências para gerenciar.</div>`;}
 draw();window.saveManagement=id=>{const d=db(),o=d.occurrences.find(x=>x.id===id);if(!o)return;o.priority=document.getElementById("priority-"+id).value;o.status=document.getElementById("status-"+id).value;o.measures=document.getElementById("measures-"+id).value;o.justification=document.getElementById("justification-"+id).value;const date=new Date().toLocaleString("pt-BR");o.history.unshift({date,sector:currentSession()?.sector||"Gestão",action:`Atualizou prioridade/situação para ${o.priority}/${o.status}`});d.logs.unshift({action:`Atualizou ${id}`,sector:currentSession()?.sector||"Gestão",date});save(d);draw();alert("Atualização registrada.");};
 window.forwardOccurrence=id=>{const d=db(),o=d.occurrences.find(x=>x.id===id);if(!o)return;o.forwarded=true;const date=new Date().toLocaleString("pt-BR");o.history.unshift({date,sector:currentSession()?.sector||"Secretaria",action:"Encaminhou ocorrência à gestão"});d.logs.unshift({action:`Encaminhou ${id} à gestão`,sector:currentSession()?.sector||"Secretaria",date});save(d);draw();};
}
function initMap(){
 const map=document.getElementById("schoolMap");if(!map)return;
 const places=["Salas de aula","Banheiros","Biblioteca","Laboratórios","Pátio","Quadra","Secretaria","Refeitório","Corredores"];
 const data=db();map.innerHTML=places.map((p,i)=>{const open=data.occurrences.filter(o=>o.local===p&&o.status!=="Resolvida").length;return `<button class="place ${open?"has-open":""}" onclick="selectPlace('${p}')"><span>${["🏫","🚻","📚","🧪","🌳","🏀","🏢","🍽️","🚶"][i]}</span><strong>${p}</strong><small>${open?open+" ocorrência(s) pendente(s)":"Sem pendências registradas"}</small></button>`}).join("");
 window.selectPlace=p=>{localStorage.setItem("selectedPlace",p);location.href="registrar-ocorrencia.html";};
}
function initReports(){
 const box=document.getElementById("reportSummary");if(!box)return;
 function draw(){const all=db().occurrences;const period=document.getElementById("period").value;const now=new Date();let start=new Date(now);
  if(period==="Diário")start.setHours(0,0,0,0);else if(period==="Semanal")start.setDate(now.getDate()-7);else start.setDate(1);
  const list=all.filter(o=>new Date(o.createdAt)>=start);box.innerHTML=`<div class="grid"><div class="card"><div class="stat">${list.length}</div><div class="stat-label">Ocorrências no período</div></div><div class="card"><div class="stat">${list.filter(o=>o.status==="Pendente").length}</div><div class="stat-label">Pendentes</div></div><div class="card"><div class="stat">${list.filter(o=>o.status==="Em andamento").length}</div><div class="stat-label">Em andamento</div></div><div class="card"><div class="stat">${list.filter(o=>o.status==="Resolvida").length}</div><div class="stat-label">Resolvidas</div></div></div>${renderOccurrences(list)}`;}
 document.getElementById("period").addEventListener("change",draw);draw();
 document.getElementById("printReport").addEventListener("click",()=>window.print());
 document.getElementById("csvReport").addEventListener("click",()=>{const rows=[["Protocolo","Problema","Local","Categoria","Prioridade","Situação","Data"],...db().occurrences.map(o=>[o.id,o.title,o.local,o.category,o.priority,o.status,o.createdLabel])];const csv=rows.map(r=>r.map(x=>'"'+String(x??"").replaceAll('"','""')+'"').join(";")).join("\n");const a=document.createElement("a");a.href=URL.createObjectURL(new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8"}));a.download="relatorio-ocorrencias.csv";a.click();URL.revokeObjectURL(a.href);});
}
function initMessages(){
 const form=document.getElementById("messageForm"),list=document.getElementById("messageList");if(!list)return;
 function draw(){const messages=db().messages;list.innerHTML=messages.length?messages.map(m=>`<article class="card" style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;gap:10px"><strong>${escapeHTML(m.title)}</strong><span class="badge">${escapeHTML(m.date)}</span></div><p style="margin-top:10px;line-height:1.5">${escapeHTML(m.body)}</p><p class="muted">Publicado pela gestão</p>${!m.archived?`<button class="small secondary no-print" onclick="archiveMessage('${m.id}')">Arquivar</button>`:`<span class="badge">Arquivado</span>`}</article>`).join(""):`<div class="empty">Nenhum comunicado publicado.</div>`;}
 if(form)form.addEventListener("submit",e=>{e.preventDefault();if(currentSession()?.sector!=="Gestão"){alert("Somente a gestão pode publicar comunicados.");return;}const d=db();d.messages.unshift({id:Date.now().toString(),title:document.getElementById("messageTitle").value,body:document.getElementById("messageBody").value,date:new Date().toLocaleString("pt-BR"),archived:false});d.logs.unshift({action:"Publicou comunicado oficial",sector:"Gestão",date:new Date().toLocaleString("pt-BR")});save(d);form.reset();draw();});
 window.archiveMessage=id=>{if(currentSession()?.sector!=="Gestão"){alert("Somente a gestão pode arquivar comunicados.");return;}const d=db(),m=d.messages.find(x=>x.id===id);if(m)m.archived=true;d.logs.unshift({action:"Arquivou comunicado",sector:"Gestão",date:new Date().toLocaleString("pt-BR")});save(d);draw();};draw();
}
function initHistory(){
 const box=document.getElementById("historyList");if(!box)return;
 const all=db().occurrences;box.innerHTML=all.length?all.map(o=>`<article class="card" style="margin-bottom:12px"><strong>${escapeHTML(o.id)} — ${escapeHTML(o.title)}</strong><p class="muted">${escapeHTML(o.local)} • ${escapeHTML(o.status)}</p>${(o.history||[]).map(h=>`<p style="font-size:13px;margin-top:8px">• ${escapeHTML(h.date)} — ${escapeHTML(h.sector)}: ${escapeHTML(h.action)}</p>`).join("")}</article>`).join(""):`<div class="empty">O histórico aparecerá aqui quando houver atualizações.</div>`;
}
function initActivities(){
 const box=document.getElementById("activityList");if(!box)return;const logs=db().logs;box.innerHTML=logs.length?`<div class="table-wrap"><table><thead><tr><th>Data e horário</th><th>Setor responsável</th><th>Atividade</th></tr></thead><tbody>${logs.map(l=>`<tr><td>${escapeHTML(l.date)}</td><td>${escapeHTML(l.sector)}</td><td>${escapeHTML(l.action)}</td></tr>`).join("")}</tbody></table></div>`:`<div class="empty">Nenhuma atividade registrada.</div>`;
}
document.addEventListener("DOMContentLoaded",()=>{
 initLogin();initRegister();
 const page=document.body.dataset.page;
 if(page&&page!=="login"&&page!=="register"){if(!requireLogin())return;}
 if(page==="dashboard")initDashboard();\n if(page==="occurrence-form")initOccurrenceForm();
 if(page==="occurrences")initOccurrences();
 if(page==="management")initManagement();
 if(page==="map")initMap();
 if(page==="reports")initReports();
 if(page==="messages")initMessages();
 if(page==="history")initHistory();
 if(page==="activities")initActivities();
});
