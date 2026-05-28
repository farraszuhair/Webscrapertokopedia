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
  'Cuma aksesoris',
  'Spesifikasi tidak sesuai query',
  'Harga tidak sesuai',
  'Nama produk salah',
  'Gambar tidak sesuai',
  'Toko tidak terpercaya',
  'Duplikat',
  'Bukan sesuai intent pencarian',
  'Data tidak lengkap',
  'Lainnya',
];

const RECOMMENDATION_MODES = [
  { key: 'terbaik', label: 'Terbaik', shortLabel: 'Terbaik', icon: '⭐', sortMode: 'terbaik' },
  { key: 'termurah', label: 'Termurah', shortLabel: 'Termurah', icon: '💸', sortMode: 'termurah' },
  { key: 'trusted', label: 'Most Trusted', shortLabel: 'Trusted', icon: '🏆', sortMode: 'most_trusted' },
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
      aiStatus: null,
      engineMode: 'auto',
      recommendationMode: 'terbaik',
      hasUserSelectedRecommendation: false,
      autoExpandedOnce: false,
      activeFeedbackProductId: null,
    };

    this.activeProduct = null;
    this.activeProductCard = null;
    this.isModalAnimating = false;

    this.$ = (id) => document.getElementById(id);
    this.panels = ['search-panel', 'progress-panel', 'error-panel', 'results-panel'];
    this.recommendationObserver = null;
    this.recommendationTimeline = null;
    this.init();
  }

  init() {
    this.bindBudgetFormat();
    this.bindBudgetInfo();
    this.bindEnter();
    this.bindResetAI();
    this.bindResetLearning();
    this.bindQuickSort();
    this.bindProductModalEvents();
    this.bindRecommendationModalEvents();
    this.bindProductCardClick();
    this.fetchAiStatus();
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

  isBlockedMessage(message) {
    return /captcha|blocked|access denied|too many requests|robot|bot detection/i.test(String(message || ''));
  }

  prefersReducedMotion() {
    return Boolean(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches);
  }

  canAnimate() {
    return Boolean(window.anime) && !this.prefersReducedMotion();
  }

  animate(targets, options = {}) {
    if (!this.canAnimate()) return null;
    return window.anime({ targets, ...options });
  }

  showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    window.setTimeout(() => toast.classList.add('is-visible'), 10);
    window.setTimeout(() => {
      toast.classList.remove('is-visible');
      window.setTimeout(() => toast.remove(), 180);
    }, 1800);
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

  formatRupiah(value) {
    const number = Number(value || 0);
    if (!number) return 'Harga tidak tersedia';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      maximumFractionDigits: 0,
    }).format(number);
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

  bindResetLearning() {
    const btn = this.$('reset-learning-btn');
    if (!btn) return;
    btn.addEventListener('click', async () => {
      if (!window.confirm('Yakin hapus semua pembelajaran AI?')) return;
      const oldText = btn.textContent;
      try {
        btn.disabled = true;
        btn.textContent = 'Resetting...';
        const res = await fetch('/api/learning/reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scope: 'all' }),
        });
        const data = await res.json();
        btn.textContent = data.success ? 'Reset OK' : 'Reset gagal';
        this.showToast(data.success ? 'Learning direset' : 'Reset learning gagal');
      } catch (err) {
        console.error('Reset learning error:', err);
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
    document.querySelectorAll('[data-sort-mode]').forEach((btn) => {
      btn.addEventListener('click', () => this.setSortMode(btn.dataset.sortMode || 'terbaik'));
    });
  }

  async fetchAiStatus() {
    try {
      const res = await fetch('/api/ai/status');
      const status = await res.json();
      this.state.aiStatus = status;
      this.renderAiStatus(status);
    } catch (err) {
      const fallback = {
        ok: false,
        classifier: null,
        capabilities: { semantic: false, json_repair: false },
        missing: ['gemma3:4b', 'llama3.2:3b', 'phi4-mini', 'nomic-embed-text'],
        message: 'Ollama belum bisa dihubungi. Search tetap bisa berjalan dengan rules.',
        install_commands: [
          'ollama pull gemma3:4b',
          'ollama pull llama3.2:3b',
          'ollama pull phi4-mini',
          'ollama pull nomic-embed-text',
        ],
      };
      this.state.aiStatus = fallback;
      this.renderAiStatus(fallback);
      console.warn('AI status error:', err);
    }
  }

  renderAiStatus(status) {
    const badge = this.$('ai-status-badge');
    const message = this.$('ai-status-message');
    const classifier = this.$('ai-status-classifier');
    const semantic = this.$('ai-status-semantic');
    const json = this.$('ai-status-json');
    const install = this.$('ai-install-command');
    const useAi = this.$('use_ai');
    if (!badge || !message || !classifier || !semantic || !json || !install) return;

    const capabilities = status?.capabilities || {};
    badge.textContent = status?.ok ? 'Ready' : 'Rules only';
    badge.className = `ai-status-badge ${status?.ok ? 'is-ready' : 'is-missing'}`;
    message.textContent = status?.ok
      ? (status.message || 'AI Orchestrator ready')
      : 'Model AI belum terinstall. Jalankan: ollama pull gemma3:4b';
    classifier.textContent = status?.classifier || 'Rules only';
    semantic.textContent = capabilities.semantic ? 'nomic-embed-text installed' : 'nomic-embed-text missing';
    json.textContent = capabilities.json_repair ? 'phi4-mini installed' : 'phi4-mini missing';

    const commands = status?.install_commands || [
      'ollama pull gemma3:4b',
      'ollama pull llama3.2:3b',
      'ollama pull phi4-mini',
      'ollama pull nomic-embed-text',
    ];
    const missing = Array.isArray(status?.missing) ? status.missing : [];
    const missingCommands = commands.filter((cmd) => missing.some((model) => cmd.includes(model)));
    if (status?.ok) {
      install.textContent = missingCommands.length
        ? ['Model opsional yang belum terinstall:', ...missingCommands].join('\n')
        : '';
      install.classList.toggle('hidden', !missingCommands.length);
      if (useAi) {
        useAi.disabled = false;
        useAi.checked = true;
      }
    } else {
      install.textContent = commands.join('\n');
      install.classList.remove('hidden');
      if (useAi) {
        useAi.checked = false;
        useAi.disabled = true;
      }
    }
  }

  async startSearch() {
    const query = this.$('query')?.value.trim();
    const targetRaw = this.$('target_count')?.value ?? '';
    const parsedTarget = Number.parseInt(targetRaw, 10);
    const target = Number.isFinite(parsedTarget) && parsedTarget > 0 ? parsedTarget : 50;
    const tolerance = Number.parseFloat(this.$('tolerance')?.value || '20');
    const ai = this.$('use_ai')?.checked ?? true;
    const engineMode = this.$('engine_mode')?.value || 'auto';
    const targetFirstMode = this.$('target_first_mode')?.checked ?? false;
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
          sort_mode: this.state.sortMode,
          target_first_mode: targetFirstMode,
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

  scrambleToText(el, targetText, duration = 900) {
    if (!el) return;

    const chars = "01#$%AI<>SCRAPE{}[]";
    const start = performance.now();

    const frame = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const revealCount = Math.floor(targetText.length * progress);

      let output = "";

      for (let i = 0; i < targetText.length; i++) {
        if (i < revealCount) {
          output += targetText[i];
        } else {
          output += chars[Math.floor(Math.random() * chars.length)];
        }
      }

      el.textContent = output;

      if (progress < 1) {
        requestAnimationFrame(frame);
      } else {
        el.textContent = targetText;
      }
    };

    requestAnimationFrame(frame);
  }

  startScrambleProgress() {
    const el = document.querySelector(".progress-scramble-text");
    if (!el) return;

    this.stopScrambleProgress();

    const progressMessages = [
      "Mengambil data marketplace...",
      "Membaca kartu produk...",
      "Membersihkan duplikat...",
      "Mengecek budget...",
      "AI sedang audit kandidat...",
      "Menyusun rekomendasi terbaik...",
      "Menyiapkan hasil..."
    ];

    this._scrambleIndex = 0;
    const play = () => {
      const text = progressMessages[this._scrambleIndex % progressMessages.length];
      this.scrambleToText(el, text, 900);
      this._scrambleIndex += 1;
    };

    play();
    this._scrambleTimer = setInterval(play, 1400);
  }

  stopScrambleProgress(finalText = "Selesai — hasil siap ditampilkan") {
    if (this._scrambleTimer) {
      clearInterval(this._scrambleTimer);
      this._scrambleTimer = null;
    }

    const el = document.querySelector(".progress-scramble-text");
    if (el) this.scrambleToText(el, finalText, 850);
  }

  startProgressAnimation() {
    this.startScrambleProgress();
  }

  stopProgressAnimation() {
    let finalText = "Selesai — hasil siap ditampilkan";
    if (this.state.lastProgress && this.state.lastProgress.error) {
      finalText = "Pipeline error — cek log";
    }
    this.stopScrambleProgress(finalText);
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
    this.stopProgressAnimation();
    this.stopScrambleProgress("Menunggu proses...");
    this.renderProgress({
      percent: 0,
      progress_percent: 0,
      stage: 'preparing',
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
      logs: [{ stage: 'initializing', message: 'Initializing...' }],
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
    if (!this.state.estimatedCompletionEpochMs) return 'Menghitung...';

    const remainingMs = Number(this.state.estimatedCompletionEpochMs) - Date.now();
    if (remainingMs < -5000) return 'Menghitung...';
    if (remainingMs <= 0) return 'Memperbarui...';

    const seconds = this.computeLocalEta(this.state.estimatedCompletionEpochMs);
    this.state.localEtaSeconds = seconds;
    return seconds == null ? 'Menghitung...' : this.formatDuration(seconds);
  }

  renderLiveTimers() {
    const elapsedTextEl = this.$('elapsedText');
    const etaTextEl = this.$('etaText');
    const seconds = this.state.progressStartedAtMs
      ? Math.floor((Date.now() - Number(this.state.progressStartedAtMs)) / 1000)
      : 0;
    this.state.localElapsedSeconds = Math.max(0, seconds);
    const elapsedFormatted = this.formatDuration(this.state.localElapsedSeconds);

    if (elapsedTextEl) elapsedTextEl.textContent = elapsedFormatted;

    const etaText = this.etaDisplayText();
    if (etaTextEl) etaTextEl.textContent = etaText;

    const elapsedEl = this.$('pm-elapsed');
    const resultElapsedEl = this.$('rt-elapsed');
    if (elapsedEl) elapsedEl.textContent = elapsedFormatted;
    if (resultElapsedEl) resultElapsedEl.textContent = elapsedFormatted;

    const etaEl = this.$('pm-eta');
    const resultEtaEl = this.$('rt-eta');
    if (etaEl) etaEl.textContent = etaText;
    if (resultEtaEl) resultEtaEl.textContent = etaText;
  }

  renderResultTimers() {
    const elapsed = this.state.localElapsedSeconds || 0;
    this.setText('rt-elapsed', this.formatDuration(elapsed));
    this.setText('rt-eta', this.etaDisplayText());
  }

  renderProgress(progress) {
    this.state.lastProgress = progress;
    if (progress.started_at_epoch_ms) {
      this.state.progressStartedAtMs = Number(progress.started_at_epoch_ms);
      if (!this.state.elapsedTimer && !progress.done) this.startElapsedTimer();
    }
    this.updateEtaDeadline(progress);

    const pct = Math.max(0, Math.min(100, Number(progress.progress_percent ?? progress.percent ?? 0)));
    const pctEl = this.$('progress-pct');
    if (pctEl) pctEl.textContent = `${Math.round(pct)}%`;
    const barEl = this.$('progress-bar');
    if (barEl) barEl.style.width = `${pct}%`;
    const stage = progress.stage || progress.phase;
    const phase = progress.phase || stage;
    const stageLabelEl = this.$('progress-stage-label');
    if (stageLabelEl) stageLabelEl.textContent = this.stageLabel(stage);
    const msgEl = this.$('progress-message');
    if (msgEl) msgEl.textContent = progress.statusText || progress.status_text || progress.message || '';
    
    const elapsedEl = this.$('elapsedText');
    const etaEl = this.$('etaText');
    if (elapsedEl && this.state.progressStartedAtMs) {
      const seconds = Math.floor((Date.now() - Number(this.state.progressStartedAtMs)) / 1000);
      this.state.localElapsedSeconds = Math.max(0, seconds);
      elapsedEl.textContent = this.formatDuration(this.state.localElapsedSeconds);
    } else if (elapsedEl) {
      elapsedEl.textContent = progress.elapsed_seconds != null ? this.formatDuration(progress.elapsed_seconds) : '00:00';
    }
    if (etaEl) {
      etaEl.textContent = this.etaDisplayText();
    }

    const foundEl = this.$('pm-found');
    if (foundEl) foundEl.textContent = progress.foundCount ?? progress.found ?? 0;
    const validEl = this.$('pm-valid');
    if (validEl) validEl.textContent = progress.valid ?? 0;
    const targetEl = this.$('pm-target');
    if (targetEl) targetEl.textContent = progress.targetCount ?? progress.target ?? '-';
    
    if (this.state.progressStartedAtMs) {
      this.renderLiveTimers();
    } else {
      const pmElapsedEl = this.$('pm-elapsed');
      if (pmElapsedEl) pmElapsedEl.textContent = progress.elapsed_seconds != null ? this.formatDuration(progress.elapsed_seconds) : '-';
      const pmEtaEl = this.$('pm-eta');
      if (pmEtaEl) pmEtaEl.textContent = this.etaDisplayText();
    }
    const engineEl = this.$('pm-engine');
    if (engineEl) engineEl.textContent = `${progress.engine_mode || 'auto'} / ${progress.active_engine || 'none'}`;
    const attemptEl = this.$('pm-attempt');
    if (attemptEl) attemptEl.textContent = `${progress.attempt || 1}/${progress.max_attempts || 1}`;
    this.updateStagePipeline(phase, pct);
    this.renderProgressLogs(progress.logs || []);

    if (!progress.done && !this._progressAnimationStarted) {
      this._progressAnimationStarted = true;
      this.startProgressAnimation();
    }
    if (progress.done) {
      this.stopProgressAnimation();
      this._progressAnimationStarted = false;
    }
  }

  renderProgressLogs(logs) {
    const el = this.$('progress-log');
    if (!el) return;
    const visible = [...(logs || [])].slice(-8).reverse();
    if (!visible.length) {
      el.innerHTML = '<div class="progress-log-empty">Menunggu aktivitas...</div>';
      return;
    }
    el.innerHTML = '';
    visible.forEach((item) => {
      const row = document.createElement('div');
      row.className = 'progress-log-row';
      const stage = document.createElement('span');
      stage.className = 'progress-log-stage';
      stage.textContent = this.stageLabel(item.stage || 'preparing');
      const message = document.createElement('span');
      message.className = 'progress-log-message';
      message.textContent = item.message || '';
      row.append(stage, message);
      el.appendChild(row);
    });
  }

  stageLabel(stage) {
    const labels = {
      idle: 'Idle',
      preparing: 'Preparing',
      scraping: 'Scraping',
      completed: 'Completed',
      blocked: 'Blocked',
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
      ai_filtering: 'AI Orchestrator',
      ranking: 'Ranking',
      recommendation_building: 'Recommendations',
      finalizing: 'Finalizing',
      done: 'Completed',
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
    this.state.products = (data.data || []).map((product) => this.normalizeProduct(product));
    window.__MARKETSPY_PRODUCTS__ = this.state.products;
    this.state.recommendations = data.recommendations || {};
    this.state.metadata = data.result_metadata || {};
    this.state.engineMode = data.engine_mode || 'auto';
    this.state.metadata.engine_mode = this.state.engineMode;
    this.state.sortMode = data.sort_mode || this.state.metadata.sort_mode || this.state.sortMode || 'terbaik';
    this.state.recommendationsOpen = true;
    this.state.recommendationMode = 'terbaik';
    this.state.hasUserSelectedRecommendation = false;
    this.state.autoExpandedOnce = false;

    this.applySortMode(this.state.sortMode, false);
    this.renderResultSummary(data);
    this.renderResultTimers();
    this.renderBudgetBar(data.budget_info);
    this.renderComparison(data);
    this.renderResultWarning(data);
    this.renderRecommendations();
    this.updateResultCount();
    this.renderProducts();
    this.observeRecommendationStage();
    this.animateResultsEntrance();
  }

  normalizeProduct(product) {
    const item = { ...(product || {}) };
    const priceNumber = Number(item.priceNumber ?? item.price_value ?? item.price_val ?? 0) || 0;
    const confidenceScore = Number(item.confidenceScore ?? item.confidence ?? item.relevance_score ?? item.ai_confidence ?? 0) || 0;
    const imageUrl = this.resolveProductImage(item);
    return {
      ...item,
      id: String(item.id || item.url || item.product_url || item.title || ''),
      title: item.title || 'Produk Tokopedia',
      price: item.price || item.price_raw || item.price_text || (priceNumber ? this.formatRupiah(priceNumber) : ''),
      priceNumber,
      price_value: priceNumber,
      image_url: imageUrl,
      image: imageUrl || '',
      has_image: Boolean(imageUrl),
      storeName: item.storeName || item.shop_name || item.shop || item.store || '',
      rating: item.rating || 0,
      soldCount: Number(item.soldCount ?? item.sold_count ?? 0) || 0,
      sold_count: Number(item.sold_count ?? item.soldCount ?? 0) || 0,
      url: item.url || item.product_url || '#',
      source: item.source || item.source_engine || 'tokopedia',
      confidenceScore,
      relevanceReason: item.relevanceReason || item.ai_reason || item.reason || item.ai_explanation || '',
    };
  }

  renderResultWarning(data) {
    const box = this.$('r-warning');
    if (!box) return;
    const meta = data.result_metadata || this.state.metadata || {};
    const requested = Number(meta.requested_count ?? data.requested_count ?? data.target_count ?? 0);
    const displayed = this.state.products.length || Number(meta.displayed_count ?? data.displayed_count ?? 0);
    const shortage = requested > displayed && displayed > 0
      ? `Diminta ${requested}, tersedia ${displayed} produk sesuai budget.`
      : '';
    const warning = String(data.ai_warning || meta.ai_warning || data.limited_reason || meta.limited_reason || shortage || '').trim();
    if (!warning) {
      box.classList.add('hidden');
      box.textContent = '';
      return;
    }
    box.textContent = warning;
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

    const engine_mode = data.engine_mode || this.state.engineMode || this.state.metadata.engine_mode || 'auto';
    const runs = data.engine_runs || this.state.comparison;
    
    if (engine_mode !== 'compare_both' || !runs || !runs.length) {
      panel.classList.add('hidden');
      grid.innerHTML = '';
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
          <span>Semantic checked: <b>${item.result_metadata?.semantic_checked ?? 0}</b></span>
          <span>AI checked: <b>${item.result_metadata?.classifier_checked ?? item.result_metadata?.ai_checked ?? 0}</b></span>
          <span>AI accepted: <b>${item.ai_accepted_count ?? item.result_metadata?.ai_accepted_count ?? 0}</b></span>
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
    this.state.products = (item.data || item.products || []).map((product) => this.normalizeProduct(product));
    window.__MARKETSPY_PRODUCTS__ = this.state.products;
    this.state.recommendations = item.recommendations || {};
    this.state.metadata = item.result_metadata || {};
    this.state.recommendationsOpen = true;
    this.state.recommendationMode = 'terbaik';
    this.renderComparison({ engine_mode: this.state.engineMode, engine_runs: this.state.comparison });
    this.renderRecommendations();
    this.renderResultSummary(item);
    this.renderResultTimers();
    this.renderResultWarning({
      limited_reason: this.state.metadata.limited_reason,
      ai_warning: item.ai_warning || '',
      result_metadata: this.state.metadata,
    });
    this.updateResultCount();
    this.renderProducts();
    this.observeRecommendationStage();
    this.animateResultsEntrance();
  }

  renderResultSummary(data) {
    const meta = data.result_metadata || this.state.metadata || {};
    const requested = Number(meta.requested_count ?? data.requested_count ?? data.target_count ?? 0);
    const productCount = Array.isArray(data.data || data.products) ? (data.data || data.products).length : this.state.products.length;
    const displayed = productCount;
    const raw = Number(meta.raw_scraped_count ?? meta.raw_scraped ?? data.raw_count ?? 0);
    const deduped = Number(meta.deduped_count ?? data.deduped_count ?? 0);
    const budget = Number(meta.budget_valid_count ?? data.budget_valid_count ?? data.budget_count ?? 0);
    const semanticChecked = Number(meta.semantic_checked ?? meta.semantic_checked_count ?? 0);
    const aiChecked = Number(meta.classifier_checked ?? meta.ai_checked ?? data.ai_checked ?? 0);
    const aiAccepted = Number(meta.ai_accepted ?? meta.ai_accepted_count ?? data.ai_accepted_count ?? 0);
    const aiCallsAttempted = Number(meta.ai_calls_attempted ?? 0);
    const aiCallsSucceeded = Number(meta.ai_calls_succeeded ?? 0);

    this.setText('r-count', displayed || this.state.products.length || 0);
    this.setText('r-target', requested || '-');
    this.setText('rs-requested', requested || 0);
    this.setText('rs-raw', raw || 0);
    this.setText('rs-deduped', deduped || 0);
    this.setText('rs-budget', budget || 0);
    this.setText('rs-semantic', semanticChecked || 0);
    this.setText('rs-ai-checked', aiChecked || 0);
    this.setText('rs-ai', aiAccepted || 0);
    this.setText('rs-ai-calls', `${aiCallsSucceeded || 0}/${aiCallsAttempted || 0}`);
    this.setText('rs-displayed', displayed || this.state.products.length || 0);
    const status = this.$('result-status-badge');
    if (status) {
      status.textContent = displayed >= requested ? 'Target met' : 'Partial';
      status.className = `status-badge ${displayed >= requested ? 'status-done' : 'status-running'}`;
    }
  }

  renderRecommendations() {
    const panel = this.$('recommendations-panel');
    const grid = this.$('recommendation-stage-grid');
    const tabs = this.$('recommendation-tabs');
    const title = this.$('recommendationTitle');
    if (!panel || !grid || !tabs || !title) return;

    if (!this.state.products.length) {
      panel.classList.add('hidden');
      grid.innerHTML = '';
      tabs.innerHTML = '';
      return;
    }

    panel.classList.remove('hidden');
    const activeMode = this.state.recommendationMode || 'terbaik';
    const buckets = this.buildRecommendationBuckets();
    const activeMeta = RECOMMENDATION_MODES.find((mode) => mode.key === activeMode) || RECOMMENDATION_MODES[0];
    title.textContent = activeMeta.label;

    tabs.innerHTML = '';
    for (const mode of RECOMMENDATION_MODES) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `recommendation-tab ${mode.key === activeMode ? 'active' : ''}`;
      btn.dataset.recommendationMode = mode.key;
      btn.setAttribute('role', 'tab');
      btn.setAttribute('aria-selected', String(mode.key === activeMode));
      btn.innerHTML = `<span>${this.esc(mode.icon)}</span>${this.esc(mode.label)}`;
      btn.addEventListener('click', () => this.selectRecommendation(mode.key));
      tabs.appendChild(btn);
    }

    const inactive = RECOMMENDATION_MODES.filter((mode) => mode.key !== activeMode);
    const panelOrder = [inactive[0], activeMeta, inactive[1]].filter(Boolean);
    grid.innerHTML = '';
    for (const mode of panelOrder) {
      const stagePanel = this.createRecommendationPanel(mode, buckets[mode.key] || [], mode.key === activeMode);
      grid.appendChild(stagePanel);
    }
  }

  buildRecommendationBuckets() {
    const list = [...this.state.products];
    const number = (value) => {
      const parsed = Number(String(value ?? 0).replace(',', '.'));
      return Number.isFinite(parsed) ? parsed : 0;
    };
    const price = (p) => {
      const value = number(p.priceNumber ?? p.price_value ?? p.price);
      return value > 0 ? value : Number.MAX_SAFE_INTEGER;
    };
    const rating = (p) => number(p.rating);
    const confidence = (p) => number(p.confidenceScore ?? p.confidence ?? p.relevance_score ?? p.ai_confidence);
    const semantic = (p) => number(p.semantic_score);
    const sold = (p) => number(p.soldCount ?? p.sold_count);
    const storeTrust = (p) => {
      if (p.store_trust_score != null) return number(p.store_trust_score);
      const shop = String(p.storeName || p.shop_name || p.shop || '').toLowerCase();
      return /(official|mall|power merchant|pro)/.test(shop) ? 2 : shop ? 1 : 0;
    };

    return {
      terbaik: [...list].sort((a, b) =>
        rating(b) - rating(a)
        || confidence(b) - confidence(a)
        || sold(b) - sold(a)
        || semantic(b) - semantic(a)
      ).slice(0, 6),
      termurah: [...list].sort((a, b) =>
        price(a) - price(b)
        || rating(b) - rating(a)
      ).slice(0, 6),
      trusted: [...list].sort((a, b) =>
        storeTrust(b) - storeTrust(a)
        || sold(b) - sold(a)
        || rating(b) - rating(a)
        || confidence(b) - confidence(a)
      ).slice(0, 6),
    };
  }

  createRecommendationPanel(mode, products, active) {
    const panel = document.createElement('div');
    panel.className = `recommendation-panel ${active ? 'is-active' : 'is-side'}`;
    panel.dataset.recommendationMode = mode.key;
    if (!active) {
      panel.setAttribute('role', 'button');
      panel.tabIndex = 0;
      panel.addEventListener('click', () => this.selectRecommendation(mode.key));
      panel.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          this.selectRecommendation(mode.key);
        }
      });
    }

    const head = document.createElement('div');
    head.className = 'recommendation-panel-head';
    head.innerHTML = `
      <span class="recommendation-panel-icon">${this.esc(mode.icon)}</span>
      <span class="recommendation-panel-label">${this.esc(mode.label)}</span>
      <span class="recommendation-panel-count">${products.length} produk</span>
    `;
    panel.appendChild(head);

    if (!active) {
      const preview = products[0];
      const previewTitle = preview?.title || 'Belum ada produk';
      const previewPrice = preview?.price || preview?.price_text || '';
      const side = document.createElement('div');
      side.className = 'recommendation-side-preview';
      side.innerHTML = `<strong>${this.esc(previewTitle)}</strong><span>${this.esc(previewPrice)}</span>`;
      panel.appendChild(side);
      return panel;
    }

    const body = document.createElement('div');
    body.className = 'recommendation-mini-grid';
    if (!products.length) {
      const empty = document.createElement('div');
      empty.className = 'recommendation-empty';
      empty.textContent = 'Belum cukup data untuk rekomendasi ini.';
      body.appendChild(empty);
    } else {
      products.forEach((product) => body.appendChild(this.createRecommendationMiniCard(product)));
    }
    panel.appendChild(body);
    return panel;
  }

  createRecommendationMiniCard(product) {
    const item = this.normalizeProduct(product);
    const card = document.createElement('div');
    card.className = 'recommendation-product-card product-card';
    const id = String(item.id || item.url || item.product_url || item.title || '');
    card.dataset.productId = id;
    card.dataset.id = id;

    const img = document.createElement('img');
    const imageUrl = this.resolveProductImage(item);
    img.src = imageUrl || '';
    img.alt = item.title || 'Product image';
    img.loading = 'lazy';
    img.onerror = () => {
      if (imageUrl && !img.dataset.proxyTried) {
        img.dataset.proxyTried = '1';
        img.src = this.proxyImageUrl(imageUrl);
      }
    };

    const details = document.createElement('div');
    const h4 = document.createElement('h4');
    h4.textContent = item.title || 'Produk Tokopedia';
    const strong = document.createElement('strong');
    strong.textContent = item.price || '';
    const span = document.createElement('span');
    const ratingStr = item.rating ? `Rating ${item.rating}` : '';
    const soldStr = item.sold || item.sold_text || item.soldCount || item.sold_count || '';
    span.textContent = [ratingStr, soldStr].filter(Boolean).join(' | ');

    details.append(h4, strong, span);
    card.append(img, details);

    card.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      this.openRecommendationProductModal(item, card);
    });

    return card;
  }

  createSmallImagePlaceholder(text) {
    const placeholder = document.createElement('div');
    placeholder.className = 'recommendation-img-placeholder';
    placeholder.textContent = text;
    return placeholder;
  }

  toggleRecommendations() {
    this.state.recommendationsOpen = true;
    this.renderRecommendations();
    this.expandRecommendationStage(true);
  }

  selectRecommendation(mode) {
    if (!RECOMMENDATION_MODES.some((item) => item.key === mode)) return;
    if (this.state.recommendationMode === mode && this.state.hasUserSelectedRecommendation) return;
    if (this.recommendationTransitionRunning) return;
    this.state.hasUserSelectedRecommendation = true;
    this.recommendationTransitionRunning = true;

    const nextMode = mode;
    const stage = document.querySelector(".recommendation-stage");
    const activePanel = document.querySelector(".recommendation-panel.is-active");
    const title = document.querySelector(".recommendation-active-title");
    const cards = document.querySelectorAll(".recommendation-product-card");
    const clickedButton = document.querySelector(`[data-recommendation-mode="${nextMode}"]`);

    const tl = window.anime.timeline({
      easing: "easeOutExpo",
      complete: () => {
        this.state.recommendationMode = nextMode;

        // Update content
        this.renderRecommendations();
        const modeMeta = RECOMMENDATION_MODES.find((m) => m.key === nextMode);
        if (modeMeta) {
          this.applySortMode(modeMeta.sortMode, false);
          this.renderProducts();
          this.animateProductCards();
          this.updateResultCount();
        }

        // Animate in new cards and title
        window.anime({
          targets: ".recommendation-product-card",
          opacity: [0, 1],
          translateY: [26, 0],
          scale: [0.92, 1],
          delay: window.anime.stagger(55),
          duration: 750,
          easing: "easeOutExpo"
        });

        window.anime({
          targets: "#recommendationTitle",
          opacity: [0, 1],
          translateY: [18, 0],
          scale: [0.94, 1],
          duration: 650,
          easing: "easeOutExpo"
        });

        window.anime({
          targets: ".recommendation-panel.is-active",
          scale: [1.04, 1],
          duration: 650,
          easing: "easeOutExpo",
          complete: () => {
            this.recommendationTransitionRunning = false;
          }
        });
      }
    });

    if (cards.length) {
      tl.add({
        targets: cards,
        opacity: [1, 0],
        translateY: [0, 18],
        scale: [1, 0.94],
        delay: window.anime.stagger(35, { direction: "reverse" }),
        duration: 360
      });
    }

    if (title) {
      tl.add({
        targets: title,
        opacity: [1, 0],
        translateY: [0, -16],
        scale: [1, 0.92],
        duration: 320
      }, "-=260");
    }

    if (clickedButton) {
      tl.add({
        targets: clickedButton,
        scale: [1, 1.12, 1.04],
        duration: 520
      }, "-=220");
    }

    if (activePanel) {
      tl.add({
        targets: activePanel,
        scale: [1, 1.08],
        translateY: [0, -10],
        boxShadow: [
          "0 0 0 rgba(96,165,250,0)",
          "0 28px 90px rgba(96,165,250,0.24)"
        ],
        duration: 620
      }, "-=300");
    }

    const sidePanels = document.querySelectorAll(".recommendation-panel.is-side");
    if (sidePanels.length) {
      tl.add({
        targets: sidePanels,
        opacity: [1, 0.65],
        scale: [1, 0.94],
        translateX: function(el, i) {
          return i === 0 ? [-0, -26] : [0, 26];
        },
        duration: 520
      }, "-=520");
    }
  }

  animateRecommendationStage() {
    if (!this.canAnimate()) return;
    window.anime.remove?.('.recommendation-panel, .recommendation-product-card, .recommendation-tab');
    window.anime({
      targets: '.recommendation-panel',
      opacity: [0, 1],
      translateY: [24, 0],
      scale: [0.96, 1],
      delay: window.anime.stagger(70),
      duration: 650,
      easing: 'easeOutExpo',
    });
    window.anime({
      targets: '.recommendation-product-card',
      opacity: [0, 1],
      translateY: [18, 0],
      scale: [0.94, 1],
      delay: window.anime.stagger(45),
      duration: 680,
      easing: 'easeOutExpo',
    });
  }

  observeRecommendationStage() {
    if (this.recommendationObserver) this.recommendationObserver.disconnect();
    const panel = this.$('recommendations-panel');
    if (!panel || !('IntersectionObserver' in window)) return;
    this.recommendationObserver = new IntersectionObserver((entries) => {
      const entry = entries[0];
      if (
        entry?.isIntersecting
        && entry.intersectionRatio >= 0.45
        && !this.state.hasUserSelectedRecommendation
        && !this.state.autoExpandedOnce
      ) {
        this.state.autoExpandedOnce = true;
        this.expandRecommendationStage(false);
      }
    }, { threshold: [0, 0.45, 0.7] });
    this.recommendationObserver.observe(panel);
  }

  expandRecommendationStage(fromUser) {
    const stage = this.$('recommendation-stage');
    if (!stage) return;
    if (fromUser) this.state.hasUserSelectedRecommendation = true;
    stage.classList.add('is-auto-expanded');
    if (!this.canAnimate()) return;

    const startHeight = stage.offsetHeight;
    stage.style.height = `${startHeight}px`;
    const endHeight = stage.scrollHeight;
    window.anime({
      targets: stage,
      height: [startHeight, endHeight],
      scale: [0.98, 1],
      duration: 650,
      easing: 'easeOutExpo',
      complete: () => {
        stage.style.height = '';
      },
    });
    this.animateRecommendationStage();
  }

  animateResultsEntrance() {
    if (!this.canAnimate()) return;
    window.anime.remove?.('.result-stat-card, .quick-sort-btn, .product-card');
    window.anime({
      targets: '.result-stat-card',
      opacity: [0, 1],
      translateY: [24, 0],
      scale: [0.96, 1],
      delay: window.anime.stagger(60),
      duration: 650,
      easing: 'easeOutExpo',
    });
    window.anime({
      targets: '.quick-sort-btn, .recommendation-tab',
      opacity: [0, 1],
      translateY: [14, 0],
      scale: [0.96, 1],
      delay: window.anime.stagger(45),
      duration: 520,
      easing: 'easeOutExpo',
    });
    window.anime({
      targets: '.product-card',
      opacity: [0, 1],
      translateY: [30, 0],
      scale: [0.94, 1],
      delay: window.anime.stagger(45),
      duration: 700,
      easing: 'easeOutExpo',
    });
    this.animateRecommendationStage();
  }

  updateResultCount() {
    const meta = this.state.metadata || {};
    const displayed = this.state.products.length;
    const requested = Number(meta.requested_count ?? this.$('r-target')?.textContent ?? displayed);
    this.setText('r-count', displayed || this.state.products.length);
    this.setText('r-target', requested || '-');
    this.setText('rs-displayed', displayed || this.state.products.length);
  }

  renderProducts() {
    const grid = this.$('products-grid');
    grid.innerHTML = '';
    if (!this.state.products.length) {
      grid.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">?</div>
          <strong>Tidak ada produk valid untuk pilihan ini.</strong>
          <span>Coba naikkan toleransi budget, kurangi filter, atau aktifkan target-first mode.</span>
        </div>
      `;
      return;
    }
    for (const product of this.state.products) {
      grid.appendChild(this.createCard(product));
    }
  }

  activeSortMode() {
    return document.querySelector('.quick-sort-btn.active')?.dataset.sortMode || this.state.sortMode || 'terbaik';
  }

  setSortMode(mode) {
    if (!this.state.products.length) {
      this.showToast('Belum ada hasil untuk diurutkan');
      this.applySortMode(mode, false);
      return;
    }
    this.applySortMode(mode, true);
  }

  applySortMode(mode, rerender) {
    const nextMode = ['most_trusted', 'termurah', 'terbaik'].includes(mode) ? mode : 'terbaik';
    this.state.sortMode = nextMode;
    document.querySelectorAll('[data-sort-mode]').forEach((btn) => {
      btn.classList.toggle('active', btn.dataset.sortMode === nextMode);
    });
    this.state.products = this.sortProducts(this.state.products, nextMode);
    window.__MARKETSPY_PRODUCTS__ = this.state.products;
    if (rerender) {
      this.renderProducts();
      this.animateProductCards();
      this.renderRecommendations();
      this.updateResultCount();
    }
  }

  animateProductCards() {
    if (!this.canAnimate()) return;
    window.anime.remove?.('.product-card');
    window.anime({
      targets: '.product-card',
      opacity: [0, 1],
      translateY: [30, 0],
      scale: [0.94, 1],
      delay: window.anime.stagger(45),
      duration: 700,
      easing: 'easeOutExpo',
    });
  }

  sortProducts(products, mode) {
    const list = [...(products || [])];
    const safeNumber = (value) => {
      const parsed = Number(String(value ?? 0).replace(',', '.'));
      return Number.isFinite(parsed) ? parsed : 0;
    };
    const price = (p) => {
      const value = safeNumber(p.priceNumber ?? p.price_value ?? p.price);
      return value > 0 ? value : Number.MAX_SAFE_INTEGER;
    };
    const relevance = (p) => safeNumber(p.confidenceScore ?? p.confidence ?? p.relevance_score ?? p.ai_confidence);
    const rating = (p) => safeNumber(p.rating);
    const sold = (p) => safeNumber(p.soldCount ?? p.sold_count);
    const review = (p) => safeNumber(p.review_count);
    const trust = (p) => {
      if (p.store_trust_score != null) return safeNumber(p.store_trust_score);
      const shop = String(p.storeName || p.shop_name || p.shop || '').toLowerCase();
      const shopBoost = /(official|mall|power merchant|pro)/.test(shop) ? 1 : shop ? 0.5 : 0;
      return shopBoost + rating(p) / 5 + Math.min(sold(p), 1000) / 1000 + Math.min(review(p), 1000) / 2000;
    };
    if (mode === 'termurah') {
      return list.sort((a, b) =>
        price(a) - price(b)
        || relevance(b) - relevance(a)
        || rating(b) - rating(a)
      );
    }
    if (mode === 'most_trusted') {
      return list.sort((a, b) =>
        trust(b) - trust(a)
        || rating(b) - rating(a)
        || sold(b) - sold(a)
        || review(b) - review(a)
      );
    }
    return list.sort((a, b) =>
      relevance(b) - relevance(a)
      || rating(b) - rating(a)
      || sold(b) - sold(a)
      || price(a) - price(b)
    );
  }

  resolveProductImage(product) {
    const candidates = [
      product?.image_url,
      product?.image,
      product?.thumbnail,
      product?.thumb,
      product?.img,
      product?.photo,
      Array.isArray(product?.images) ? product.images[0] : null,
      product?.media?.image,
      product?.media?.thumbnail,
      product?.media?.url,
    ];

    for (const value of candidates) {
      if (!value) continue;
      let url = String(value).trim();
      if (!url) continue;
      if (url.startsWith('//')) url = `https:${url}`;
      if (!/^https?:\/\//i.test(url)) continue;
      if (['undefined', 'null', 'noimage'].includes(url.toLowerCase().replace(/\s+/g, ''))) continue;
      return url;
    }

    return null;
  }

  getValidImageUrl(product) {
    return this.resolveProductImage(product);
  }

  proxyImageUrl(imageUrl) {
    return `/api/image-proxy?url=${encodeURIComponent(imageUrl)}`;
  }

  createImagePlaceholder(text) {
    const placeholder = document.createElement('div');
    placeholder.className = 'product-image-placeholder';
    const icon = document.createElement('span');
    icon.textContent = 'No image';
    const label = document.createElement('small');
    label.textContent = text;
    placeholder.append(icon, label);
    return placeholder;
  }

  createProductImage(product) {
    const wrapper = document.createElement('div');
    wrapper.className = 'product-image-wrap';
    const imageUrl = this.resolveProductImage(product);
    if (!imageUrl) {
      wrapper.appendChild(this.createImagePlaceholder('Gambar tidak tersedia'));
      return wrapper;
    }

    const img = document.createElement('img');
    img.className = 'product-image';
    img.src = imageUrl;
    img.alt = product.title || 'Product image';
    img.loading = 'lazy';
    img.onerror = () => {
      if (!img.dataset.proxyTried) {
        img.dataset.proxyTried = '1';
        img.src = this.proxyImageUrl(imageUrl);
        return;
      }
      wrapper.replaceChildren(this.createImagePlaceholder('Gambar gagal dimuat'));
    };
    wrapper.appendChild(img);
    return wrapper;
  }

  appendText(parent, className, text, tagName = 'div') {
    if (text == null || text === '') return null;
    const el = document.createElement(tagName);
    el.className = className;
    el.textContent = String(text);
    parent.appendChild(el);
    return el;
  }

  createBadge(text) {
    const badge = document.createElement('span');
    badge.className = 'product-badge';
    badge.textContent = text;
    return badge;
  }

  createCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    const id = String(product.id || product.url || product.title || '');
    card.dataset.productId = id;
    card.dataset.id = id;

    const title = product.title || 'Produk Tokopedia';
    const url = product.url || '#';
    const numericPrice = product.priceNumber ?? product.price_value ?? product.price;
    const priceText = product.price || (Number(numericPrice) > 0
      ? this.formatRupiah(numericPrice)
      : (product.price_text || product.price_raw || 'Harga tidak tersedia'));
    const soldText = product.sold || product.sold_text || product.soldCount || product.sold_count || '';
    const shopName = product.storeName || product.shop || product.shop_name || '';
    const shopLocation = product.location || product.shop_location || '';
    const aiValue = product.confidenceScore ?? product.ai_confidence ?? product.relevance_score;
    const aiNumeric = Number(aiValue);
    const aiConfidenceLabel = product.ai_confidence_label
      || (aiNumeric >= 0.85 ? 'High' : aiNumeric >= 0.70 ? 'Medium' : 'Low');
    const aiLabel = product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan');
    const aiReason = product.relevanceReason || product.ai_confidence_explanation || product.ai_explanation || product.ai_reason || '';

    // Append image wrapper directly to card (no wrapping <a>)
    card.appendChild(this.createProductImage(product));

    const body = document.createElement('div');
    body.className = 'product-body';
    this.appendText(body, 'product-title', title);
    this.appendText(body, 'product-price', priceText);

    const meta = document.createElement('div');
    meta.className = 'product-meta';
    if (product.rating) this.appendText(meta, 'product-rating', `Rating ${product.rating}`, 'span');
    if (soldText) this.appendText(meta, 'product-sold', String(soldText), 'span');
    if (shopName) this.appendText(meta, 'product-shop', shopName, 'span');
    if (shopLocation) this.appendText(meta, 'product-location', shopLocation, 'span');
    body.appendChild(meta);

    const badges = document.createElement('div');
    badges.className = 'product-badges';
    if (aiValue != null && Number.isFinite(aiNumeric)) {
      badges.appendChild(this.createBadge(`AI ${aiNumeric.toFixed(2)} ${aiConfidenceLabel}`));
    }
    const learnedAdjustment = Number(product.learned_adjustment ?? 0);
    if (Number.isFinite(learnedAdjustment) && Math.abs(learnedAdjustment) > 0) {
      const sign = learnedAdjustment > 0 ? '+' : '';
      badges.appendChild(this.createBadge(`Learned ${sign}${learnedAdjustment.toFixed(2)}`));
    }
    badges.appendChild(this.createBadge(product.ai_source || product.decision_source || 'rule'));
    if (product.source || product.source_engine) badges.appendChild(this.createBadge(product.source || product.source_engine));
    if (product.outside_budget || product.budget_badge) badges.appendChild(this.createBadge(product.budget_badge || 'Di luar budget'));
    body.appendChild(badges);

    const labelLine = document.createElement('div');
    labelLine.className = 'ai-line';
    labelLine.appendChild(this.createBadge(aiLabel));
    (product.ai_categories || []).slice(0, 3).forEach((cat) => labelLine.appendChild(this.createBadge(cat)));
    body.appendChild(labelLine);

    if (aiReason) this.appendText(body, 'ai-reason', aiReason);

    const actionsBox = document.createElement('div');
    actionsBox.className = 'product-card-actions';

    const correctBtn = document.createElement('button');
    correctBtn.className = 'card-action-btn is-correct';
    correctBtn.dataset.feedbackCorrect = 'true';
    correctBtn.dataset.noModal = 'true';
    correctBtn.textContent = 'Benar';
    correctBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      this._submitFeedback(id, {
        userAction: 'benar',
        feedbackType: 'positive',
        selectedReasons: [],
        customReason: '',
        correctedLabel: 'relevan',
      });
    });

    const wrongBtn = document.createElement('button');
    wrongBtn.className = 'card-action-btn is-wrong';
    wrongBtn.dataset.feedbackWrong = 'true';
    wrongBtn.dataset.noModal = 'true';
    wrongBtn.textContent = 'Salah';
    wrongBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      this.openProductModal(product, card);
      this.revealReasonPanel();
    });

    const openBtn = document.createElement('a');
    openBtn.className = 'card-action-btn is-open';
    openBtn.dataset.noModal = 'true';
    openBtn.href = url || '#';
    openBtn.target = '_blank';
    openBtn.rel = 'noopener noreferrer';
    openBtn.textContent = 'Buka Produk';
    openBtn.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    actionsBox.append(correctBtn, wrongBtn, openBtn);
    body.appendChild(actionsBox);

    card.appendChild(body);

    return card;
  }

  openProductModal(product, cardEl) {
    const dialog = document.querySelector("#product-feedback-dialog");
    if (!dialog || this.isModalAnimating) return;

    this.activeProduct = product;
    this.activeProductCard = cardEl;

    this.fillProductModal(product);

    const reasonPanel = dialog.querySelector(".feedback-reason-panel");
    if (reasonPanel) reasonPanel.hidden = true;

    dialog.showModal();
    this.isModalAnimating = true;

    window.anime({
      targets: ".product-modal-card",
      opacity: [0, 1],
      translateY: [48, 0],
      scale: [0.92, 1],
      duration: 1000,
      easing: "easeOutExpo",
      complete: () => {
        this.isModalAnimating = false;
      }
    });

    window.anime({
      targets: ".product-modal-image-wrap",
      opacity: [0, 1],
      translateX: [-40, 0],
      duration: 1000,
      delay: 120,
      easing: "easeOutExpo"
    });

    window.anime({
      targets: ".product-modal-content > *",
      opacity: [0, 1],
      translateX: [32, 0],
      delay: window.anime.stagger(70, { start: 180 }),
      duration: 850,
      easing: "easeOutExpo"
    });
  }

  closeProductModal() {
    const dialog = document.querySelector("#product-feedback-dialog");
    if (!dialog || this.isModalAnimating) return;

    this.isModalAnimating = true;

    window.anime({
      targets: ".product-modal-card",
      opacity: [1, 0],
      translateY: [0, 28],
      scale: [1, 0.94],
      duration: 1000,
      easing: "easeOutExpo",
      complete: () => {
        dialog.close();
        this.activeProduct = null;
        this.activeProductCard = null;
        this.isModalAnimating = false;
      }
    });
  }

  fillProductModal(product) {
    const dialog = document.querySelector("#product-feedback-dialog");
    if (!dialog) return;

    const img = dialog.querySelector(".product-modal-image");
    if (img) {
      const imageUrl = this.resolveProductImage(product);
      img.src = imageUrl || '';
      img.onerror = () => {
        if (imageUrl && !img.dataset.proxyTried) {
          img.dataset.proxyTried = '1';
          img.src = this.proxyImageUrl(imageUrl);
        } else {
          img.src = '';
        }
      };
    }

    dialog.querySelector(".product-modal-title").textContent = product.title || 'Produk';
    dialog.querySelector(".product-modal-store").textContent = product.storeName || product.shop_name || product.shop || '';
    dialog.querySelector(".product-modal-price").textContent = product.price || '';

    const ratingEl = dialog.querySelector(".product-modal-rating");
    if (ratingEl) {
      ratingEl.textContent = product.rating ? `⭐ ${product.rating}` : '';
      ratingEl.style.display = product.rating ? 'inline' : 'none';
    }

    const soldEl = dialog.querySelector(".product-modal-sold");
    if (soldEl) {
      const soldText = product.sold || product.sold_text || product.soldCount || product.sold_count || '';
      soldEl.textContent = soldText ? `🛍️ ${soldText}` : '';
      soldEl.style.display = soldText ? 'inline' : 'none';
    }

    const confEl = dialog.querySelector(".product-modal-confidence");
    if (confEl) {
      const aiValue = product.confidenceScore ?? product.ai_confidence ?? product.relevance_score;
      const aiNumeric = Number(aiValue);
      confEl.textContent = (aiValue != null && Number.isFinite(aiNumeric)) ? `🧠 AI Confidence: ${aiNumeric.toFixed(2)}` : '';
      confEl.style.display = (aiValue != null && Number.isFinite(aiNumeric)) ? 'inline' : 'none';
    }

    const openBtn = dialog.querySelector(".open-product-btn");
    if (openBtn) {
      openBtn.href = product.url || '#';
    }

    const reasonGrid = dialog.querySelector(".feedback-reason-grid");
    if (reasonGrid) {
      reasonGrid.innerHTML = '';
      FEEDBACK_REASONS.forEach((reason) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "feedback-reason-chip";
        chip.dataset.reason = reason;
        chip.textContent = reason;
        chip.addEventListener("click", (e) => {
          e.preventDefault();
          chip.classList.toggle("is-selected");
        });
        reasonGrid.appendChild(chip);
      });
    }

    const noteTextarea = dialog.querySelector(".feedback-note");
    if (noteTextarea) {
      noteTextarea.value = '';
    }
  }

  revealReasonPanel() {
    const panel = document.querySelector(".feedback-reason-panel");
    if (!panel) return;

    panel.hidden = false;

    window.anime({
      targets: ".feedback-reason-panel",
      opacity: [0, 1],
      translateY: [24, 0],
      duration: 650,
      easing: "easeOutExpo"
    });

    window.anime({
      targets: ".feedback-reason-chip",
      opacity: [0, 1],
      translateY: [14, 0],
      scale: [0.94, 1],
      delay: window.anime.stagger(45),
      duration: 650,
      easing: "easeOutExpo"
    });
  }

  bindProductModalEvents() {
    const dialog = document.querySelector("#product-feedback-dialog");
    if (!dialog) return;

    dialog.querySelector("[data-product-modal-close]")?.addEventListener("click", () => {
      this.closeProductModal();
    });

    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) {
        this.closeProductModal();
      }
    });

    dialog.querySelector("[data-feedback-correct]")?.addEventListener("click", async () => {
      if (!this.activeProduct) return;
      const pid = this.activeProduct.id;

      const success = await this._submitFeedback(pid, {
        userAction: 'benar',
        feedbackType: 'positive',
        selectedReasons: [],
        customReason: '',
        correctedLabel: 'relevan',
      });

      if (success) {
        setTimeout(() => {
          this.closeProductModal();
        }, 800);
      }
    });

    dialog.querySelector("[data-feedback-wrong]")?.addEventListener("click", () => {
      this.revealReasonPanel();
    });

    dialog.querySelector("[data-feedback-save]")?.addEventListener("click", async () => {
      if (!this.activeProduct) return;
      const pid = this.activeProduct.id;

      const selectedReasons = Array.from(dialog.querySelectorAll(".feedback-reason-chip.is-selected"))
        .map(chip => chip.dataset.reason);
      const note = dialog.querySelector(".feedback-note")?.value.trim() || '';

      const success = await this._submitFeedback(pid, {
        userAction: 'salah',
        feedbackType: 'negative',
        selectedReasons,
        customReason: note,
        correctedLabel: 'tidak_relevan',
      });

      if (success) {
        this.closeProductModal();
      }
    });

    dialog.querySelector("[data-feedback-reason-cancel]")?.addEventListener("click", () => {
      const panel = dialog.querySelector(".feedback-reason-panel");
      if (panel) panel.hidden = true;
    });
  }

  bindProductCardClick() {
    const isInsideRecommendation = (cardEl) => {
      return Boolean(cardEl.closest(".recommendation-stage"));
    };

    document.addEventListener("click", (event) => {
      const card = event.target.closest(".product-card, .recommendation-product-card");
      if (!card) return;

      const clickedAction = event.target.closest("button, a, [data-no-modal]");
      if (clickedAction) return;

      if (isInsideRecommendation(card)) {
        const productId = card.dataset.productId;
        const product = window.__MARKETSPY_PRODUCTS__?.find(
          item => String(item.id) === String(productId)
        );

        if (!product) return;

        this.openRecommendationProductModal(product, card);
        return;
      }
    });
  }

  openRecommendationProductModal(product, sourceCardEl) {
    const dialog = document.querySelector("#recommendation-product-dialog");
    if (!dialog) return;

    window.__ACTIVE_MODAL_PRODUCT__ = product;
    window.__ACTIVE_MODAL_SOURCE_CARD__ = sourceCardEl;

    this.fillRecommendationProductModal(product);

    const reasonPanel = dialog.querySelector(".modal-feedback-reason-panel");
    if (reasonPanel) reasonPanel.hidden = true;

    dialog.showModal();

    window.anime({
      targets: ".recommendation-modal-card",
      opacity: [0, 1],
      translateY: [50, 0],
      scale: [0.90, 1],
      duration: 1000,
      easing: "easeOutExpo"
    });

    window.anime({
      targets: ".recommendation-modal-image-wrap",
      opacity: [0, 1],
      translateX: [-48, 0],
      scale: [0.96, 1],
      duration: 1000,
      delay: 120,
      easing: "easeOutExpo"
    });

    window.anime({
      targets: ".recommendation-modal-content > *",
      opacity: [0, 1],
      translateX: [36, 0],
      delay: window.anime.stagger(70, { start: 180 }),
      duration: 850,
      easing: "easeOutExpo"
    });
  }

  closeRecommendationProductModal() {
    const dialog = document.querySelector("#recommendation-product-dialog");
    if (!dialog) return;

    window.anime({
      targets: ".recommendation-modal-card",
      opacity: [1, 0],
      translateY: [0, 28],
      scale: [1, 0.94],
      duration: 1000,
      easing: "easeOutExpo",
      complete: () => {
        dialog.close();
        window.__ACTIVE_MODAL_PRODUCT__ = null;
        window.__ACTIVE_MODAL_SOURCE_CARD__ = null;
      }
    });
  }

  fillRecommendationProductModal(product) {
    const dialog = document.querySelector("#recommendation-product-dialog");
    if (!dialog) return;

    const img = dialog.querySelector(".recommendation-modal-image");
    if (img) {
      const imageUrl = this.resolveProductImage(product);
      img.src = imageUrl || '';
      img.onerror = () => {
        if (imageUrl && !img.dataset.proxyTried) {
          img.dataset.proxyTried = '1';
          img.src = this.proxyImageUrl(imageUrl);
        } else {
          img.src = '';
        }
      };
    }

    dialog.querySelector(".recommendation-modal-title").textContent = product.title || 'Produk';
    dialog.querySelector(".recommendation-modal-store").textContent = product.storeName || product.shop_name || product.shop || '';
    dialog.querySelector(".recommendation-modal-price").textContent = product.price || '';

    const ratingEl = dialog.querySelector(".recommendation-modal-rating");
    if (ratingEl) {
      ratingEl.textContent = product.rating ? `⭐ ${product.rating}` : '';
      ratingEl.style.display = product.rating ? 'inline' : 'none';
    }

    const soldEl = dialog.querySelector(".recommendation-modal-sold");
    if (soldEl) {
      const soldText = product.sold || product.sold_text || product.soldCount || product.sold_count || '';
      soldEl.textContent = soldText ? `🛍️ ${soldText}` : '';
      soldEl.style.display = soldText ? 'inline' : 'none';
    }

    const confEl = dialog.querySelector(".recommendation-modal-confidence");
    if (confEl) {
      const aiValue = product.confidenceScore ?? product.ai_confidence ?? product.relevance_score;
      const aiNumeric = Number(aiValue);
      confEl.textContent = (aiValue != null && Number.isFinite(aiNumeric)) ? `🧠 AI Confidence: ${aiNumeric.toFixed(2)}` : '';
      confEl.style.display = (aiValue != null && Number.isFinite(aiNumeric)) ? 'inline' : 'none';
    }

    const openBtn = dialog.querySelector(".open-product-btn");
    if (openBtn) {
      openBtn.href = product.url || '#';
    }

    const reasonGrid = dialog.querySelector(".modal-feedback-reason-grid");
    if (reasonGrid) {
      reasonGrid.innerHTML = '';
      FEEDBACK_REASONS.forEach((reason) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "feedback-reason-chip";
        chip.dataset.reason = reason;
        chip.textContent = reason;
        chip.addEventListener("click", (e) => {
          e.preventDefault();
          chip.classList.toggle("is-selected");
        });
        reasonGrid.appendChild(chip);
      });
    }

    const noteTextarea = dialog.querySelector(".modal-feedback-note");
    if (noteTextarea) {
      noteTextarea.value = '';
    }
  }

  revealModalReasonPanel() {
    const panel = document.querySelector(".modal-feedback-reason-panel");
    const grid = document.querySelector(".modal-feedback-reason-grid");
    if (!panel || !grid) return;

    panel.hidden = false;

    window.anime({
      targets: panel,
      opacity: [0, 1],
      translateY: [24, 0],
      duration: 650,
      easing: "easeOutExpo"
    });

    window.anime({
      targets: ".modal-feedback-reason-grid .feedback-reason-chip",
      opacity: [0, 1],
      translateY: [16, 0],
      scale: [0.94, 1],
      delay: window.anime.stagger(45),
      duration: 650,
      easing: "easeOutExpo"
    });
  }

  bindRecommendationModalEvents() {
    const dialog = document.querySelector("#recommendation-product-dialog");
    if (!dialog) return;

    dialog.querySelector("[data-recommendation-modal-close]")?.addEventListener("click", () => {
      this.closeRecommendationProductModal();
    });

    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) {
        this.closeRecommendationProductModal();
      }
    });

    dialog.querySelector("[data-modal-feedback-correct]")?.addEventListener("click", async () => {
      if (!window.__ACTIVE_MODAL_PRODUCT__) return;
      const pid = window.__ACTIVE_MODAL_PRODUCT__.id;

      const success = await this._submitFeedback(pid, {
        userAction: 'benar',
        feedbackType: 'positive',
        selectedReasons: [],
        customReason: '',
        correctedLabel: 'relevan',
      });

      if (success) {
        setTimeout(() => {
          this.closeRecommendationProductModal();
        }, 800);
      }
    });

    dialog.querySelector("[data-modal-feedback-wrong]")?.addEventListener("click", () => {
      this.revealModalReasonPanel();
    });

    dialog.querySelector("[data-modal-feedback-save]")?.addEventListener("click", async () => {
      if (!window.__ACTIVE_MODAL_PRODUCT__) return;
      const pid = window.__ACTIVE_MODAL_PRODUCT__.id;

      const selectedReasons = Array.from(dialog.querySelectorAll(".modal-feedback-reason-grid .feedback-reason-chip.is-selected"))
        .map(chip => chip.dataset.reason);
      const note = dialog.querySelector(".modal-feedback-note")?.value.trim() || '';

      const success = await this._submitFeedback(pid, {
        userAction: 'salah',
        feedbackType: 'negative',
        selectedReasons,
        customReason: note,
        correctedLabel: 'tidak_relevan',
      });

      if (success) {
        this.closeRecommendationProductModal();
      }
    });

    dialog.querySelector("[data-modal-feedback-cancel]")?.addEventListener("click", () => {
      const panel = dialog.querySelector(".modal-feedback-reason-panel");
      if (panel) panel.hidden = true;
    });
  }

  _learningScopeHint(feedback) {
    const reasons = feedback.selectedReasons || [];
    if ((feedback.feedbackType || '').toLowerCase() === 'positive') return 'exact_query';
    if (reasons.includes('Spesifikasi tidak sesuai query')) return 'query_constraint';
    if (reasons.includes('Cuma aksesoris')) return 'query_intent';
    if (reasons.includes('Bukan sesuai intent pencarian')) return 'query_intent';
    if (reasons.includes('Harga tidak sesuai')) return 'query_constraint';
    if (reasons.includes('Data tidak lengkap')) return 'global';
    if (reasons.includes('Duplikat')) return 'product_fingerprint';
    return 'exact_query';
  }

  async _submitFeedback(productId, feedback) {
    const product = this.state.products.find((p) => String(p.id || p.url || p.title || '') === String(productId));
    if (!product) return;
    const selectedReasons = feedback.selectedReasons || [];
    const learningScopeHint = this._learningScopeHint(feedback);
    const productImage = this.resolveProductImage(product);

    const payload = {
      search_id: this.state.searchId || 'unknown',
      product_id: productId || 'unknown',
      product_title: product.title || '',
      user_action: feedback.userAction,
      feedback_type: feedback.feedbackType || (feedback.userAction === 'benar' ? 'positive' : 'negative'),
      selected_reasons: selectedReasons,
      reasons: selectedReasons,
      custom_reason: feedback.customReason || '',
      note: feedback.customReason || '',
      corrected_label: feedback.correctedLabel,
      ai_label: product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan'),
      ai_confidence: product.confidenceScore ?? product.ai_confidence ?? product.relevance_score ?? 0,
      rule_score: product.rule_score ?? 0,
      semantic_score: product.semantic_score ?? 0,
      combined_score: product.combined_score ?? 0,
      learned_adjustment: product.learned_adjustment ?? 0,
      confidence: product.confidenceScore ?? product.confidence ?? product.ai_confidence ?? product.relevance_score ?? 0,
      learning_scope_hint: learningScopeHint,
      model_used: product._model || product.model_used || '',
      ai_reason: product.relevanceReason || product.ai_reason || product.reason || '',
      sort_mode: this.state.sortMode || 'terbaik',
      decision_source: product.ai_source || product.decision_source || '',
      query_intent: product.query_intent || this.state.metadata.query_intent || '',
      product: {
        id: product.id || '',
        title: product.title || '',
        price_value: product.priceNumber ?? product.price_value ?? 0,
        price: product.priceNumber ?? product.price_value ?? 0,
        store: product.storeName || product.shop_name || product.shop || '',
        url: product.url || product.product_url || '',
        image: product.image || product.image_url || '',
        image_url: productImage,
        has_image: Boolean(productImage),
        product_category: product.product_category || '',
        decision_source: product.ai_source || product.decision_source || '',
        confidence: product.confidenceScore ?? product.confidence ?? product.ai_confidence ?? product.relevance_score ?? 0,
        rule_score: product.rule_score ?? 0,
        semantic_score: product.semantic_score ?? 0,
        combined_score: product.combined_score ?? 0,
        learned_adjustment: product.learned_adjustment ?? 0,
        query_constraints: product.query_constraints || {},
        product_constraints: product.product_constraints || {},
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
        return false;
      }
      const card = Array.from(document.querySelectorAll('.product-card'))
        .find((item) => item.dataset.id === String(productId) || item.dataset.productId === String(productId));
      if (card) {
        card.classList.add('feedback-sent');
        card.title = `Feedback: ${feedback.userAction}`;
        
        if (card.classList.contains('recommendation-product-card')) {
          let badge = card.querySelector('.feedback-accepted-badge');
          if (!badge) {
            badge = document.createElement('span');
            badge.className = 'feedback-accepted-badge product-badge';
            badge.textContent = feedback.feedbackType === 'positive' ? 'Benar' : 'Feedback diterima';
            card.querySelector('div')?.appendChild(badge);
          }
        } else {
          const badges = card.querySelector('.product-badges');
          if (badges && !badges.querySelector('.feedback-accepted-badge')) {
            const badge = this.createBadge(feedback.feedbackType === 'positive' ? 'Benar' : 'Feedback diterima');
            badge.classList.add('feedback-accepted-badge');
            badges.appendChild(badge);
          }
        }

        if (feedback.feedbackType === 'positive') {
          this.animatePositiveFeedback(card);
        }
      }
      this.showToast('Feedback disimpan');
      return true;
    } catch (err) {
      console.error('Feedback error:', err);
      return false;
    }
  }

  animatePositiveFeedback(card) {
    if (!card) return;
    const burst = document.createElement('div');
    burst.className = 'success-burst';
    burst.textContent = 'OK';
    card.appendChild(burst);
    if (!this.canAnimate()) {
      setTimeout(() => burst.remove(), 900);
      return;
    }
    window.anime({
      targets: card,
      scale: [1, 1.03, 1],
      borderColor: ['rgba(148, 163, 184, 0.18)', 'rgba(16, 185, 129, 0.72)'],
      duration: 540,
      easing: 'easeOutExpo',
    });
    window.anime({
      targets: burst,
      opacity: [0, 1, 0],
      translateY: [10, -18],
      scale: [0.8, 1.1, 1],
      duration: 900,
      easing: 'easeOutExpo',
      complete: () => burst.remove(),
    });
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
    this.setStatus(this.isBlockedMessage(message) ? 'Blocked' : 'Error', 'status-error');
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
    if (this.recommendationObserver) this.recommendationObserver.disconnect();
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
  window.openRecommendationProductModal = (product, card) => app.openRecommendationProductModal(product, card);
  window.closeRecommendationProductModal = () => app.closeRecommendationProductModal();
});
