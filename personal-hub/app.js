function formatToday() {
  const d = new Date();
  const opts = { weekday: 'long', month: 'long', day: 'numeric' };
  return d.toLocaleDateString(undefined, opts);
}

document.getElementById('today').textContent = formatToday();

// Segmented control switching
const segments = Array.from(document.querySelectorAll('.segment'));
segments.forEach(btn => {
  btn.addEventListener('click', () => {
    segments.forEach(b => b.classList.remove('segment-active'));
    btn.classList.add('segment-active');
    const target = btn.dataset.section;
    document.querySelectorAll('.section').forEach(s => s.classList.remove('section-active'));
    document.getElementById(`section-${target}`).classList.add('section-active');
  });
});

// Health sub-tabs (Summary, Browse, Sharing)
const subTabs = Array.from(document.querySelectorAll('#section-health .segmented-sub .segment'));
subTabs.forEach(btn => {
  btn.addEventListener('click', () => {
    subTabs.forEach(b => b.classList.remove('segment-active'));
    btn.classList.add('segment-active');
    const tab = btn.dataset.subtab;
    document.querySelectorAll('#section-health .subtab').forEach(el => el.classList.remove('subtab-active'));
    document.querySelector(`#section-health .subtab-${tab}`).classList.add('subtab-active');
  });
});

// Sidebar navigation → open Browse category sections when clicked
const sidebarCats = Array.from(document.querySelectorAll('.sidebar [data-cat]'));
sidebarCats.forEach(item => {
  item.addEventListener('click', () => {
    try {
      const browseBtn = document.querySelector('#section-health .segmented-sub .segment[data-subtab="browse"]');
      if (browseBtn) browseBtn.click();
      const cat = item.getAttribute('data-cat');
      // wait for layout to switch before querying elements
      requestAnimationFrame(() => {
        const detailsEl = document.querySelector(`#section-health .subtab-browse .browse-cat[data-cat="${cat}"]`);
        if (detailsEl) {
          detailsEl.open = true;
          detailsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    } catch (e) {
      console.error('Navigation error:', e);
    }
  });
});

// Chart helpers
function createLine(ctx, color, data) {
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map((_, i) => i + 1),
      datasets: [{
        data,
        borderColor: color,
        backgroundColor: 'transparent',
        tension: 0.35,
        borderWidth: 2,
        pointRadius: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { display: false },
        y: { display: false }
      },
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });
}

function createBar(ctx, color, data) {
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map((_, i) => i + 1),
      datasets: [{
        data,
        backgroundColor: color,
        borderRadius: 6,
        maxBarThickness: 18
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { display: false },
        y: { display: false }
      },
      plugins: { legend: { display: false }, tooltip: { enabled: false } }
    }
  });
}

// Seed random-ish demo data
function randSeq(n, base, vary) {
  return Array.from({ length: n }, (_, i) => {
    const jiggle = Math.sin(i * 0.6) * vary + (Math.random() - 0.5) * vary * 0.6;
    return Math.max(0, base + jiggle);
  });
}

// Create charts once DOM and Chart.js are ready
window.addEventListener('DOMContentLoaded', () => {
  const healthColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-health').trim();
  const financeColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-finances').trim();
  const goalsColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-goals').trim();

  // Health
  // Activity rings: compute dasharray based on circumference
  function setRingProgress(id, pct) {
    const el = document.getElementById(id);
    if (!el) return;
    const r = parseFloat(el.getAttribute('r'));
    const c = 2 * Math.PI * r;
    const filled = Math.max(0, Math.min(1, pct)) * c;
    el.style.strokeDasharray = `${filled} ${Math.max(0, c - filled)}`;
  }

  // Example values similar to Apple Activity (Move/Exercise/Stand)
  setRingProgress('ring-move', 540/700);
  setRingProgress('ring-exercise', 28/30);
  setRingProgress('ring-stand', 10/12);

  const steps = document.getElementById('chart-steps');
  if (steps) createBar(steps, healthColor, randSeq(14, 7000, 2500));

  const hr = document.getElementById('chart-hr');
  if (hr) createLine(hr, '#ff375f', randSeq(30, 65, 12));

  const sleep = document.getElementById('chart-sleep');
  if (sleep) createLine(sleep, healthColor, randSeq(14, 7, 1.5));

  const vo2 = document.getElementById('chart-vo2');
  if (vo2) createLine(vo2, '#30d158', randSeq(16, 42, 2));

  const spo2 = document.getElementById('chart-spo2');
  if (spo2) createLine(spo2, '#64d2ff', randSeq(16, 97, 1));

  const resp = document.getElementById('chart-resp');
  if (resp) createLine(resp, '#bf5af2', randSeq(16, 14, 2));

  const audio = document.getElementById('chart-audio');
  if (audio) createBar(audio, '#0a84ff', randSeq(14, 4, 2));

  // Finances
  const spending = document.getElementById('chart-spending');
  if (spending) createBar(spending, financeColor, randSeq(30, 60, 40));

  const networth = document.getElementById('chart-networth');
  if (networth) createLine(networth, financeColor, randSeq(24, 120, 18));

  const savings = document.getElementById('chart-savings');
  if (savings) createLine(savings, financeColor, randSeq(12, 20, 8));

  const donut = document.getElementById('chart-spending-donut');
  if (donut) new Chart(donut, {
    type: 'doughnut',
    data: {
      labels: ['Groceries', 'Dining', 'Transport', 'Shopping', 'Bills'],
      datasets: [{ data: [320, 180, 90, 260, 420], backgroundColor: ['#22c55e','#f59e0b','#06b6d4','#a78bfa','#ef4444'] }]
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, cutout: '60%' }
  });

  const cashflow = document.getElementById('chart-cashflow');
  if (cashflow) new Chart(cashflow, {
    type: 'bar',
    data: {
      labels: ['May','Jun','Jul','Aug','Sep','Oct'],
      datasets: [
        { label: 'Income', data: [5200,5100,5300,5400,5500,5600], backgroundColor: '#22c55e', borderRadius: 6 },
        { label: 'Expenses', data: [3900,4100,4000,4200,4300,4400], backgroundColor: '#ef4444', borderRadius: 6 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { x: { display: false }, y: { display: false } },
      plugins: { legend: { display: false } }
    }
  });

  // Goals
  const reading = document.getElementById('chart-reading');
  if (reading) createBar(reading, goalsColor, randSeq(12, 1, 0.8));

  const streak = document.getElementById('chart-streak');
  if (streak) createBar(streak, goalsColor, randSeq(10, 5, 3));

  const habits = document.getElementById('chart-habits');
  if (habits) createLine(habits, goalsColor, randSeq(14, 4, 1.5));

  // Investments chart
  const investments = document.getElementById('chart-investments');
  if (investments) {
    new Chart(investments, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          data: [82000, 83500, 84200, 85600, 87100, 89420],
          borderColor: '#ff9500',
          backgroundColor: 'rgba(255, 149, 0, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { display: false },
          y: { display: false }
        }
      }
    });
  }
});

// Integration placeholders
function toast(message) {
  alert(message);
}

const btnBank = document.getElementById('btn-connect-bank');
if (btnBank) {
  btnBank.addEventListener('click', async () => {
    try {
      const res = await fetch('http://localhost:4000/api/plaid/create_link_token', { method: 'POST' });
      const { link_token } = await res.json();
      if (!link_token) throw new Error('No link_token');
      // Load Plaid Link JS if not present
      if (!window.Plaid) {
        await new Promise((resolve, reject) => {
          const s = document.createElement('script');
          s.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
          s.onload = resolve;
          s.onerror = reject;
          document.head.appendChild(s);
        });
      }
      const handler = window.Plaid.create({
        token: link_token,
        onSuccess: async (public_token, metadata) => {
          try {
            await fetch('http://localhost:4000/api/plaid/exchange_public_token', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ public_token })
            });
            toast('Bank connected successfully (sandbox).');
          } catch (e) {
            toast('Exchange failed. Check server.');
          }
        },
        onExit: (err, metadata) => {
          if (err) console.error('Plaid exit error', err);
        }
      });
      handler.open();
    } catch (e) {
      console.error(e);
      toast('Unable to start Plaid link. Is the server running?');
    }
  });
}

const btnCSV = document.getElementById('btn-import-csv');
const csvUpload = document.getElementById('csv-upload');
if (btnCSV && csvUpload) {
  btnCSV.addEventListener('click', () => csvUpload.click());
  csvUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const csv = e.target.result;
        console.log('CSV loaded:', csv.substring(0, 200) + '...');
        toast('CSV uploaded! Parsing and updating dashboard...');
        // TODO: Parse CSV and update charts/accounts
      };
      reader.readAsText(file);
    }
  });
}

const btnApple = document.getElementById('btn-apple-signin');
if (btnApple) {
  btnApple.addEventListener('click', () => {
    toast('Sign in with Apple web flow (Apple JS) or native app auth.');
  });
}

const btnHealthZip = document.getElementById('btn-apple-health-import');
if (btnHealthZip) {
  btnHealthZip.addEventListener('click', () => {
    toast('Select Health app export ZIP for parsing (client or backend).');
  });
}

// iPhone preview toggle
const previewBtn = document.getElementById('btn-iphone-preview');
if (previewBtn) {
  previewBtn.addEventListener('click', () => {
    const body = document.body;
    if (!body.classList.contains('iphone-preview')) {
      body.classList.add('iphone-preview');
      // Wrap existing content into an iPhone frame
      const root = document.querySelector('.app-root');
      if (root && !document.querySelector('.iphone-frame')) {
        const frame = document.createElement('div');
        frame.className = 'iphone-frame';
        frame.innerHTML = '<div class="iphone-notch"></div><div class="iphone-screen"></div>';
        const screen = frame.querySelector('.iphone-screen');
        root.parentNode.insertBefore(frame, root);
        screen.appendChild(root);
      }
      previewBtn.textContent = 'Exit iPhone Preview';
    } else {
      // Unwrap
      const frame = document.querySelector('.iphone-frame');
      const screen = document.querySelector('.iphone-screen');
      const root = document.querySelector('.app-root');
      if (frame && screen && root) {
        frame.parentNode.insertBefore(root, frame);
        frame.remove();
      }
      document.body.classList.remove('iphone-preview');
      previewBtn.textContent = 'iPhone Preview';
    }
  });
}


