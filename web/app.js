// =====================================================
// FRONTEND APP (Python API Compatible)
// Features: Real progress polling, ETA, AI Feedback
// =====================================================

class ScraperApp {
  constructor() {
    this.state = {
      products: [],
      query: null,
      searchId: null,
      budgetInfo: null,
      pollTimer: null,
      selectedProduct: null,
    };

    this.$ = (id) => document.getElementById(id);
    this.panels = ['search-panel', 'progress-panel', 'error-panel', 'results-panel'];

    this.init();
  }

  // ── INIT ──────────────────────────────────────

  async init() {
    this.bindBudgetFormat();
    this.bindBudgetInfo();
    this.bindEnter();
    this.bindResetAI();
  }

  // ── SECTION HELPERS ───────────────────────────

  show(panelId) {
    this.panels.forEach((id) => {
      const el = this.$(id);
      if (el) {
        id === panelId ? el.classList.remove('hidden') : el.classList.add('hidden');
      }
    });
  }

  setStatus(text, cls) {
    const el = this.$('status-badge');
    if (!el) return;
    el.textContent = text;
    el.className = `status-badge ${cls}`;
  }

  // ── BUDGET FORMATTING ─────────────────────────

  bindBudgetFormat() {
    const input = this.$('budget');
    if (!input) return;

    input.addEventListener('input', () => {
      const raw = input.value.replace(/[^\d]/g, '');
      if (!raw) {
        input.value = '';
        return;
      }
      const formatted = parseInt(raw, 10).toLocaleString('id-ID');
      input.value = formatted;
    });

    input.addEventListener('keydown', (e) => {
      const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
      if (allowed.includes(e.key)) return;
      if (!/^\d$/.test(e.key)) e.preventDefault();
    });
  }

  parseBudgetInput() {
    const val = this.$('budget')?.value || '';
    if (!val.trim()) return null;
    const num = parseInt(val.replace(/\./g, ''), 10);
    return isNaN(num) || num <= 0 ? null : num;
  }

  formatRp(num) {
    if (!num || typeof num !== 'number') return '—';
    return 'Rp' + num.toLocaleString('id-ID');
  }

  // ── BUDGET INFO BOX ───────────────────────────

  bindBudgetInfo() {
    const budgetInput = this.$('budget');
    const tolInput = this.$('tolerance');
    if (!budgetInput || !tolInput) return;

    const update = () => this.updateBudgetInfo();
    budgetInput.addEventListener('input', update);
    tolInput.addEventListener('input', update);
  }

  updateBudgetInfo() {
    const budget = this.parseBudgetInput();
    const tol = Math.max(0, Math.min(parseFloat(this.$('tolerance')?.value) || 20, 100));
    const infoEl = this.$('budget-info');

    if (!budget || !infoEl) {
      infoEl?.classList.add('hidden');
      return;
    }

    const frac = tol / 100;
    const min = Math.round(budget * (1 - frac));
    const max = Math.round(budget * (1 + frac));

    this.$('bi-budget').textContent = this.formatRp(budget);
    this.$('bi-tolerance').textContent = `±${tol}%`;
    this.$('bi-range').textContent = `${this.formatRp(min)} - ${this.formatRp(max)}`;
    infoEl.classList.remove('hidden');
  }

  // ── BIND ENTER ────────────────────────────────

  bindEnter() {
    this.$('query')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.startSearch();
    });
  }
  
  // ── RESET AI ──────────────────────────────────
  bindResetAI() {
    const btn = this.$('reset-ai-btn'); // Assuming there is or will be a button for this
    if(btn) {
      btn.addEventListener('click', async () => {
         if(!confirm("Yakin ingin mereset memori AI? AI akan melupakan semua yang sudah dipelajari.")) return;
         try {
             btn.disabled = true;
             const res = await fetch('/api/ai/reset', { method: 'POST' });
             const data = await res.json();
             if(data.success) {
                 alert("Memori AI berhasil direset.");
             } else {
                 alert("Gagal mereset AI.");
             }
         } catch(e) {
             alert("Error: " + e.message);
         } finally {
             btn.disabled = false;
         }
      });
    }
  }

  // ── START SEARCH ─────────────────────────────

  async startSearch() {
    const query = this.$('query')?.value.trim();
    const targetCount = parseInt(this.$('target_count')?.value || '25');
    const budget = this.parseBudgetInput();
    const tolerance = parseFloat(this.$('tolerance')?.value || '20');
    const useAI = this.$('use_ai')?.checked ?? true;

    if (!query) {
      alert('Query tidak boleh kosong');
      return;
    }

    this.state.query = query;
    this.state.budgetInfo = budget ? { budget, tolerance } : null;

    this.show('progress-panel');
    this.setStatus('Running', 'status-running');
    this.resetProgress();

    try {
      const res = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, target_count: targetCount, budget, tolerance, use_ai: useAI }),
      });

      const data = await res.json();
      if (!data.success) {
        this.showError(data.error || 'Gagal memulai scraping');
        return;
      }

      this.state.searchId = data.search_id;
      this.startPolling();

    } catch (err) {
      this.showError('Gagal terhubung ke server: ' + err.message);
    }
  }

  // ── PROGRESS POLLING ─────────────────────────

  startPolling() {
    this.stopPolling();
    this.state.pollTimer = setInterval(() => this.fetchProgress(), 1000);
  }

  stopPolling() {
    if (this.state.pollTimer) {
      clearInterval(this.state.pollTimer);
      this.state.pollTimer = null;
    }
  }

  async fetchProgress() {
    if (!this.state.searchId) return;
    
    try {
      const res = await fetch(`/api/progress/${this.state.searchId}`);
      if (!res.ok) return;
      
      const data = await res.json();
      this.renderProgress(data);
      
      if (data.done) {
        this.stopPolling();
        if (data.error) {
            this.showError(data.error);
        } else {
            this.fetchResults();
        }
      }
    } catch (_) {}
  }
  
  async fetchResults() {
      try {
          const res = await fetch(`/api/result/${this.state.searchId}`);
          if (!res.ok) throw new Error("Gagal mengambil hasil final.");
          const data = await res.json();
          this.state.products = data.data || [];
          setTimeout(() => this.showResults(data), 500);
      } catch (err) {
          this.showError(err.message);
      }
  }

  resetProgress() {
    this.renderProgress({ percent: 0, stage: 'init', message: 'Memulai...', found: 0, valid: 0, target: 0, elapsed_seconds: 0, eta_seconds: null });
    document.querySelectorAll('.stage-item').forEach((el) => {
      el.classList.remove('active', 'done');
    });
  }

  renderProgress(p) {
    const pct = Math.max(0, Math.min(100, p.percent || 0));

    const pctEl = this.$('progress-pct');
    const barEl = this.$('progress-bar');
    const stageEl = this.$('progress-stage-label');
    const msgEl = this.$('progress-message');

    if (pctEl) pctEl.textContent = `${pct}%`;
    if (barEl) barEl.style.width = `${pct}%`;
    if (stageEl) stageEl.textContent = this.stageLabel(p.stage);
    if (msgEl) msgEl.textContent = p.message || '';

    if (this.$('pm-found')) this.$('pm-found').textContent = p.found ?? 0;
    if (this.$('pm-valid')) this.$('pm-valid').textContent = p.valid ?? 0;
    if (this.$('pm-target')) this.$('pm-target').textContent = p.target ?? '—';
    if (this.$('pm-elapsed')) this.$('pm-elapsed').textContent = p.elapsed_seconds != null ? `${p.elapsed_seconds}s` : '—';
    
    const etaEl = this.$('pm-eta');
    if (etaEl) {
        if (p.eta_seconds === null || p.eta_seconds === undefined) {
            etaEl.textContent = 'Calculating...';
        } else {
            etaEl.textContent = `${p.eta_seconds}s`;
        }
    }
    
    if (this.$('pm-engine')) this.$('pm-engine').textContent = p.engine || 'unknown';
    if (this.$('pm-attempt')) this.$('pm-attempt').textContent = `${p.attempt || 1}/${p.max_attempts || 3}`;

    this.updateStagePipeline(p.stage, pct);
  }

  stageLabel(stage) {
    const labels = {
      queued: 'Menunggu Giliran',
      engine_selecting: '🚀 Memilih Engine...',
      puppeteer_starting: '🚀 Membuka Browser (Puppeteer)...',
      puppeteer_opening: '🌐 Membuka Tokopedia...',
      puppeteer_scrolling: '📜 Scroll Halaman...',
      puppeteer_extracting: '📦 Ekstrak Produk...',
      switching_to_rollback: '⚠️ Pindah ke Fallback Scraper...',
      rollback_starting: '🚀 Mulai Fallback Scraper...',
      rollback_extracting: '📜 Scroll & Ekstrak...',
      deduplicating: '🧹 Menghapus Duplikat...',
      budget_filtering: '💰 Memfilter Budget...',
      ai_filtering: '🤖 Validasi AI...',
      finalizing: '✨ Finalisasi Hasil...',
      done: '✅ Selesai!',
      failed: '❌ Gagal',
      cancelled: '🛑 Dibatalkan'
    };
    return labels[stage] || stage || 'Processing...';
  }

  updateStagePipeline(currentStage, pct) {
    const order = [
        'engine_selecting', 
        'puppeteer_opening', 
        'rollback_starting', 
        'budget_filtering', 
        'ai_filtering', 
        'finalizing'
    ];
    
    // Map intermediate states to the main UI states
    const stageMap = {
        'queued': -1,
        'engine_selecting': 0,
        'puppeteer_starting': 1,
        'puppeteer_opening': 1,
        'puppeteer_scrolling': 1,
        'puppeteer_extracting': 1,
        'switching_to_rollback': 2,
        'rollback_starting': 2,
        'rollback_extracting': 2,
        'deduplicating': 3,
        'budget_filtering': 3,
        'ai_filtering': 4,
        'finalizing': 5,
        'done': 6
    };

    const currentIdx = stageMap[currentStage] !== undefined ? stageMap[currentStage] : 0;
    
    // The HTML has elements like stage-init, stage-opening, etc.
    // Let's map our index to those DOM ids:
    const domOrder = ['init', 'opening', 'scrolling', 'extracting', 'filtering', 'ai_validation', 'finalizing'];
    // For simplicity, we just fill them up progressively based on percentage
    
    domOrder.forEach((s, i) => {
      const el = this.$(`stage-${s}`);
      if (!el) return;
      el.classList.remove('active', 'done');
      if (pct >= 100 || (pct > (i * (100 / domOrder.length)))) {
        if (pct < 100 && pct < ((i + 1) * (100 / domOrder.length))) {
            el.classList.add('active');
        } else {
            el.classList.add('done');
        }
      }
    });

    if (pct >= 100) {
      domOrder.forEach((s) => this.$(`stage-${s}`)?.classList.add('done'));
      this.$(`stage-finalizing`)?.classList.remove('active');
    }
  }

  // ── SHOW RESULTS ─────────────────────────────

  showResults(data) {
    this.setStatus('Done', 'status-done');
    this.show('results-panel');

    const count = this.$('r-count');
    const target = this.$('r-target');
    if (count) count.textContent = data.count ?? 0;
    if (target) target.textContent = data.requested_count ?? '—';

    // Budget bar
    const budgetBar = this.$('r-budget-bar');
    const budgetText = this.$('r-budget-text');
    if (data.budget_info && budgetBar && budgetText) {
      const bi = data.budget_info;
      const min = this.formatRp(bi.min);
      const max = this.formatRp(bi.max);
      budgetText.textContent = `Budget: ${this.formatRp(bi.budget)} · Toleransi ±${bi.tolerance}% · Range: ${min} - ${max}`;
      budgetBar.classList.remove('hidden');
    } else {
      budgetBar?.classList.add('hidden');
    }

    this.renderProducts();
  }

  renderProducts() {
    const grid = this.$('products-grid');
    if (!grid) return;
    grid.innerHTML = '';

    if (!this.state.products.length) {
      grid.innerHTML = '<p class="no-results">Tidak ada produk ditemukan.</p>';
      return;
    }

    for (const p of this.state.products) {
      grid.appendChild(this.createCard(p));
    }
  }

  createCard(p) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.dataset.id = p.id;

    const imgHtml = p.image
      ? `<img src="${this.esc(p.image)}" alt="${this.esc(p.title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'product-img-placeholder\\'>📦</div>'">`
      : '<div class="product-img-placeholder">📦</div>';

    const aiInfo = p.relevance_score != null ? `<div class="product-ai">AI Score: ${p.relevance_score.toFixed(2)}<br><i>${this.esc(p.ai_reason)}</i></div>` : '';

    card.innerHTML = `
      <a href="${this.esc(p.link)}" target="_blank" rel="noopener" style="text-decoration:none;color:inherit;">
        <div class="product-img">${imgHtml}</div>
        <div class="product-body">
          <div class="product-title">${this.esc(p.title)}</div>
          <div class="product-price">${this.esc(p.price_text || '—')}</div>
          ${p.shop ? `<div class="product-shop">🏪 ${this.esc(p.shop)}</div>` : ''}
          ${p.location ? `<div class="product-location">📍 ${this.esc(p.location)}</div>` : ''}
          ${aiInfo}
        </div>
      </a>
      <div class="product-footer">
        <button class="btn-benar" onclick="event.stopPropagation();app.sendFeedback('${p.id}', 'should_include')">✓ Benar</button>
        <button class="btn-salah" onclick="event.stopPropagation();app.sendFeedback('${p.id}', 'should_exclude')">✗ Salah</button>
      </div>
    `;

    return card;
  }

  esc(str) {
    if (!str) return '';
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
  }

  // ── ERROR ────────────────────────────────────

  showError(message) {
    this.stopPolling();
    this.setStatus('Error', 'status-error');
    this.show('error-panel');
    const el = this.$('error-msg');
    if (el) el.textContent = message;
  }

  retry() {
    this.reset();
    setTimeout(() => this.startSearch(), 100);
  }

  reset() {
    this.stopPolling();
    this.setStatus('Idle', 'status-idle');
    this.show('search-panel');
  }

  // ── FEEDBACK ─────────────────────────────────

  async sendFeedback(productId, feedbackType) {
    const p = this.state.products.find((x) => x.id === productId);
    if (!p) return;

    const reason = prompt(`Alasan mengapa produk ini ${feedbackType === 'should_include' ? 'benar' : 'salah'}?`);
    if (reason === null) return; // cancelled

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: this.state.query, product: p, feedback: feedbackType, reason: reason }),
      });

      const data = await res.json();
      if (data.success) {
        alert("Feedback tersimpan. AI akan belajar dari ini.");
        const card = document.querySelector(`[data-id="${p.id}"]`);
        if (card) {
          card.style.opacity = '0.6';
          card.style.filter = feedbackType === 'should_include' ? 'sepia(1) hue-rotate(90deg)' : 'grayscale(0.7)';
        }
      } else {
        alert('Gagal menyimpan feedback: ' + (data.detail || 'Unknown error'));
      }
    } catch (err) {
      alert('Error: ' + err.message);
    }
  }
}

// ── INIT ──────────────────────────────────────────

let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new ScraperApp();
});
