// Frontend controller for search, progress polling, comparison, and feedback.

class ScraperApp {
  constructor() {
    this.state = {
      products: [],
      query: null,
      searchId: null,
      pollTimer: null,
      comparison: [],
      selectedEngine: null,
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

    input.addEventListener('keydown', (event) => {
      const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab', 'Home', 'End'];
      if (allowed.includes(event.key)) return;
      if (!/^\d$/.test(event.key)) event.preventDefault();
    });
  }

  getBudgetText() {
    const text = this.$('budget')?.value.trim() || '';
    return text || null;
  }

  parseBudgetInput() {
    const text = this.getBudgetText();
    if (!text) return null;
    const number = Number.parseInt(text.replace(/\./g, ''), 10);
    return Number.isFinite(number) && number > 0 ? number : null;
  }

  formatRp(value) {
    const number = Number(value);
    if (!Number.isFinite(number) || number <= 0) return 'Rp0';
    return 'Rp' + number.toLocaleString('id-ID');
  }

  bindBudgetInfo() {
    this.$('tolerance')?.addEventListener('input', () => this.updateBudgetInfo());
  }

  updateBudgetInfo() {
    const budget = this.parseBudgetInput();
    const tolerance = Math.max(0, Math.min(Number.parseFloat(this.$('tolerance')?.value || '20'), 100));
    const info = this.$('budget-info');

    if (!budget || !info) {
      info?.classList.add('hidden');
      return;
    }

    const min = Math.round(budget * (1 - tolerance / 100));
    const max = Math.round(budget * (1 + tolerance / 100));
    this.$('bi-budget').textContent = this.formatRp(budget);
    this.$('bi-tolerance').textContent = `${tolerance}%`;
    this.$('bi-range').textContent = `${this.formatRp(min)} - ${this.formatRp(max)}`;
    info.classList.remove('hidden');
  }

  bindEnter() {
    this.$('query')?.addEventListener('keypress', (event) => {
      if (event.key === 'Enter') this.startSearch();
    });
  }

  bindResetAI() {
    const btn = this.$('reset-ai-btn');
    if (!btn) return;

    btn.addEventListener('click', async () => {
      if (!confirm('Reset memori AI?')) return;
      try {
        btn.disabled = true;
        const res = await fetch('/api/ai/reset', { method: 'POST' });
        const data = await res.json();
        alert(data.success ? 'Memori AI berhasil direset.' : 'Gagal mereset AI.');
      } catch (error) {
        alert('Error: ' + error.message);
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

    if (!query) {
      alert('Query tidak boleh kosong');
      return;
    }

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
          query,
          target,
          target_count: target,
          budget,
          tolerance,
          ai,
          use_ai: ai,
          engine_mode: engineMode,
        }),
      });

      const data = await response.json();
      if (!data.success) {
        this.showError(data.error || 'Gagal memulai scraping');
        return;
      }

      this.state.searchId = data.search_id;
      this.startPolling();
    } catch (error) {
      this.showError('Gagal terhubung ke server: ' + error.message);
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
      const response = await fetch(`/api/progress/${this.state.searchId}`);
      if (!response.ok) return;
      const progress = await response.json();
      this.renderProgress(progress);

      if (progress.done) {
        this.stopPolling();
        progress.error ? this.showError(progress.error) : this.fetchResults();
      }
    } catch (_) {
      // Polling errors are transient while the server is busy.
    }
  }

  async fetchResults() {
    try {
      const response = await fetch(`/api/result/${this.state.searchId}`);
      if (!response.ok) throw new Error('Gagal mengambil hasil final.');
      const data = await response.json();
      this.showResults(data);
    } catch (error) {
      this.showError(error.message);
    }
  }

  resetProgress() {
    this.renderProgress({
      percent: 0,
      stage: 'queued',
      message: 'Memulai...',
      found: 0,
      valid: 0,
      target: 0,
      elapsed_seconds: 0,
      eta_seconds: null,
      engine_mode: this.$('engine_mode')?.value || 'auto',
      active_engine: 'none',
      attempt: 1,
      max_attempts: 1,
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
    this.$('pm-engine').textContent = `${progress.engine_mode || 'auto'} / ${progress.active_engine || progress.engine || 'none'}`;
    this.$('pm-attempt').textContent = `${progress.attempt || 1}/${progress.max_attempts || 1}`;
    this.updateStagePipeline(progress.stage, pct);
  }

  stageLabel(stage) {
    const labels = {
      queued: 'Menunggu giliran',
      engine_selecting: 'Memilih engine',
      puppeteer_starting: 'Puppeteer starting',
      puppeteer_opening: 'Puppeteer opening',
      puppeteer_query: 'Puppeteer query',
      puppeteer_query_failed: 'Puppeteer query failed',
      puppeteer_scrolling: 'Puppeteer scrolling',
      puppeteer_extracting: 'Puppeteer extracting',
      puppeteer_retry: 'Puppeteer retry',
      switching_to_rollback: 'Pindah ke Rollback/Selenium',
      rollback_browser_starting: 'Selenium starting',
      rollback_opening: 'Selenium opening',
      rollback_extracting: 'Selenium extracting',
      compare_filtering: 'Compare filtering',
      deduplicating: 'Deduplicating',
      category_filtering: 'Category filtering',
      budget_filtering: 'Budget filtering',
      ai_filtering: 'AI filtering',
      finalizing: 'Finalizing',
      done: 'Selesai',
      failed: 'Gagal',
      cancelled: 'Dibatalkan',
    };
    return labels[stage] || stage || 'Processing';
  }

  updateStagePipeline(currentStage, pct) {
    const domOrder = ['init', 'opening', 'scrolling', 'extracting', 'filtering', 'ai_validation', 'finalizing'];
    domOrder.forEach((name, index) => {
      const el = this.$(`stage-${name}`);
      if (!el) return;
      el.classList.remove('active', 'done');
      const threshold = index * (100 / domOrder.length);
      const nextThreshold = (index + 1) * (100 / domOrder.length);
      if (pct >= 100 || pct >= nextThreshold) el.classList.add('done');
      else if (pct >= threshold) el.classList.add('active');
    });
  }

  showResults(data) {
    this.setStatus('Done', 'status-done');
    this.show('results-panel');
    this.state.comparison = data.comparison || [];
    this.state.selectedEngine = data.selected_engine || null;
    this.state.products = data.data || [];

    this.$('r-target').textContent = data.requested_count ?? '-';
    this.renderBudgetBar(data.budget_info);
    this.renderComparison();
    this.updateResultCount();
    this.renderProducts();
  }

  renderBudgetBar(budgetInfo) {
    const bar = this.$('r-budget-bar');
    const text = this.$('r-budget-text');
    if (!budgetInfo || !bar || !text) {
      bar?.classList.add('hidden');
      return;
    }
    text.textContent =
      `Budget ${this.formatRp(budgetInfo.budget)} | ` +
      `Range ${this.formatRp(budgetInfo.min)} - ${this.formatRp(budgetInfo.max)} | ` +
      `Tolerance ${budgetInfo.tolerance}%`;
    bar.classList.remove('hidden');
  }

  renderComparison() {
    const panel = this.$('comparison-panel');
    const grid = this.$('comparison-grid');
    if (!panel || !grid) return;

    if (!this.state.comparison.length) {
      panel.classList.add('hidden');
      grid.innerHTML = '';
      return;
    }

    panel.classList.remove('hidden');
    grid.innerHTML = '';

    for (const item of this.state.comparison) {
      const card = document.createElement('div');
      card.className = `compare-card ${item.engine === this.state.selectedEngine ? 'active' : ''}`;
      const canUse = (item.valid_after_ai || 0) > 0;
      const rawCount = item.raw_count ?? item.raw_products_found ?? 0;
      const debugFiles = item.debug_files || [
        item.normalizer_debug_path,
        item.category_debug_path,
        item.budget_debug_path,
      ].filter(Boolean);
      const zeroRawMessage = rawCount === 0 ? '<small>No raw products extracted. Check selector/debug snapshot.</small>' : '';
      const debugHtml = debugFiles.length
        ? `<div class="debug-files">${debugFiles.map((file) => `<code>${this.esc(file)}</code>`).join('')}</div>`
        : '';
      card.innerHTML = `
        <strong>${this.esc(item.engine)}</strong>
        <span>Raw scraped: ${rawCount}</span>
        <span>Laptop candidates: ${item.laptop_candidates || 0}</span>
        <span>Rejected accessories: ${item.rejected_accessories || 0}</span>
        <span>Budget valid: ${item.valid_after_budget}</span>
        <span>AI valid: ${item.valid_after_ai}</span>
        <span>Duration: ${item.duration}s</span>
        <span>Status: ${this.esc(item.status || (item.ok ? 'success' : 'fail'))}</span>
        ${zeroRawMessage}
        ${item.error ? `<small>${this.esc(item.error)}</small>` : ''}
        ${debugHtml}
        <button class="compare-use" ${canUse ? '' : 'disabled'}>${item.engine === 'puppeteer' ? 'Use Puppeteer Results' : 'Use Rollback Results'}</button>
      `;
      card.querySelector('.compare-use')?.addEventListener('click', () => this.selectComparisonEngine(item.engine));
      grid.appendChild(card);
    }
  }

  selectComparisonEngine(engine) {
    const item = this.state.comparison.find((entry) => entry.engine === engine);
    if (!item) return;
    this.state.selectedEngine = engine;
    this.state.products = item.data || [];
    this.renderComparison();
    this.updateResultCount();
    this.renderProducts();
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

  createCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.dataset.id = product.id || '';

    const title = product.title || 'Produk Tokopedia';
    const url = product.url || product.link || '#';
    const price = product.price_raw || product.price_text || '-';
    const imageHtml = product.image
      ? `<img src="${this.esc(product.image)}" alt="${this.esc(title)}" loading="lazy" onerror="this.parentElement.innerHTML='<div class=\\'product-img-placeholder\\'>No image</div>'">`
      : '<div class="product-img-placeholder">No image</div>';
    const aiInfo =
      product.relevance_score != null
        ? `<div class="product-ai">AI Score: ${Number(product.relevance_score).toFixed(2)}<br><i>${this.esc(product.ai_reason || '')}</i></div>`
        : '';

    card.innerHTML = `
      <a href="${this.esc(url)}" target="_blank" rel="noopener" class="product-link">
        <div class="product-img">${imageHtml}</div>
        <div class="product-body">
          <div class="product-title">${this.esc(title)}</div>
          <div class="product-price">${this.esc(price)}</div>
          ${product.shop ? `<div class="product-shop">${this.esc(product.shop)}</div>` : ''}
          ${product.location ? `<div class="product-location">${this.esc(product.location)}</div>` : ''}
          ${product.source_engine ? `<div class="product-source">${this.esc(product.source_engine)}</div>` : ''}
          ${aiInfo}
        </div>
      </a>
      <div class="product-footer">
        <button class="btn-benar" onclick="event.stopPropagation();app.sendFeedback('${this.esc(product.id || '')}', 'should_include')">Benar</button>
        <button class="btn-salah" onclick="event.stopPropagation();app.sendFeedback('${this.esc(product.id || '')}', 'should_exclude')">Salah</button>
      </div>
    `;
    return card;
  }

  showError(message) {
    this.stopPolling();
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
    this.setStatus('Idle', 'status-idle');
    this.show('search-panel');
  }

  async sendFeedback(productId, feedbackType) {
    const product = this.state.products.find((item) => item.id === productId);
    if (!product) return;

    const reason = prompt(`Alasan produk ini ${feedbackType === 'should_include' ? 'benar' : 'salah'}?`);
    if (reason === null) return;

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: this.state.query, product, feedback: feedbackType, reason }),
      });
      const data = await response.json();
      alert(data.success ? 'Feedback tersimpan.' : 'Gagal menyimpan feedback.');
    } catch (error) {
      alert('Error: ' + error.message);
    }
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
