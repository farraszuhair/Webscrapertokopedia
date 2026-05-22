/**
 * Tokopedia Scraper frontend controller.
 *
 * Active UI contract:
 * - product cards show only Benar / Salah
 * - Salah opens a modal before POST /api/feedback
 * - recommendations render as one collapsed clickable box
 */

const FEEDBACK_REASONS = [
  'Produk tidak relevan',
  'Harga tidak sesuai',
  'Nama produk salah',
  'Bukan produk utama / cuma aksesoris',
  'Duplikat',
  'Toko tidak terpercaya',
  'Gambar tidak sesuai',
  'Produk kosong / data tidak lengkap',
  'Bukan sesuai intent pencarian',
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
      recommendationsOpen: false,
      metadata: {},
      sortMode: 'terbaik',
      elapsedTimer: null,
      progressStartedAtMs: null,
      estimatedCompletionEpochMs: null,
      localElapsedSeconds: 0,
      localEtaSeconds: null,
      lastEtaFallbackSignature: null,
      lastProgress: null,
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
    this.bindQuickSort();
    this._createFeedbackModal();
  }

  show(panelId) {
    this.panels.forEach((id) => {
      const el = this.$(id);
      if (el) el.classList.toggle('hidden', id !== panelId);
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
    if (!budget || !info) {
      info?.classList.add('hidden');
      return;
    }
    const min = Math.round(budget * (1 - tol / 100));
    const max = Math.round(budget * (1 + tol / 100));
    this.$('bi-budget').textContent = this.formatRp(budget);
    this.$('bi-tolerance').textContent = `${tol}%`;
    this.$('bi-range').textContent = `${this.formatRp(min)} - ${this.formatRp(max)}`;
    info.classList.remove('hidden');
  }

  bindEnter() {
    this.$('query')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.startSearch();
    });
  }

  bindResetAI() {
    const btn = this.$('reset-ai-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      if (!window.confirm('Reset memori AI? Feedback dan contoh akan dihapus. Model Ollama tidak tersentuh.')) return;
      const oldText = btn.textContent;
      try {
        btn.disabled = true;
        btn.textContent = 'Resetting...';
        const res = await fetch('/api/ai/reset', { method: 'POST' });
        const data = await res.json();
        btn.textContent = data.success ? 'Reset OK' : 'Reset gagal';
      } catch (err) {
        console.error('Reset AI error:', err);
        btn.textContent = 'Reset error';
      } finally {
        setTimeout(() => {
          btn.textContent = oldText;
          btn.disabled = false;
        }, 1200);
      }
    });
  }

  bindQuickSort() {
    document.querySelectorAll('.quick-sort-btn').forEach((btn) => {
      btn.addEventListener('click', () => this.setSortMode(btn.dataset.sort || 'terbaik'));
    });
  }

  async startSearch() {
    const query = this.$('query')?.value.trim();
    const targetRaw = this.$('target_count')?.value ?? '';
    const parsedTarget = Number.parseInt(targetRaw, 10);
    const target = Number.isFinite(parsedTarget) && parsedTarget > 0 ? parsedTarget : 50;
    const tolerance = Number.parseFloat(this.$('tolerance')?.value || '20');
    const ai = this.$('use_ai')?.checked ?? true;
    const engineMode = this.$('engine_mode')?.value || 'auto';
    const aiMode = this.$('ai_mode')?.value || 'balanced';
    const budget = this.getBudgetText();

    if (!query) {
      this.setStatus('Error', 'status-error');
      this.$('query')?.focus();
      return;
    }

    this.state.query = query;
    this.state.comparison = [];
    this.state.selectedEngine = null;
    this.state.recommendations = {};
    this.state.recommendationsOpen = false;
    this.state.sortMode = this.activeSortMode();
    this.show('progress-panel');
    this.setStatus('Running', 'status-running');
    this.resetProgress();

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          target,
          target_count: target,
          budget,
          tolerance,
          ai,
          use_ai: ai,
          engine_mode: engineMode,
          ai_mode: aiMode,
          sort_mode: this.state.sortMode,
        }),
      });
      const data = await response.json();
      if (!data.success) {
        this.showError(data.error || 'Gagal memulai scraping');
        return;
      }
      this.state.searchId = data.search_id;
      this.state.progressStartedAtMs = data.started_at_epoch_ms || null;
      if (this.state.progressStartedAtMs) this.startElapsedTimer();
      this.startPolling();
    } catch (err) {
      this.showError('Gagal terhubung ke server: ' + err.message);
    }
  }

  startPolling() {
    this.stopPolling();
    this.fetchProgress();
    this.state.pollTimer = setInterval(() => this.fetchProgress(), 750);
  }

  stopPolling() {
    if (!this.state.pollTimer) return;
    clearInterval(this.state.pollTimer);
    this.state.pollTimer = null;
  }

  startElapsedTimer() {
    this.stopElapsedTimer();
    this.renderLiveTimers();
    this.state.elapsedTimer = setInterval(() => this.renderLiveTimers(), 1000);
  }

  stopElapsedTimer() {
    if (!this.state.elapsedTimer) return;
    clearInterval(this.state.elapsedTimer);
    this.state.elapsedTimer = null;
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
        this.stopElapsedTimer();
        progress.error ? this.showError(progress.error) : this.fetchResults();
      }
    } catch (err) {
      console.error('Progress error:', err);
    }
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
    this.stopPolling();
    this.stopElapsedTimer();
    this.state.progressStartedAtMs = null;
    this.state.estimatedCompletionEpochMs = null;
    this.state.localElapsedSeconds = 0;
    this.state.localEtaSeconds = null;
    this.state.lastEtaFallbackSignature = null;
    this.state.lastProgress = null;
    this.renderProgress({
      percent: 0,
      progress_percent: 0,
      stage: 'initializing',
      phase: 'initializing',
      message: 'Initializing...',
      found: 0,
      valid: 0,
      target: 0,
      started_at_epoch_ms: null,
      elapsed_seconds: 0,
      eta_seconds: null,
      engine_mode: this.$('engine_mode')?.value || 'auto',
      active_engine: 'none',
      attempt: 1,
      max_attempts: 1,
    });
    document.querySelectorAll('.stage-item').forEach((el) => el.classList.remove('active', 'done'));
  }

  formatDuration(seconds) {
    if (seconds == null || Number.isNaN(Number(seconds))) return 'calculating...';
    const safe = Math.max(0, Math.floor(Number(seconds)));
    const minutes = Math.floor(safe / 60);
    const secs = safe % 60;
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  computeLocalEta(estimatedCompletionEpochMs) {
    if (!estimatedCompletionEpochMs) return null;
    const remainingMs = Number(estimatedCompletionEpochMs) - Date.now();
    if (remainingMs < -5000) return null;
    return Math.max(0, Math.ceil(remainingMs / 1000));
  }

  updateEtaDeadline(progress) {
    if (progress.done) {
      this.state.estimatedCompletionEpochMs = progress.error ? null : Date.now();
      this.state.localEtaSeconds = progress.error ? null : 0;
      return;
    }

    const backendDeadline = Number(progress.estimated_completion_epoch_ms);
    if (Number.isFinite(backendDeadline) && backendDeadline > 0) {
      this.state.estimatedCompletionEpochMs = backendDeadline;
      this.state.lastEtaFallbackSignature = null;
      return;
    }

    if (progress.eta_seconds != null && Number.isFinite(Number(progress.eta_seconds))) {
      const signature = `${progress.updated_at_epoch_ms || ''}:${progress.eta_seconds}`;
      if (!this.state.estimatedCompletionEpochMs || signature !== this.state.lastEtaFallbackSignature) {
        this.state.estimatedCompletionEpochMs = Date.now() + Math.max(0, Number(progress.eta_seconds)) * 1000;
        this.state.lastEtaFallbackSignature = signature;
      }
      return;
    }

    this.state.estimatedCompletionEpochMs = null;
    this.state.localEtaSeconds = null;
    this.state.lastEtaFallbackSignature = null;
  }

  etaDisplayText() {
    const progress = this.state.lastProgress || {};
    if (progress.done) return progress.error ? '-' : '00:00';
    if (!this.state.estimatedCompletionEpochMs) return 'ETA: calculating...';

    const remainingMs = Number(this.state.estimatedCompletionEpochMs) - Date.now();
    if (remainingMs < -5000) return 'ETA: calculating...';
    if (remainingMs <= 0) return 'ETA: extending...';

    const seconds = this.computeLocalEta(this.state.estimatedCompletionEpochMs);
    this.state.localEtaSeconds = seconds;
    return seconds == null ? 'ETA: calculating...' : this.formatDuration(seconds);
  }

  renderLiveTimers() {
    const elapsedEl = this.$('pm-elapsed');
    if (elapsedEl && this.state.progressStartedAtMs) {
      const seconds = Math.floor((Date.now() - Number(this.state.progressStartedAtMs)) / 1000);
      this.state.localElapsedSeconds = Math.max(0, seconds);
      elapsedEl.textContent = this.formatDuration(this.state.localElapsedSeconds);
    }

    const etaEl = this.$('pm-eta');
    if (etaEl) etaEl.textContent = this.etaDisplayText();
  }

  renderProgress(progress) {
    this.state.lastProgress = progress;
    if (progress.started_at_epoch_ms) {
      this.state.progressStartedAtMs = Number(progress.started_at_epoch_ms);
      if (!this.state.elapsedTimer && !progress.done) this.startElapsedTimer();
    }
    this.updateEtaDeadline(progress);

    const pct = Math.max(0, Math.min(100, Number(progress.progress_percent ?? progress.percent ?? 0)));
    this.$('progress-pct').textContent = `${Math.round(pct)}%`;
    this.$('progress-bar').style.width = `${pct}%`;
    const phase = progress.phase || progress.stage;
    this.$('progress-stage-label').textContent = this.stageLabel(phase);
    this.$('progress-message').textContent = progress.message || '';
    this.$('pm-found').textContent = progress.found ?? 0;
    this.$('pm-valid').textContent = progress.valid ?? 0;
    this.$('pm-target').textContent = progress.target ?? '-';
    if (this.state.progressStartedAtMs) {
      this.renderLiveTimers();
    } else {
      this.$('pm-elapsed').textContent = progress.elapsed_seconds != null ? this.formatDuration(progress.elapsed_seconds) : '-';
      this.$('pm-eta').textContent = this.etaDisplayText();
    }
    this.$('pm-engine').textContent = `${progress.engine_mode || 'auto'} / ${progress.active_engine || 'none'}`;
    this.$('pm-attempt').textContent = `${progress.attempt || 1}/${progress.max_attempts || 1}`;
    this.updateStagePipeline(phase, pct);
  }

  stageLabel(stage) {
    const labels = {
      queued: 'Menunggu',
      initializing: 'Initializing',
      engine_selecting: 'Memilih engine',
      launching_browser: 'Launching browser',
      opening_page: 'Opening page',
      scrolling: 'Scrolling',
      extracting: 'Extracting',
      puppeteer_starting: 'Puppeteer start',
      puppeteer_opening: 'Puppeteer open',
      puppeteer_query: 'Puppeteer query',
      puppeteer_retry: 'Puppeteer retry',
      switching_to_rollback: 'Pindah ke Selenium',
      rollback_browser_starting: 'Selenium start',
      rollback_opening: 'Selenium open',
      rollback_extracting: 'Selenium extract',
      compare_filtering: 'Compare filter',
      deduplicating: 'Dedup',
      budget_filtering: 'Budget filter',
      ai_filtering: 'Qwen AI filter',
      ranking: 'Ranking',
      recommendation_building: 'Recommendations',
      finalizing: 'Finalizing',
      done: 'Selesai',
      error: 'Error',
      failed: 'Gagal',
      cancelled: 'Dibatalkan',
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
    this.state.sortMode = data.sort_mode || this.state.metadata.sort_mode || this.state.sortMode || 'terbaik';
    this.state.recommendationsOpen = false;

    this.applySortMode(this.state.sortMode, false);
    this.renderResultSummary(data);
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
    const meta = data.result_metadata || this.state.metadata || {};
    const requested = Number(meta.requested_count ?? data.requested_count ?? 0);
    const displayed = Number(meta.displayed_count ?? data.displayed_count ?? this.state.products.length);
    const limitedReason = meta.limited_reason || data.limited_reason;
    if (requested && displayed < requested) {
      messages.push(
        `Produk yang tampil kurang dari permintaan. Diminta ${requested}, tetapi hanya ${displayed} yang lolos.`
      );
      messages.push(`Alasan: ${limitedReason || 'hanya produk tersebut yang lolos filter setelah scraping dan AI.'}`);
    } else if (limitedReason) {
      messages.push(limitedReason);
    }
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
    if (!budgetInfo || !bar || !text) {
      bar?.classList.add('hidden');
      return;
    }
    text.textContent = `Budget ${this.formatRp(budgetInfo.budget)} | Range ${this.formatRp(budgetInfo.min)} - ${this.formatRp(budgetInfo.max)} | Tolerance ${budgetInfo.tolerance}%`;
    bar.classList.remove('hidden');
  }

  renderComparison(data) {
    const panel = this.$('comparison-panel');
    const grid = this.$('comparison-grid');
    if (!panel || !grid) return;

    const runs = data.engine_runs || this.state.comparison;
    if (!runs || !runs.length) {
      panel.classList.add('hidden');
      return;
    }

    panel.classList.remove('hidden');
    grid.innerHTML = '';

    for (const item of runs) {
      const card = document.createElement('div');
      const isSelected = item.engine === this.state.selectedEngine;
      card.className = `compare-card ${isSelected ? 'compare-selected' : ''}`;

      const pageOpened = item.opened_real_page;
      const pageStatus = pageOpened === false
        ? `<span class="compare-fail">opened_real_page: NO - ${this.esc(item.error_type || 'unknown')}</span>`
        : pageOpened === true
          ? '<span class="compare-ok">opened_real_page: YES</span>'
          : '<span class="compare-warn">opened_real_page: unknown</span>';

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
          <span>Qwen accepted: <b>${item.qwen_accepted_count ?? item.ai_valid_count ?? 0}</b></span>
          <span>Duration: ${item.duration_seconds ?? item.duration ?? 0}s</span>
          <span>Status: ${item.ok ? 'OK' : 'FAIL'}</span>
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
    this.state.recommendationsOpen = false;
    this.renderComparison({ engine_runs: this.state.comparison });
    this.renderRecommendations(this.state.recommendations);
    this.renderResultSummary(item);
    this.renderResultWarning({
      limited_reason: this.state.metadata.limited_reason,
      qwen_warning: item.qwen_warning || '',
      result_metadata: this.state.metadata,
    });
    this.updateResultCount();
    this.renderProducts();
  }

  renderResultSummary(data) {
    const meta = data.result_metadata || this.state.metadata || {};
    const requested = Number(meta.requested_count ?? data.requested_count ?? data.target_count ?? 0);
    const displayed = Number(meta.displayed_count ?? data.displayed_count ?? this.state.products.length);
    const raw = Number(meta.raw_scraped_count ?? meta.raw_scraped ?? data.raw_count ?? 0);
    const deduped = Number(meta.deduped_count ?? data.deduped_count ?? 0);
    const budget = Number(meta.budget_valid_count ?? data.budget_valid_count ?? data.budget_count ?? 0);
    const qwen = Number(meta.qwen_accepted_count ?? meta.ai_accepted_count ?? data.qwen_accepted_count ?? data.ai_valid_count ?? 0);

    this.setText('r-count', displayed || this.state.products.length || 0);
    this.setText('r-target', requested || '-');
    this.setText('rs-requested', requested || 0);
    this.setText('rs-raw', raw || 0);
    this.setText('rs-deduped', deduped || 0);
    this.setText('rs-budget', budget || 0);
    this.setText('rs-qwen', qwen || 0);
    this.setText('rs-displayed', displayed || this.state.products.length || 0);
  }

  renderRecommendations(recommendations) {
    const panel = this.$('recommendations-panel');
    const grid = this.$('recommendations-grid');
    if (!panel || !grid) return;

    const hasAny = ['cheapest', 'trusted', 'best'].some((key) => Boolean(recommendations?.[key]));
    if (!hasAny) {
      panel.classList.add('hidden');
      grid.innerHTML = '';
      return;
    }

    panel.classList.remove('hidden');
    panel.classList.toggle('recommendations-open', this.state.recommendationsOpen);
    grid.classList.toggle('hidden', !this.state.recommendationsOpen);

    const trigger = this.$('recommendations-trigger');
    if (trigger) {
      trigger.setAttribute('aria-expanded', String(this.state.recommendationsOpen));
      trigger.querySelector('.recommendation-trigger-state').textContent =
        this.state.recommendationsOpen ? 'Tutup' : 'Buka';
    }

    if (!this.state.recommendationsOpen) {
      grid.innerHTML = '';
      return;
    }

    const items = [
      ['cheapest', 'Harga Termurah'],
      ['trusted', 'Trusted'],
      ['best', 'Terbaik'],
    ];

    grid.innerHTML = '';
    for (const [key, label] of items) {
      grid.appendChild(this.createRecommendationCard(label, recommendations?.[key]));
    }
  }

  createRecommendationCard(label, product) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    if (!product) {
      card.innerHTML = `
        <div class="recommendation-label">${this.esc(label)}</div>
        <div class="recommendation-empty">Belum cukup data untuk rekomendasi ini.</div>
      `;
      return card;
    }

    const title = product.title || 'Produk Tokopedia';
    const img = product.image
      ? `<img src="${this.esc(product.image)}" alt="${this.esc(title)}" loading="lazy">`
      : '<div class="recommendation-img-placeholder">No image</div>';
    card.innerHTML = `
      <div class="recommendation-label">${this.esc(label)}</div>
      <div class="recommendation-main">
        <div class="recommendation-img">${img}</div>
        <div class="recommendation-body">
          <div class="recommendation-title">${this.esc(title)}</div>
          <div class="recommendation-price">${this.esc(product.price || '-')}</div>
          <div class="recommendation-meta">
            ${product.rating ? `<span>&#9733; ${this.esc(product.rating)}</span>` : ''}
            ${product.sold ? `<span>${this.esc(product.sold)}</span>` : ''}
          </div>
          ${product.shop_name ? `<div class="recommendation-shop">${this.esc(product.shop_name)}</div>` : ''}
          <div class="recommendation-reason">${this.esc(product.reason || '')}</div>
          ${product.url ? `<a class="recommendation-link" href="${this.esc(product.url)}" target="_blank" rel="noopener">Buka produk</a>` : ''}
        </div>
      </div>
    `;
    return card;
  }

  toggleRecommendations() {
    this.state.recommendationsOpen = !this.state.recommendationsOpen;
    this.renderRecommendations(this.state.recommendations);
  }

  updateResultCount() {
    const meta = this.state.metadata || {};
    const displayed = Number(meta.displayed_count ?? this.state.products.length);
    const requested = Number(meta.requested_count ?? this.$('r-target')?.textContent ?? displayed);
    this.setText('r-count', displayed || this.state.products.length);
    this.setText('r-target', requested || '-');
    this.setText('rs-displayed', displayed || this.state.products.length);
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

  activeSortMode() {
    return document.querySelector('.quick-sort-btn.active')?.dataset.sort || this.state.sortMode || 'terbaik';
  }

  setSortMode(mode) {
    this.applySortMode(mode, true);
  }

  applySortMode(mode, rerender) {
    const nextMode = ['most_trusted', 'termurah', 'terbaik'].includes(mode) ? mode : 'terbaik';
    this.state.sortMode = nextMode;
    document.querySelectorAll('.quick-sort-btn').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.sort === nextMode);
    });
    this.state.products = this.sortProducts(this.state.products, nextMode);
    if (rerender) {
      this.renderProducts();
      this.updateResultCount();
    }
  }

  sortProducts(products, mode) {
    const list = [...(products || [])];
    const numeric = (value, fallback = 0) => {
      const n = Number(value);
      return Number.isFinite(n) ? n : fallback;
    };
    const price = (p) => numeric(p.price_value ?? p.price, Number.MAX_SAFE_INTEGER);
    const relevance = (p) => numeric(p.relevance_score ?? p.ai_confidence, 0);
    const rating = (p) => numeric(p.rating, 0);
    const sold = (p) => numeric(p.sold_count, 0);
    const trust = (p) => {
      const shop = String(p.shop_name || p.shop || '').toLowerCase();
      const shopBoost = /(official|mall|power merchant|pro)/.test(shop) ? 1 : shop ? 0.5 : 0;
      return shopBoost + rating(p) / 5 + Math.min(sold(p), 1000) / 1000;
    };
    if (mode === 'termurah') return list.sort((a, b) => price(a) - price(b) || relevance(b) - relevance(a));
    if (mode === 'most_trusted') return list.sort((a, b) => trust(b) - trust(a) || relevance(b) - relevance(a));
    return list.sort((a, b) => relevance(b) - relevance(a) || rating(b) - rating(a) || sold(b) - sold(a));
  }

  createCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    const id = product.id || '';
    card.dataset.id = id;

    const title = product.title || 'Produk Tokopedia';
    const url = product.url || '#';
    const price = product.price_raw || product.price_text || '-';
    const image = product.image || product.image_url || '';
    const soldText = product.sold || product.sold_text || product.sold_count || '';
    const shopName = product.shop || product.shop_name || '';
    const shopLocation = product.location || product.shop_location || '';
    const imgHtml = image
      ? `<img src="${this.esc(image)}" alt="${this.esc(title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\"product-img-placeholder\\">No image</div>'">`
      : '<div class="product-img-placeholder">No image</div>';
    const aiValue = product.ai_confidence ?? product.relevance_score;
    const aiNumeric = Number(aiValue);
    const aiConfidenceLabel = product.ai_confidence_label
      || (aiNumeric >= 0.85 ? 'High' : aiNumeric >= 0.70 ? 'Medium' : 'Low');
    const confidenceClass = aiConfidenceLabel.toLowerCase();
    const confidence = aiValue != null && Number.isFinite(Number(aiValue))
      ? `<span class="ai-score conf-${this.esc(confidenceClass)}">AI ${Number(aiValue).toFixed(2)} ${this.esc(aiConfidenceLabel)}</span>`
      : '';
    const aiLabel = product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan');
    const aiReason = product.ai_confidence_explanation || product.ai_explanation || product.ai_reason || '';
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
            ${product.rating ? `<span class="product-rating">&#9733; ${this.esc(product.rating)}</span>` : ''}
            ${soldText ? `<span class="product-sold">${this.esc(soldText)}</span>` : ''}
          </div>
          ${shopName ? `<div class="product-shop">Shop: ${this.esc(shopName)}</div>` : ''}
          ${shopLocation ? `<div class="product-location">Location: ${this.esc(shopLocation)}</div>` : ''}
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
      <div class="modal-box" role="dialog" aria-modal="true" aria-label="Feedback salah">
        <div class="modal-header">
          <h3>Kenapa data ini salah?</h3>
          <button class="modal-close" id="modal-close" aria-label="Tutup">x</button>
        </div>
        <div class="modal-product" id="modal-product-info"></div>
        <p class="modal-question">Pilih satu atau lebih alasan.</p>
        <div class="modal-cats" id="modal-cats"></div>
        <div class="modal-note-wrap">
          <label for="modal-note">Penjelasan</label>
          <textarea id="modal-note" placeholder="Jelaskan kenapa AI salah..." maxlength="500"></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-primary" id="modal-submit">Save</button>
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
    const selectedReasons = Array.from(this._modal.querySelectorAll('input[name="reason"]:checked'))
      .map((cb) => cb.value);
    const customReason = this._modal.querySelector('#modal-note')?.value.trim() || '';
    this._submitFeedback(this._modalPid, {
      userAction: 'salah',
      feedbackType: 'negative',
      selectedReasons,
      customReason,
      correctedLabel: 'tidak_relevan',
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
      feedback_type: feedback.feedbackType || (feedback.userAction === 'benar' ? 'positive' : 'negative'),
      selected_reasons: feedback.selectedReasons || [],
      reasons: feedback.selectedReasons || [],
      custom_reason: feedback.customReason || '',
      note: feedback.customReason || '',
      corrected_label: feedback.correctedLabel,
      ai_label: product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan'),
      ai_confidence: product.ai_confidence ?? product.relevance_score ?? 0,
      rule_score: product.rule_score ?? 0,
      sort_mode: this.state.sortMode || 'terbaik',
      query_intent: product.query_intent || this.state.metadata.query_intent || '',
      product: {
        id: product.id || '',
        title: product.title || '',
        price: product.price_value ?? product.price ?? 0,
        store: product.shop_name || product.shop || '',
        url: product.url || product.product_url || '',
        image: product.image || product.image_url || '',
        product_category: product.product_category || '',
      },
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
      feedbackType: 'positive',
      selectedReasons: [],
      customReason: '',
      correctedLabel: 'relevan',
    });
  }

  showError(message) {
    this.stopPolling();
    this.stopElapsedTimer();
    this.setStatus('Error', 'status-error');
    this.show('error-panel');
    this.$('error-msg').textContent = message;
  }

  retry() {
    this.reset();
    setTimeout(() => this.startSearch(), 100);
  }

  reset() {
    this.stopPolling();
    this.stopElapsedTimer();
    this.setStatus('Idle', 'status-idle');
    this.show('search-panel');
  }

  setText(id, value) {
    const el = this.$(id);
    if (el) el.textContent = value;
  }

  esc(value) {
    const div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  }
}

let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new ScraperApp();
});
