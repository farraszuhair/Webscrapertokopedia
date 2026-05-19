/**
 * app.js - Tokopedia Scraper frontend controller.
 *
 * Features:
 * - Search form with engine mode, budget, AI toggle
 * - Progress polling with stage pipeline display
 * - Compare mode table with opened_real_page status
 * - Product cards with Benar/Salah feedback
 * - Feedback modal for Salah corrections
 * - AI reset button
 */

const FEEDBACK_REASONS = [
  'Produk tidak relevan',
  'Produk sebenarnya relevan',
  'Kategori salah',
  'AI salah paham judul',
  'Harga tidak sesuai',
  'Bukan produk yang dicari',
  'Aksesori dianggap produk utama',
  'Produk utama dianggap tidak relevan',
  'Gambar / data tidak sesuai',
  'Lainnya',
];

class ScraperApp {
  constructor() {
    this.state = {
      products: [],
      query: null,
      searchId: null,
      pollTimer: null,
      comparison: [],
      selectedEngine: null,
      recommendations: {},
      metadata: {},
    };

    this.$ = (id) => document.getElementById(id);
    this.panels = ['search-panel', 'progress-panel', 'error-panel', 'results-panel'];
    this.init();
  }

  init() {
    this.bindBudgetFormat();
    this.bindBudgetInfo();
    this.bindEnter();
    this.bindResetAI();
    this._createFeedbackModal();
  }

  show(panelId) {
    this.panels.forEach((id) => {
      const el = this.$(id);
      if (!el) return;
      el.classList.toggle('hidden', id !== panelId);
    });
  }

  setStatus(text, cls) {
    const el = this.$('status-badge');
    if (!el) return;
    el.textContent = text;
    el.className = `status-badge ${cls}`;
  }

  bindBudgetFormat() {
    const input = this.$('budget');
    if (!input) return;
    input.addEventListener('input', () => {
      const raw = input.value.replace(/[^\d]/g, '');
      input.value = raw ? Number.parseInt(raw, 10).toLocaleString('id-ID') : '';
      this.updateBudgetInfo();
    });
    input.addEventListener('keydown', (e) => {
      const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
      if (allowed.includes(e.key)) return;
      if (!/^\d$/.test(e.key)) e.preventDefault();
    });
  }

  getBudgetText() {
    return this.$('budget')?.value.trim() || null;
  }

  parseBudgetInput() {
    const text = this.getBudgetText();
    if (!text) return null;
    const n = Number.parseInt(text.replace(/\./g, ''), 10);
    return Number.isFinite(n) && n > 0 ? n : null;
  }

  formatRp(value) {
    const n = Number(value);
    if (!Number.isFinite(n) || n <= 0) return 'Rp0';
    return 'Rp' + n.toLocaleString('id-ID');
  }

  bindBudgetInfo() {
    this.$('tolerance')?.addEventListener('input', () => this.updateBudgetInfo());
  }

  updateBudgetInfo() {
    const budget = this.parseBudgetInput();
    const tol = Math.max(0, Math.min(Number.parseFloat(this.$('tolerance')?.value || '20'), 100));
    const info = this.$('budget-info');
    if (!budget || !info) { info?.classList.add('hidden'); return; }
    const min = Math.round(budget * (1 - tol / 100));
    const max = Math.round(budget * (1 + tol / 100));
    this.$('bi-budget').textContent = this.formatRp(budget);
    this.$('bi-tolerance').textContent = `${tol}%`;
    this.$('bi-range').textContent = `${this.formatRp(min)} - ${this.formatRp(max)}`;
    info.classList.remove('hidden');
  }

  bindEnter() {
    this.$('query')?.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.startSearch(); });
  }

  bindResetAI() {
    const btn = this.$('reset-ai-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      if (!confirm('Reset memori AI? (Feedback dan contoh akan dihapus. Model Ollama tidak tersentuh.)')) return;
      try {
        btn.disabled = true;
        const res = await fetch('/api/ai/reset', { method: 'POST' });
        const data = await res.json();
        alert(data.success ? 'Memori AI berhasil direset.' : 'Gagal mereset AI.');
      } catch (err) {
        alert('Error: ' + err.message);
      } finally {
        btn.disabled = false;
      }
    });
  }

  async startSearch() {
    const query = this.$('query')?.value.trim();
    const target = Number.parseInt(this.$('target_count')?.value || '25', 10);
    const tolerance = Number.parseFloat(this.$('tolerance')?.value || '20');
    const ai = this.$('use_ai')?.checked ?? true;
    const engineMode = this.$('engine_mode')?.value || 'auto';
    const budget = this.getBudgetText();

    if (!query) { alert('Query tidak boleh kosong'); return; }

    this.state.query = query;
    this.state.comparison = [];
    this.state.selectedEngine = null;
    this.show('progress-panel');
    this.setStatus('Running', 'status-running');
    this.resetProgress();

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query, target, target_count: target,
          budget, tolerance, ai, use_ai: ai, engine_mode: engineMode,
        }),
      });
      const data = await response.json();
      if (!data.success) { this.showError(data.error || 'Gagal memulai scraping'); return; }
      this.state.searchId = data.search_id;
      this.startPolling();
    } catch (err) {
      this.showError('Gagal terhubung ke server: ' + err.message);
    }
  }

  startPolling() {
    this.stopPolling();
    this.state.pollTimer = setInterval(() => this.fetchProgress(), 1000);
  }

  stopPolling() {
    if (!this.state.pollTimer) return;
    clearInterval(this.state.pollTimer);
    this.state.pollTimer = null;
  }

  async fetchProgress() {
    if (!this.state.searchId) return;
    try {
      const res = await fetch(`/api/progress/${this.state.searchId}`);
      if (!res.ok) return;
      const progress = await res.json();
      this.renderProgress(progress);
      if (progress.done) {
        this.stopPolling();
        progress.error ? this.showError(progress.error) : this.fetchResults();
      }
    } catch (_) {}
  }

  async fetchResults() {
    try {
      const res = await fetch(`/api/result/${this.state.searchId}`);
      if (!res.ok) throw new Error('Gagal mengambil hasil final.');
      const data = await res.json();
      this.showResults(data);
    } catch (err) {
      this.showError(err.message);
    }
  }

  resetProgress() {
    this.renderProgress({
      percent: 0, stage: 'queued', message: 'Memulai...', found: 0, valid: 0,
      target: 0, elapsed_seconds: 0, eta_seconds: null,
      engine_mode: this.$('engine_mode')?.value || 'auto',
      active_engine: 'none', attempt: 1, max_attempts: 1,
    });
    document.querySelectorAll('.stage-item').forEach((el) => el.classList.remove('active', 'done'));
  }

  renderProgress(progress) {
    const pct = Math.max(0, Math.min(100, progress.percent || 0));
    this.$('progress-pct').textContent = `${pct}%`;
    this.$('progress-bar').style.width = `${pct}%`;
    this.$('progress-stage-label').textContent = this.stageLabel(progress.stage);
    this.$('progress-message').textContent = progress.message || '';
    this.$('pm-found').textContent = progress.found ?? 0;
    this.$('pm-valid').textContent = progress.valid ?? 0;
    this.$('pm-target').textContent = progress.target ?? '-';
    this.$('pm-elapsed').textContent = progress.elapsed_seconds != null ? `${progress.elapsed_seconds}s` : '-';
    this.$('pm-eta').textContent = progress.eta_label || 'Calculating...';
    this.$('pm-engine').textContent = `${progress.engine_mode || 'auto'} / ${progress.active_engine || 'none'}`;
    this.$('pm-attempt').textContent = `${progress.attempt || 1}/${progress.max_attempts || 1}`;
    this.updateStagePipeline(progress.stage, pct);
  }

  stageLabel(stage) {
    const labels = {
      queued: 'Menunggu', initializing: 'Initializing', engine_selecting: 'Memilih engine',
      launching_browser: 'Launching browser', opening_page: 'Opening page',
      scrolling: 'Scrolling', extracting: 'Extracting',
      puppeteer_starting: 'Puppeteer start', puppeteer_opening: 'Puppeteer open',
      puppeteer_query: 'Puppeteer query', puppeteer_retry: 'Puppeteer retry',
      switching_to_rollback: 'Pindah ke Selenium',
      rollback_browser_starting: 'Selenium start', rollback_opening: 'Selenium open',
      rollback_extracting: 'Selenium extract', compare_filtering: 'Compare filter',
      deduplicating: 'Dedup', budget_filtering: 'Budget filter',
      ai_filtering: 'Qwen AI filter', ranking: 'Ranking', finalizing: 'Finalizing',
      done: 'Selesai', error: 'Error', failed: 'Gagal', cancelled: 'Dibatalkan',
    };
    return labels[stage] || stage || 'Processing';
  }

  updateStagePipeline(currentStage, pct) {
    const stages = ['init', 'opening', 'scrolling', 'extracting', 'filtering', 'ai_validation', 'finalizing'];
    stages.forEach((name, i) => {
      const el = this.$(`stage-${name}`);
      if (!el) return;
      el.classList.remove('active', 'done');
      const threshold = i * (100 / stages.length);
      const next = (i + 1) * (100 / stages.length);
      if (pct >= 100 || pct >= next) el.classList.add('done');
      else if (pct >= threshold) el.classList.add('active');
    });
  }

  showResults(data) {
    this.setStatus('Done', 'status-done');
    this.show('results-panel');
    this.state.comparison = data.comparison || [];
    this.state.selectedEngine = data.selected_engine || null;
    this.state.products = data.data || [];
    this.state.recommendations = data.recommendations || {};
    this.state.metadata = data.result_metadata || {};

    this.$('r-target').textContent = data.requested_count ?? '-';
    this.renderBudgetBar(data.budget_info);
    this.renderComparison(data);
    this.renderResultWarning(data);
    this.renderRecommendations(this.state.recommendations);
    this.updateResultCount();
    this.renderProducts();
  }

  renderResultWarning(data) {
    const box = this.$('r-warning');
    if (!box) return;
    const messages = [];
    if (data.limited_reason) messages.push(data.limited_reason);
    if (data.qwen_warning) messages.push(data.qwen_warning);
    if (!messages.length) {
      box.classList.add('hidden');
      box.textContent = '';
      return;
    }
    box.textContent = messages.join(' ');
    box.classList.remove('hidden');
  }

  renderBudgetBar(budgetInfo) {
    const bar = this.$('r-budget-bar');
    const text = this.$('r-budget-text');
    if (!budgetInfo || !bar || !text) { bar?.classList.add('hidden'); return; }
    text.textContent = `Budget ${this.formatRp(budgetInfo.budget)} | Range ${this.formatRp(budgetInfo.min)} - ${this.formatRp(budgetInfo.max)} | Tolerance ${budgetInfo.tolerance}%`;
    bar.classList.remove('hidden');
  }

  renderComparison(data) {
    const panel = this.$('comparison-panel');
    const grid = this.$('comparison-grid');
    if (!panel || !grid) return;

    const runs = data.engine_runs || this.state.comparison;
    if (!runs || !runs.length) { panel.classList.add('hidden'); return; }

    panel.classList.remove('hidden');
    grid.innerHTML = '';

    for (const item of runs) {
      const card = document.createElement('div');
      const isSelected = item.engine === this.state.selectedEngine;
      card.className = `compare-card ${isSelected ? 'compare-selected' : ''}`;

      // opened_real_page is the KEY diagnostic field
      const pageOpened = item.opened_real_page;
      const pageStatus = pageOpened === false
        ? `<span class="compare-fail">❌ opened_real_page: NO — ${this.esc(item.error_type || 'unknown')}</span>`
        : pageOpened === true
          ? `<span class="compare-ok">✅ opened_real_page: YES</span>`
          : `<span class="compare-warn">⚠️ opened_real_page: unknown</span>`;

      const debugFiles = (item.debug_files || []).filter(Boolean);
      const debugHtml = debugFiles.length
        ? `<div class="debug-files">${debugFiles.map(f => `<code>${this.esc(f)}</code>`).join('')}</div>`
        : '';

      card.innerHTML = `
        <strong class="compare-engine">${this.esc(item.engine)}</strong>
        ${pageStatus}
        <div class="compare-stats">
          <span>Raw scraped: <b>${item.raw_scraped ?? item.raw_count ?? 0}</b></span>
          <span>Budget valid: <b>${item.budget_valid_count ?? 0}</b></span>
          <span>Qwen accepted: <b>${item.ai_valid_count ?? 0}</b></span>
          <span>Duration: ${item.duration_seconds ?? item.duration ?? 0}s</span>
          <span>Status: ${item.ok ? '✅ OK' : '❌ FAIL'}</span>
        </div>
        ${item.error ? `<div class="compare-error">${this.esc(item.error)}</div>` : ''}
        ${debugFiles.length ? `<div class="compare-debug">Debug: ${debugHtml}</div>` : ''}
        ${item.products && item.products.length
          ? `<button class="btn btn-ghost compare-use-btn" data-engine="${this.esc(item.engine)}">Gunakan Hasil ${this.esc(item.engine)}</button>`
          : ''}
      `;

      card.querySelector('.compare-use-btn')?.addEventListener('click', () => {
        this.selectComparisonEngine(item.engine);
      });
      grid.appendChild(card);
    }
  }

  selectComparisonEngine(engine) {
    const item = this.state.comparison.find((e) => e.engine === engine);
    if (!item) return;
    this.state.selectedEngine = engine;
    this.state.products = item.data || item.products || [];
    this.state.recommendations = item.recommendations || {};
    this.state.metadata = item.result_metadata || {};
    this.renderComparison({ engine_runs: this.state.comparison });
    this.renderRecommendations(this.state.recommendations);
    this.renderResultWarning({
      limited_reason: this.state.metadata.limited_reason,
      qwen_warning: item.qwen_warning || '',
    });
    this.updateResultCount();
    this.renderProducts();
  }

  renderRecommendations(recommendations) {
    const panel = this.$('recommendations-panel');
    const grid = this.$('recommendations-grid');
    if (!panel || !grid) return;

    const items = [
      ['most_trusted', '&#128737; Most Trusted'],
      ['cheapest', '&#128176; Termurah'],
      ['best_overall', '&#11088; Terbaik'],
    ];

    grid.innerHTML = '';
    let rendered = 0;
    for (const [key, label] of items) {
      const product = recommendations?.[key];
      if (!product) continue;
      rendered += 1;
      const card = document.createElement('div');
      card.className = 'recommendation-card';
      const title = product.title || 'Produk Tokopedia';
      const img = product.image
        ? `<img src="${this.esc(product.image)}" alt="${this.esc(title)}" loading="lazy">`
        : '<div class="recommendation-img-placeholder">No image</div>';
      card.innerHTML = `
        <div class="recommendation-label">${label}</div>
        <div class="recommendation-main">
          <div class="recommendation-img">${img}</div>
          <div class="recommendation-body">
            <div class="recommendation-title">${this.esc(title)}</div>
            <div class="recommendation-price">${this.esc(product.price || '-')}</div>
            <div class="recommendation-meta">
              ${product.rating ? `<span>Rating ${this.esc(product.rating)}</span>` : ''}
              ${product.sold ? `<span>${this.esc(product.sold)}</span>` : ''}
            </div>
            ${product.shop_name ? `<div class="recommendation-shop">${this.esc(product.shop_name)}</div>` : ''}
            <div class="recommendation-reason">${this.esc(product.reason || '')}</div>
            ${product.url ? `<a class="recommendation-link" href="${this.esc(product.url)}" target="_blank" rel="noopener">Buka produk</a>` : ''}
          </div>
        </div>
      `;
      grid.appendChild(card);
    }

    panel.classList.toggle('hidden', rendered === 0);
  }

  updateResultCount() {
    this.$('r-count').textContent = this.state.products.length;
  }

  renderProducts() {
    const grid = this.$('products-grid');
    grid.innerHTML = '';
    if (!this.state.products.length) {
      grid.innerHTML = '<p class="no-results">Tidak ada produk valid untuk pilihan ini.</p>';
      return;
    }
    for (const product of this.state.products) {
      grid.appendChild(this.createCard(product));
    }
  }

  _createCardLegacy(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    const id = product.id || '';
    card.dataset.id = id;

    const title = product.title || 'Produk Tokopedia';
    const url = product.url || '#';
    const price = product.price_raw || '-';
    const imgHtml = product.image
      ? `<img src="${this.esc(product.image)}" alt="${this.esc(title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\"product-img-placeholder\\">No image</div>'">`
      : '<div class="product-img-placeholder">No image</div>';

    const confidence = product.relevance_score != null
      ? `<span class="ai-score">AI ${Number(product.relevance_score).toFixed(2)}</span>`
      : '';
    const aiReason = product.ai_reason
      ? `<div class="ai-reason">${this.esc(product.ai_reason)}</div>`
      : '';
    const aiCategories = (product.ai_categories || []).length
      ? `<div class="ai-cats">${product.ai_categories.map(c => `<span class="cat-tag">${this.esc(c)}</span>`).join('')}</div>`
      : '';

    card.innerHTML = `
      <a href="${this.esc(url)}" target="_blank" rel="noopener" class="product-link">
        <div class="product-img">${imgHtml}</div>
        <div class="product-body">
          <div class="product-title">${this.esc(title)}</div>
          <div class="product-price">${this.esc(price)}</div>
          <div class="product-stats">
            ${product.rating ? `<span class="product-rating">⭐ ${this.esc(product.rating)}</span>` : ''}
            ${product.sold ? `<span class="product-sold">${this.esc(product.sold)}</span>` : ''}
          </div>
          ${product.shop ? `<div class="product-shop">🏢 ${this.esc(product.shop)}</div>` : ''}
          ${product.location ? `<div class="product-location">📍 ${this.esc(product.location)}</div>` : ''}
          ${product.source_engine ? `<div class="product-source">${this.esc(product.source_engine)}</div>` : ''}
          ${confidence}${aiCategories}${aiReason}
        </div>
      </a>
      <div class="product-footer">
        <button class="btn-feedback btn-benar" data-id="${this.esc(id)}" data-correction="should_include" title="Produk ini benar/relevan">✅ Benar</button>
        <button class="btn-feedback btn-salah" data-id="${this.esc(id)}" data-correction="should_exclude" title="Produk ini salah/tidak relevan">❌ Salah</button>
        <button class="btn-feedback btn-relevan" data-id="${this.esc(id)}" data-correction="relevan" title="Tandai relevan">👍 Relevan</button>
        <button class="btn-feedback btn-tidak-relevan" data-id="${this.esc(id)}" data-correction="tidak_relevan" title="Tandai tidak relevan">👎 Tidak Relevan</button>
        <button class="btn-feedback btn-ajarkan" data-id="${this.esc(id)}" data-correction="ajarkan" title="Ajarkan AI dengan kategori">🧠 Ajarkan AI</button>
      </div>
    `;

    // Bind feedback buttons
    card.querySelectorAll('.btn-feedback').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const pid = btn.dataset.id;
        const correction = btn.dataset.correction;
        if (correction === 'ajarkan' || correction === 'should_exclude' || correction === 'tidak_relevan') {
          // Open popup for multi-category selection
          this._openFeedbackModal(pid, correction);
        } else {
          // Quick feedback - no popup needed
          this._submitFeedback(pid, correction, [], '');
        }
      });
    });

    return card;
  }

  // ── Feedback Modal ─────────────────────────────────────────────────────────

  createCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    const id = product.id || '';
    card.dataset.id = id;

    const title = product.title || 'Produk Tokopedia';
    const url = product.url || '#';
    const price = product.price_raw || product.price_text || '-';
    const image = product.image || product.image_url || '';
    const imgHtml = image
      ? `<img src="${this.esc(image)}" alt="${this.esc(title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\"product-img-placeholder\\">No image</div>'">`
      : '<div class="product-img-placeholder">No image</div>';
    const aiValue = product.ai_confidence ?? product.relevance_score;
    const confidence = aiValue != null && Number.isFinite(Number(aiValue))
      ? `<span class="ai-score">AI confidence ${Number(aiValue).toFixed(2)}</span>`
      : '';
    const aiLabel = product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan');
    const aiReason = product.ai_reason || product.ai_explanation || '';
    const aiCategories = (product.ai_categories || []).length
      ? `<div class="ai-cats">${product.ai_categories.map(c => `<span class="cat-tag">${this.esc(c)}</span>`).join('')}</div>`
      : '';

    card.innerHTML = `
      <a href="${this.esc(url)}" target="_blank" rel="noopener" class="product-link">
        <div class="product-img">${imgHtml}</div>
        <div class="product-body">
          <div class="product-title">${this.esc(title)}</div>
          <div class="product-price">${this.esc(price)}</div>
          <div class="product-stats">
            ${product.rating ? `<span class="product-rating">Rating ${this.esc(product.rating)}</span>` : ''}
            ${product.sold ? `<span class="product-sold">${this.esc(product.sold)}</span>` : ''}
          </div>
          ${product.shop ? `<div class="product-shop">Shop: ${this.esc(product.shop)}</div>` : ''}
          ${product.location ? `<div class="product-location">Location: ${this.esc(product.location)}</div>` : ''}
          ${product.source_engine ? `<div class="product-source">${this.esc(product.source_engine)}</div>` : ''}
          <div class="ai-line"><span class="ai-label">AI label: ${this.esc(aiLabel)}</span>${confidence}</div>
          ${aiCategories}
          ${aiReason ? `<div class="ai-reason">${this.esc(aiReason)}</div>` : ''}
        </div>
      </a>
      <div class="product-footer">
        <button class="btn-feedback btn-benar" data-id="${this.esc(id)}" data-action="benar" title="Produk ini benar">Benar</button>
        <button class="btn-feedback btn-salah" data-id="${this.esc(id)}" data-action="salah" title="Produk ini salah">Salah</button>
      </div>
    `;

    card.querySelectorAll('.btn-feedback').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const pid = btn.dataset.id;
        if (btn.dataset.action === 'salah') {
          this._openFeedbackModal(pid);
          return;
        }
        this._submitFeedback(pid, {
          userAction: 'benar',
          selectedReasons: [],
          customReason: '',
          correctedLabel: 'relevan',
        });
      });
    });

    return card;
  }

  _createFeedbackModal() {
    const modal = document.createElement('div');
    modal.id = 'feedback-modal';
    modal.className = 'modal hidden';
    modal.innerHTML = `
      <div class="modal-overlay" id="modal-overlay"></div>
      <div class="modal-box" role="dialog" aria-modal="true" aria-label="Feedback untuk AI">
        <div class="modal-header">
          <h3 id="modal-dynamic-title">🧠 Ajarkan AI</h3>
          <button class="modal-close" id="modal-close" aria-label="Tutup">✕</button>
        </div>
        <div class="modal-product" id="modal-product-info"></div>
        <p class="modal-label" id="modal-dynamic-label">Pilih kategori yang tepat (bisa lebih dari satu):</p>
        <div class="modal-cats" id="modal-cats"></div>
        <div class="modal-note-wrap">
          <label for="modal-note">Catatan (opsional):</label>
          <input type="text" id="modal-note" placeholder="Jelaskan kenapa AI salah..." maxlength="200">
        </div>
        <div class="modal-corrected-label" id="modal-corrected-label-wrap" style="display:none; margin-top: 15px;">
          <p class="modal-label">Koreksi Label:</p>
          <label><input type="radio" name="corrected_label" value="relevan"> Relevan</label>
          <label style="margin-left:10px;"><input type="radio" name="corrected_label" value="tidak_relevan"> Tidak relevan</label>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" id="modal-submit">Kirim feedback</button>
          <button class="btn btn-ghost" id="modal-cancel">Batal</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('#modal-overlay')?.addEventListener('click', () => this._closeFeedbackModal());
    modal.querySelector('#modal-close')?.addEventListener('click', () => this._closeFeedbackModal());
    modal.querySelector('#modal-cancel')?.addEventListener('click', () => this._closeFeedbackModal());
    modal.querySelector('#modal-submit')?.addEventListener('click', () => this._submitModalFeedback());

    // Build category checkboxes once
    const catsDiv = modal.querySelector('#modal-cats');
    FEEDBACK_CATEGORIES.forEach(({ key, label }) => {
      const item = document.createElement('label');
      item.className = 'cat-checkbox';
      item.innerHTML = `<input type="checkbox" name="cat" value="${key}"><span>${label}</span>`;
      catsDiv.appendChild(item);
    });

    this._modal = modal;
    this._modalPid = null;
    this._modalCorrection = null;
  }

  _openFeedbackModal(productId, correction) {
    const product = this.state.products.find((p) => p.id === productId);
    if (!product) return;

    this._modalPid = productId;
    this._modalCorrection = correction === 'ajarkan' ? 'should_exclude' : correction;

    const titleEl = this._modal.querySelector('#modal-dynamic-title');
    const labelWrap = this._modal.querySelector('#modal-corrected-label-wrap');
    const questionEl = this._modal.querySelector('#modal-dynamic-label');
    
    if (correction === 'should_exclude') {
        titleEl.textContent = 'Ini salah kenapa?';
        questionEl.textContent = 'Kenapa hasil ini salah?';
        labelWrap.style.display = 'block';
    } else {
        titleEl.textContent = '🧠 Ajarkan AI';
        questionEl.textContent = 'Pilih kategori yang tepat (bisa lebih dari satu):';
        labelWrap.style.display = 'none';
    }

    // Show product title in modal
    const info = this._modal.querySelector('#modal-product-info');
    if (info) {
      info.textContent = product.title || 'Produk';
    }

    // Reset checkboxes and note
    this._modal.querySelectorAll('input[name="cat"]').forEach((cb) => { cb.checked = false; });
    this._modal.querySelectorAll('input[name="corrected_label"]').forEach((rb) => { rb.checked = false; });
    const note = this._modal.querySelector('#modal-note');
    if (note) note.value = '';

    this._modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
  }

  _closeFeedbackModal() {
    this._modal?.classList.add('hidden');
    document.body.classList.remove('modal-open');
    this._modalPid = null;
  }

  _submitModalFeedback() {
    if (!this._modalPid) return;

    const selected = Array.from(this._modal.querySelectorAll('input[name="cat"]:checked'))
      .map((cb) => cb.value);
    const note = this._modal.querySelector('#modal-note')?.value.trim() || '';
    const correctedLabelRb = this._modal.querySelector('input[name="corrected_label"]:checked');
    const correctedLabel = correctedLabelRb ? correctedLabelRb.value : null;

    let finalCorrection = this._modalCorrection;
    if (correctedLabel) {
        finalCorrection = correctedLabel;
    }

    this._submitFeedback(this._modalPid, finalCorrection, selected, note);
    this._closeFeedbackModal();
  }

  async _submitFeedback(productId, correction, categories, note) {
    const product = this.state.products.find((p) => p.id === productId);
    if (!product) return;

    const payload = {
      search_id: this.state.searchId || "unknown",
      product_id: productId || "unknown",
      product_title: product.title || "",
      user_action: correction === "should_exclude" ? "salah" : correction === "should_include" ? "benar" : correction,
      selected_reasons: categories || [],
      custom_reason: note || "",
      corrected_label: correction === "relevan" || correction === "should_include" ? "relevan" : "tidak_relevan",
      ai_label: product.ai_decision ? "relevan" : "tidak_relevan",
      ai_confidence: product.relevance_score || 0,
      query: this.state.query || "",
      timestamp: new Date().toISOString()
    };

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.success) {
        // Visual feedback on button
        const card = document.querySelector(`[data-id="${productId}"]`)?.closest('.product-card');
        if (card) {
          card.classList.add('feedback-sent');
          card.title = `Feedback: ${correction}`;
        }
      } else {
        console.warn('Feedback gagal:', data);
      }
    } catch (err) {
      console.error('Feedback error:', err);
    }
  }

  // Old method name kept for backward compat with onclick attributes
  sendFeedback(productId, correction) {
    if (correction === 'should_exclude') {
      this._openFeedbackModal(productId, correction);
    } else {
      this._submitFeedback(productId, correction, [], '');
    }
  }

  _createFeedbackModal() {
    const modal = document.createElement('div');
    modal.id = 'feedback-modal';
    modal.className = 'modal hidden';
    modal.innerHTML = `
      <div class="modal-overlay" id="modal-overlay"></div>
      <div class="modal-box" role="dialog" aria-modal="true" aria-label="Feedback salah">
        <div class="modal-header">
          <h3>Ini salah kenapa?</h3>
          <button class="modal-close" id="modal-close" aria-label="Tutup">x</button>
        </div>
        <div class="modal-product" id="modal-product-info"></div>
        <p class="modal-question">Kenapa hasil ini salah?</p>
        <div class="modal-cats" id="modal-cats"></div>
        <div class="modal-note-wrap">
          <label for="modal-note">Penjelasan</label>
          <textarea id="modal-note" placeholder="Jelaskan kenapa AI salah..." maxlength="500"></textarea>
        </div>
        <div class="modal-corrected-label" id="modal-corrected-label-wrap">
          <p class="modal-label">Corrected label</p>
          <label><input type="radio" name="corrected_label" value="relevan"> Relevan</label>
          <label><input type="radio" name="corrected_label" value="tidak_relevan" checked> Tidak relevan</label>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" id="modal-submit">Kirim feedback</button>
          <button class="btn btn-ghost" id="modal-cancel">Batal</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('#modal-overlay')?.addEventListener('click', () => this._closeFeedbackModal());
    modal.querySelector('#modal-close')?.addEventListener('click', () => this._closeFeedbackModal());
    modal.querySelector('#modal-cancel')?.addEventListener('click', () => this._closeFeedbackModal());
    modal.querySelector('#modal-submit')?.addEventListener('click', () => this._submitModalFeedback());

    const reasonsDiv = modal.querySelector('#modal-cats');
    FEEDBACK_REASONS.forEach((reason) => {
      const item = document.createElement('label');
      item.className = 'cat-checkbox';
      item.innerHTML = `<input type="checkbox" name="reason" value="${this.esc(reason)}"><span>${this.esc(reason)}</span>`;
      reasonsDiv.appendChild(item);
    });

    this._modal = modal;
    this._modalPid = null;
  }

  _openFeedbackModal(productId) {
    const product = this.state.products.find((p) => p.id === productId);
    if (!product) return;

    this._modalPid = productId;
    const info = this._modal.querySelector('#modal-product-info');
    if (info) info.textContent = product.title || 'Produk';
    this._modal.querySelectorAll('input[name="reason"]').forEach((cb) => { cb.checked = false; });
    this._modal.querySelectorAll('input[name="corrected_label"]').forEach((rb) => {
      rb.checked = rb.value === 'tidak_relevan';
    });
    const note = this._modal.querySelector('#modal-note');
    if (note) note.value = '';

    this._modal.classList.remove('hidden');
    document.body.classList.add('modal-open');
  }

  _submitModalFeedback() {
    if (!this._modalPid) return;
    const selectedReasons = Array.from(this._modal.querySelectorAll('input[name="reason"]:checked'))
      .map((cb) => cb.value);
    const customReason = this._modal.querySelector('#modal-note')?.value.trim() || '';
    const corrected = this._modal.querySelector('input[name="corrected_label"]:checked')?.value || 'tidak_relevan';

    this._submitFeedback(this._modalPid, {
      userAction: 'salah',
      selectedReasons,
      customReason,
      correctedLabel: corrected,
    });
    this._closeFeedbackModal();
  }

  async _submitFeedback(productId, feedback) {
    const product = this.state.products.find((p) => p.id === productId);
    if (!product) return;

    const payload = {
      search_id: this.state.searchId || 'unknown',
      product_id: productId || 'unknown',
      product_title: product.title || '',
      user_action: feedback.userAction,
      selected_reasons: feedback.selectedReasons || [],
      custom_reason: feedback.customReason || '',
      corrected_label: feedback.correctedLabel,
      ai_label: product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan'),
      ai_confidence: product.ai_confidence ?? product.relevance_score ?? 0,
      query: this.state.query || '',
      timestamp: new Date().toISOString(),
    };

    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!data.success) {
        console.warn('Feedback gagal:', data);
        return;
      }
      const card = document.querySelector(`[data-id="${productId}"]`)?.closest('.product-card');
      if (card) {
        card.classList.add('feedback-sent');
        card.title = `Feedback: ${feedback.userAction}`;
      }
    } catch (err) {
      console.error('Feedback error:', err);
    }
  }

  sendFeedback(productId, correction) {
    if (correction === 'should_exclude' || correction === 'salah') {
      this._openFeedbackModal(productId);
      return;
    }
    this._submitFeedback(productId, {
      userAction: 'benar',
      selectedReasons: [],
      customReason: '',
      correctedLabel: 'relevan',
    });
  }

  showError(message) {
    this.stopPolling();
    this.setStatus('Error', 'status-error');
    this.show('error-panel');
    this.$('error-msg').textContent = message;
  }

  retry() { this.reset(); setTimeout(() => this.startSearch(), 100); }

  reset() {
    this.stopPolling();
    this.setStatus('Idle', 'status-idle');
    this.show('search-panel');
  }

  esc(value) {
    const div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  }
}

let app;
document.addEventListener('DOMContentLoaded', () => { app = new ScraperApp(); });
