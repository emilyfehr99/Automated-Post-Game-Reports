(function() {
  const qs = (sel) => document.querySelector(sel);
  const pageTitleEl = qs('#pageTitle');
  const pageUrlEl = qs('#pageUrl');
  const cvatContextEl = qs('#cvatContext');
  const categoryEl = qs('#category');
  const severityEl = qs('#severity');
  const notesEl = qs('#notes');
  const entriesEl = qs('#entries');
  const filterTaskEl = qs('#filterTask');
  const filterJobEl = qs('#filterJob');
  const filterFrameEl = qs('#filterFrame');
  const filterCurrentBtn = qs('#filterCurrent');
  const clearFiltersBtn = qs('#clearFilters');
  const undoBtn = qs('#undoBtn');
  let lastDeleted = null;

  function parseCvatContext(url) {
    try {
      const u = new URL(url);
      const parts = u.pathname.split('/').filter(Boolean);
      let taskId = null, jobId = null, frame = null;
      for (let i = 0; i < parts.length; i++) {
        if (parts[i] === 'tasks' && parts[i+1]) taskId = parts[i+1];
        if (parts[i] === 'jobs' && parts[i+1]) jobId = parts[i+1];
      }
      const f = u.searchParams.get('frame') || u.searchParams.get('frame_id') || null;
      frame = f ? String(f) : null;
      return { taskId, jobId, frame };
    } catch {
      return { taskId: null, jobId: null, frame: null };
    }
  }

  function nowIso() { return new Date().toISOString(); }

  function renderEntries(entries) {
    entriesEl.innerHTML = '';
    const filtered = entries.filter(e => {
      if (filterTaskEl.value && String(e.taskId || '') !== String(filterTaskEl.value)) return false;
      if (filterJobEl.value && String(e.jobId || '') !== String(filterJobEl.value)) return false;
      if (filterFrameEl.value && String(e.frame || '') !== String(filterFrameEl.value)) return false;
      return true;
    });
    filtered.slice().reverse().forEach((e, idx) => {
      const li = document.createElement('li');
      li.className = 'entry';
      const title = `${e.category} • ${e.severity}`;
      const ctx = [];
      if (e.taskId) ctx.push(`task ${e.taskId}`);
      if (e.jobId) ctx.push(`job ${e.jobId}`);
      if (e.frame) ctx.push(`frame ${e.frame}`);
      const ctxStr = ctx.join(' · ');
      li.innerHTML = `
        <div class="row">
          <div class="left">
            <div class="meta">${new Date(e.timestamp).toLocaleString()} · ${title}</div>
            <div class="meta">${ctxStr}</div>
            <div class="text">${(e.notes || '').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}</div>
          </div>
          <div class="right controls">
            <button data-action="copy" data-index="${idx}">Copy</button>
            <button data-action="delete" data-index="${idx}">Delete</button>
          </div>
        </div>
      `;
      entriesEl.appendChild(li);
    });
  }

  async function loadAndRender() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab?.url || '';
    pageTitleEl.textContent = tab?.title || '—';
    pageUrlEl.textContent = url || '—';
    if (url) pageUrlEl.href = url;
    const { taskId, jobId, frame } = parseCvatContext(url);
    const ctx = [];
    if (taskId) ctx.push(`Task ${taskId}`);
    if (jobId) ctx.push(`Job ${jobId}`);
    if (frame) ctx.push(`Frame ${frame}`);
    cvatContextEl.textContent = ctx.join(' / ') || '—';

    const { entries = [] } = await chrome.storage.local.get({ entries: [] });
    renderEntries(entries);
  }

  async function saveEntry(partial) {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const url = tab?.url || '';
    const { taskId, jobId, frame } = parseCvatContext(url);
    const entry = {
      timestamp: nowIso(),
      pageTitle: tab?.title || '',
      url,
      taskId,
      jobId,
      frame,
      category: categoryEl.value,
      severity: severityEl.value,
      notes: notesEl.value.trim(),
      ...partial,
    };
    const key = 'entries';
    const data = await chrome.storage.local.get({ [key]: [] });
    data[key].push(entry);
    await chrome.storage.local.set({ [key]: data[key] });
    notesEl.value = '';
    await loadAndRender();
  }

  function toCsv(entries) {
    const headers = [
      'timestamp','pageTitle','url','taskId','jobId','frame','category','severity','notes'
    ];
    const rows = entries.map(e => headers.map(h => {
      const val = e[h] ?? '';
      const str = String(val).replace(/"/g, '""');
      return `"${str}"`;
    }).join(','));
    return [headers.join(','), ...rows].join('\n');
  }

  async function exportData() {
    const { entries = [] } = await chrome.storage.local.get({ entries: [] });
    if (entries.length === 0) {
      alert('No entries to export.');
      return;
    }
    const csv = toCsv(entries);
    const json = JSON.stringify(entries, null, 2);

    const blobCsv = new Blob([csv], { type: 'text/csv' });
    const blobJson = new Blob([json], { type: 'application/json' });

    const urlCsv = URL.createObjectURL(blobCsv);
    const urlJson = URL.createObjectURL(blobJson);

    const a1 = document.createElement('a');
    a1.href = urlCsv; a1.download = `cvat_audit_${Date.now()}.csv`; a1.click();
    const a2 = document.createElement('a');
    a2.href = urlJson; a2.download = `cvat_audit_${Date.now()}.json`; a2.click();

    setTimeout(() => { URL.revokeObjectURL(urlCsv); URL.revokeObjectURL(urlJson); }, 2000);
  }

  document.addEventListener('click', async (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;
    if (t.id === 'saveBtn') {
      await saveEntry({});
    } else if (t.id === 'quickOcclusion') {
      categoryEl.value = 'occlusion';
      await saveEntry({ notes: notesEl.value.trim() || 'Occlusion' });
    } else if (t.id === 'quickRinkPoint') {
      categoryEl.value = 'on_rink_point';
      await saveEntry({ notes: notesEl.value.trim() || 'Point placed on rink' });
    } else if (t.id === 'quickMisplaced') {
      categoryEl.value = 'joint_misplaced';
      await saveEntry({ notes: notesEl.value.trim() || 'Misplaced joint' });
    } else if (t.id === 'quickWrongAssoc') {
      categoryEl.value = 'wrong_person_association';
      await saveEntry({ notes: notesEl.value.trim() || 'Wrong person association' });
    } else if (t.id === 'exportBtn') {
      await exportData();
    } else if (t.id === 'filterCurrent') {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const { taskId, jobId, frame } = parseCvatContext(tab?.url || '');
      filterTaskEl.value = taskId || '';
      filterJobEl.value = jobId || '';
      filterFrameEl.value = frame || '';
      const { entries = [] } = await chrome.storage.local.get({ entries: [] });
      renderEntries(entries);
    } else if (t.id === 'clearFilters') {
      filterTaskEl.value = '';
      filterJobEl.value = '';
      filterFrameEl.value = '';
      const { entries = [] } = await chrome.storage.local.get({ entries: [] });
      renderEntries(entries);
    } else if (t.dataset.action === 'copy') {
      const { entries = [] } = await chrome.storage.local.get({ entries: [] });
      const idxFromBottom = Number(t.dataset.index);
      const filtered = entries.filter(e => {
        if (filterTaskEl.value && String(e.taskId || '') !== String(filterTaskEl.value)) return false;
        if (filterJobEl.value && String(e.jobId || '') !== String(filterJobEl.value)) return false;
        if (filterFrameEl.value && String(e.frame || '') !== String(filterFrameEl.value)) return false;
        return true;
      });
      const entry = filtered.slice().reverse()[idxFromBottom];
      if (entry) {
        const line = `${entry.timestamp} | ${entry.category} | ${entry.severity} | task ${entry.taskId || '-'} job ${entry.jobId || '-'} frame ${entry.frame || '-'} | ${entry.notes || ''}`;
        await navigator.clipboard.writeText(line);
        t.textContent = 'Copied';
        setTimeout(() => (t.textContent = 'Copy'), 1000);
      }
    } else if (t.dataset.action === 'delete') {
      const { entries = [] } = await chrome.storage.local.get({ entries: [] });
      const filtered = entries.filter(e => {
        if (filterTaskEl.value && String(e.taskId || '') !== String(filterTaskEl.value)) return false;
        if (filterJobEl.value && String(e.jobId || '') !== String(filterJobEl.value)) return false;
        if (filterFrameEl.value && String(e.frame || '') !== String(filterFrameEl.value)) return false;
        return true;
      });
      const idxFromBottom = Number(t.dataset.index);
      const target = filtered.slice().reverse()[idxFromBottom];
      if (!target) return;
      const newEntries = entries.slice();
      const originalIndex = newEntries.findIndex(x => x.timestamp === target.timestamp && x.url === target.url && x.category === target.category && x.notes === target.notes);
      if (originalIndex >= 0) {
        const removed = newEntries.splice(originalIndex, 1)[0];
        lastDeleted = removed;
        await chrome.storage.local.set({ entries: newEntries });
        undoBtn.disabled = false;
        renderEntries(newEntries);
      }
    }
  });

  undoBtn?.addEventListener('click', async () => {
    if (!lastDeleted) return;
    const key = 'entries';
    const data = await chrome.storage.local.get({ [key]: [] });
    data[key].push(lastDeleted);
    await chrome.storage.local.set({ [key]: data[key] });
    lastDeleted = null;
    undoBtn.disabled = true;
    renderEntries(data[key]);
  });

  document.addEventListener('DOMContentLoaded', loadAndRender);
})();

