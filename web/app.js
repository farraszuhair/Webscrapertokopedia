/**
 * Tokopedia Scraper frontend controller.
 *
 * Active UI contract:
 * - product cards show only Benar / Salah
 * - Salah opens a modal before POST /api/feedback
 * - recommendations render as one collapsed clickable box
 */

function buildTransformFromParams(params, index) {
  const parts = [];

  if (Array.isArray(params.translateX)) {
    parts.push(`translateX(${params.translateX[index]}px)`);
  }

  if (Array.isArray(params.translateY)) {
    parts.push(`translateY(${params.translateY[index]}px)`);
  }

  if (Array.isArray(params.scale)) {
    const scaleValue = params.scale[index];
    parts.push(`scale(${typeof scaleValue === "number" ? scaleValue : 1})`);
  }

  if (Array.isArray(params.rotate)) {
    parts.push(`rotate(${params.rotate[index]}deg)`);
  }

  return parts.join(" ") || "none";
}

const AnimeBridge = (() => {
  const animeGlobal = window.anime;
  const activeAnimations = new WeakMap();

  function resolveTargets(targets) {
    if (!targets) return [];
    if (typeof targets === "string") return Array.from(document.querySelectorAll(targets));
    if (targets instanceof Element || targets === window || targets === document) return [targets];
    return Array.from(targets).filter(Boolean);
  }

  function stop(targets) {
    const resolvedTargets = resolveTargets(targets);

    if (animeGlobal && typeof animeGlobal.remove === "function") {
      try {
        animeGlobal.remove(resolvedTargets);
      } catch (_error) {}
    }

    resolvedTargets.forEach(target => {
      const animation = activeAnimations.get(target);
      if (animation && typeof animation.pause === "function") {
        animation.pause();
      }
      activeAnimations.delete(target);
    });

    return resolvedTargets;
  }

  function run(targets, params) {
    if (!targets) return null;

    const resolvedTargets = stop(targets);
    if (!resolvedTargets.length) return null;

    let animation = null;
    const originalComplete = typeof params?.complete === "function" ? params.complete : null;
    const runParams = {
      ...(params || {}),
      complete: (...args) => {
        resolvedTargets.forEach(target => {
          if (activeAnimations.get(target) === animation) {
            activeAnimations.delete(target);
          }
        });

        if (originalComplete) originalComplete(...args);
      }
    };

    if (typeof window.animate === "function") {
      animation = window.animate(resolvedTargets, runParams);
    } else if (animeGlobal && typeof animeGlobal === "function") {
      animation = animeGlobal({ targets: resolvedTargets, ...runParams });
    } else if (animeGlobal && typeof animeGlobal.animate === "function") {
      animation = animeGlobal.animate(resolvedTargets, runParams);
    }

    if (animation) {
      resolvedTargets.forEach(target => activeAnimations.set(target, animation));
      return animation;
    }

    resolvedTargets.forEach(element => {
      if (!element || typeof element.animate !== "function") return;

      const keyframes = [
        {
          opacity: Array.isArray(runParams.opacity) ? runParams.opacity[0] : undefined,
          transform: buildTransformFromParams(runParams, 0)
        },
        {
          opacity: Array.isArray(runParams.opacity) ? runParams.opacity[1] : undefined,
          transform: buildTransformFromParams(runParams, 1)
        }
      ];

      const waapi = element.animate(keyframes, {
        duration: runParams.duration || 300,
        easing: "ease-out",
        fill: "forwards",
        delay: typeof runParams.delay === "function" ? runParams.delay(element, 0) : (runParams.delay || 0)
      });

      activeAnimations.set(element, waapi);
    });

    return null;
  }

  function timeline(params = {}) {
    if (typeof createTimeline === "function") {
      return createTimeline(params);
    }

    if (animeGlobal && typeof animeGlobal.timeline === "function") {
      return animeGlobal.timeline(params);
    }

    return null;
  }

  function stagger(value, params = {}) {
    if (typeof window.stagger === "function") {
      return window.stagger(value, params);
    }

    if (animeGlobal && typeof animeGlobal.stagger === "function" && animeGlobal.stagger.length > 1) {
      return animeGlobal.stagger(value, params);
    }

    return function(_el, index) {
      const start = Number(params.start || 0);
      const step = Array.isArray(value) ? 60 : Number(value || 0);
      const count = Number(params.count || 0);
      let order = index;

      if (count > 1 && params.from === "center") {
        order = Math.abs(index - (count - 1) / 2);
      } else if (count > 1 && params.from === "last") {
        order = count - 1 - index;
      }

      if (count > 1 && params.reversed) {
        order = count - 1 - order;
      }

      return Math.max(0, start + order * step);
    };
  }

  function createLayout(target, params) {
    if (typeof window.createLayout === "function") {
      return window.createLayout(target, params);
    }

    if (animeGlobal && typeof animeGlobal.createLayout === "function") {
      return animeGlobal.createLayout(target, params);
    }

    return null;
  }

  function getSvgUtil() {
    if (window.svg) return window.svg;
    if (animeGlobal && animeGlobal.svg) return animeGlobal.svg;
    return null;
  }

  return { run, timeline, stagger, createLayout, stop, getSvgUtil };
})();

function getRecommendationMotionProfile() {
  const profile = getCategoryMotionProfile();
  return {
    duration: profile.enter,
    zoomScale: 1.01,
    logoScale: profile.cloneScale,
    enterY: 26,
    enterScale: 0.965,
    rotateX: 0,
    staggerDelay: profile.stagger,
    grid: [1, 1]
  };
}

/* ─── Standalone helper functions referenced by ScraperApp ─── */

function handleImageError(img) {
  if (!img) return;
  img.classList.add("is-hidden");
  const wrapper = img.closest(".recommendation-product-image-wrap, .product-detail-media, .product-image-wrap, .product-modal-image-wrap");
  const placeholder = wrapper
    ? wrapper.querySelector(".product-image-placeholder, .product-detail-image-placeholder, .image-placeholder")
    : null;
  if (placeholder) {
    placeholder.classList.remove("is-hidden");
  } else {
    const fallbackPlaceholder = document.createElement("div");
    fallbackPlaceholder.className = "image-placeholder";
    fallbackPlaceholder.className = "product-image-placeholder";
    fallbackPlaceholder.textContent = "TIDAK ADA GAMBAR";
    img.replaceWith(fallbackPlaceholder);
  }
}

let topStatusWordAnimation = null;
let currentTopStatus = "idle";

function normalizeTopStatus(status) {
  const value = String(status || "").toLowerCase().trim();

  if (["running", "scraping", "ai", "ranking", "berjalan", "loading"].includes(value)) {
    return "running";
  }

  if (["done", "success", "complete", "completed", "selesai"].includes(value)) {
    return "done";
  }

  if (["error", "failed", "gagal"].includes(value)) {
    return "error";
  }

  return "idle";
}

function setTopStatusWord(status = "idle") {
  const normalized = normalizeTopStatus(status);
  const badge = document.querySelector("[data-app-status-wordmark]");
  const svg = document.querySelector(".status-wordmark-svg");
  const srLabel = document.querySelector(".status-label-text");

  if (!badge || !svg) {
    console.warn("[STATUS_WORDMARK] missing DOM");
    return;
  }

  currentTopStatus = normalized;

  const labelMap = {
    idle: "Siap",
    running: "Berjalan",
    done: "Selesai",
    error: "Error"
  };

  badge.classList.remove("is-idle", "is-running", "is-done", "is-error");
  badge.classList.add(`is-${normalized}`);

  svg.setAttribute("aria-label", labelMap[normalized]);
  if (srLabel) srLabel.textContent = labelMap[normalized];

  document.querySelectorAll(".status-word-paths").forEach(group => {
    group.classList.toggle("is-active", group.dataset.statusWord === normalized);
  });

  requestAnimationFrame(() => startStatusWordAnimation(normalized));
}

function stopStatusWordAnimation() {
  if (topStatusWordAnimation && typeof topStatusWordAnimation.pause === "function") {
    topStatusWordAnimation.pause();
  }

  if (topStatusWordAnimation && typeof topStatusWordAnimation.cancel === "function") {
    topStatusWordAnimation.cancel();
  }

  topStatusWordAnimation = null;

  const texts = document.querySelectorAll(".status-word-text");

  if (window.anime && typeof window.anime.remove === "function") {
    window.anime.remove(texts);
  }

  texts.forEach(text => {
    text.style.strokeDasharray = "";
    text.style.strokeDashoffset = "";
    text.style.opacity = "";
    text.style.transform = "";
  });
}

function startStatusWordAnimation(status = "idle") {
  stopStatusWordAnimation();

  const activeGroup = document.querySelector(`.status-word-paths[data-status-word="${status}"]`);
  if (!activeGroup) return;

  const text = activeGroup.querySelector(".status-word-text");
  if (!text) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion) {
    text.style.opacity = "1";
    return;
  }

  let length = 900;
  try {
    if (typeof text.getComputedTextLength === "function") {
      length = Math.ceil(text.getComputedTextLength()) + 40;
    }
  } catch (_error) {}

  text.style.strokeDasharray = String(length);
  text.style.strokeDashoffset = String(length);
  text.style.opacity = "1";

  if (window.anime && typeof window.anime === "function") {
    topStatusWordAnimation = window.anime({
      targets: text,
      strokeDashoffset: [length, 0],
      opacity: [0.4, 1],
      duration: status === "running" ? 1500 : 850,
      easing: "easeInOutSine",
      loop: status === "running",
      direction: status === "running" ? "alternate" : "normal"
    });
    return;
  }

  topStatusWordAnimation = text.animate(
    [
      { strokeDashoffset: length, opacity: 0.4 },
      { strokeDashoffset: 0, opacity: 1 }
    ],
    {
      duration: status === "running" ? 1500 : 850,
      iterations: status === "running" ? Infinity : 1,
      direction: status === "running" ? "alternate" : "normal",
      easing: "ease-in-out",
      fill: "forwards"
    }
  );
}

function startTopStatusDrawable() {
  setTopStatusWord("running");
}

function stopTopStatusDrawable(status = "idle") {
  setTopStatusWord(status);
}

let activeRecommendationMode = "all";
let recommendationTransitionRunning = false;
let isCategoryTransitioning = false;
let categoryTransitionId = 0;
let recommendationCacheVersion = 0;
let recommendationProductCache = new Map();

let activeModalMode = null;
let activeModalProducts = [];
let activeModalIndex = 0;
let activeModalProduct = null;
let modalTransitionRunning = false;
let feedbackSubmitting = false;
const reviewedProductIds = new Set();
const hoverTimers = new WeakMap();
const activeHoverTimerIds = new Set();
const activeHoverCards = new Set();
let checkedLayout = null;
let adaptiveScrollObserver = null;
let adaptiveScrollAnimation = null;
let runningDrawableAnimation = null;

const reviewState = {
  checkedById: new Map(),
  checkedOrder: [],
  activeMode: "all"
};

const RECOMMENDATION_MODES = {
  all: {
    label: "Semua Barang",
    icon: "🧺",
    accent: "#60a5fa"
  },
  terbaik: {
    label: "Terbaik",
    icon: "⭐",
    accent: "#8b5cf6"
  },
  termurah: {
    label: "Termurah",
    icon: "💸",
    accent: "#10b981"
  },
  trusted: {
    label: "Most Trusted",
    icon: "🏆",
    accent: "#f59e0b"
  }
};

function normalizeRecommendationMode(mode) {
  const value = String(mode || "").toLowerCase().trim();

  const map = {
    all: "all",
    semua: "all",
    semua_barang: "all",
    "semua-barang": "all",
    "semua barang": "all",

    terbaik: "terbaik",
    best: "terbaik",

    termurah: "termurah",
    cheapest: "termurah",

    trusted: "trusted",
    mosttrusted: "trusted",
    most_trusted: "trusted",
    "most-trusted": "trusted",
    "most trusted": "trusted"
  };

  return map[value] || null;
}

function getProductReviewId(product) {
  return String(product?.id || product?.url || product?.product_url || product?.title || "");
}

function isProductReviewed(product) {
  const id = getProductReviewId(product);
  return Boolean(id && (reviewState.checkedById.has(id) || reviewedProductIds.has(id)));
}

function invalidateRecommendationCache() {
  recommendationCacheVersion += 1;
  recommendationProductCache.clear();
}

function resetReviewState() {
  reviewState.checkedById.clear();
  reviewState.checkedOrder.length = 0;
  reviewState.activeMode = "all";
  reviewedProductIds.clear();
  invalidateRecommendationCache();
}

function markProductAsReviewed(product, result, extra = {}) {
  const id = getProductReviewId(product);
  if (!id) return "";

  if (!reviewState.checkedById.has(id)) {
    reviewState.checkedOrder.push(id);
  }

  reviewedProductIds.add(id);
  reviewState.checkedById.set(id, {
    id,
    product,
    result,
    reasons: extra.reasons || [],
    note: extra.note || "",
    reviewedAt: Date.now(),
    sourceMode: activeRecommendationMode || "all"
  });

  invalidateRecommendationCache();
  return id;
}

function getActiveRecommendationProducts(mode) {
  const reviewedIds = new Set([
    ...reviewState.checkedById.keys(),
    ...reviewedProductIds
  ]);

  return getRecommendationProducts(mode).filter(product => {
    const id = getProductReviewId(product);
    return !id || !reviewedIds.has(id);
  });
}

function getCheckedProductsForMode(mode) {
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const records = reviewState.checkedOrder
    .map(id => reviewState.checkedById.get(id))
    .filter(Boolean);

  if (normalizedMode === "all") return records;

  const modeProductIds = new Set(
    getRecommendationProducts(normalizedMode).map(product => getProductReviewId(product))
  );

  return records.filter(record => {
    if (record.sourceMode === normalizedMode) return true;
    return modeProductIds.has(record.id);
  });
}

function updateRecommendationButtons(nextMode) {
  document.querySelectorAll('[data-recommendation-mode]').forEach((btn) => {
    const mode = normalizeRecommendationMode(btn.dataset.recommendationMode);
    const isActive = mode === nextMode;

    btn.classList.toggle('is-active', isActive);
    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
}

function updateRecommendationTitle(mode) {
  const titleEl = document.getElementById('recommendationTitle');
  if (titleEl) {
    const normalizedMode = normalizeRecommendationMode(mode) || "all";
    const meta = RECOMMENDATION_MODES[normalizedMode];
    if (meta) titleEl.textContent = meta.label;
  }
}

function updateRecommendationLogo(mode) {
  const iconEl = document.querySelector('.active-mode-icon');
  if (iconEl) {
    const normalizedMode = normalizeRecommendationMode(mode) || "all";
    const meta = RECOMMENDATION_MODES[normalizedMode];
    if (meta) iconEl.textContent = meta.icon;
  }
}

function renderRecommendationProductCard(product) {
  const item = window.app && typeof window.app.normalizeProduct === "function"
    ? window.app.normalizeProduct(product)
    : { ...(product || {}) };
  const id = getProductReviewId(item);
  const imageUrl = resolveProductImage(item);
  const title = item.title || "Produk Tokopedia";
  const ratingStr = item.rating ? `Rating ${item.rating}` : "";
  const soldValue = item.sold || item.sold_text || item.soldCount || item.sold_count || "";
  const soldStr = soldValue ? `${soldValue} terjual` : "";
  const meta = [ratingStr, soldStr].filter(Boolean).join(" | ");

  const imageHtml = imageUrl
    ? `<img class="recommendation-product-image" src="${escapeHtml(imageUrl)}" data-original-src="${escapeHtml(imageUrl)}" alt="${escapeHtml(title)}" loading="lazy" decoding="async" />`
    : "";
  const placeholderHtml = imageUrl
    ? `<div class="product-image-placeholder is-hidden" aria-hidden="true"></div>`
    : `<div class="product-image-placeholder"></div>`;

  return `
    <article class="recommendation-product-card" data-product-card data-product-id="${escapeHtml(id)}" data-id="${escapeHtml(id)}">
      <div class="recommendation-product-image-wrap${imageUrl ? "" : " is-image-missing"}">
        ${imageHtml}
        ${placeholderHtml}
      </div>
      <div class="recommendation-product-card-details">
        <h4 class="recommendation-product-title">${escapeHtml(title)}</h4>
        <div class="recommendation-product-price">${escapeHtml(formatProductPrice(item))}</div>
        <div class="recommendation-product-meta">${escapeHtml(meta)}</div>
      </div>
    </article>
  `;
}

function setupProductImageErrorHandlers(scope = document) {
  scope.querySelectorAll(".recommendation-product-image").forEach(img => {
    if (img.dataset.errorHandlerBound === "true") return;
    img.dataset.errorHandlerBound = "true";

    img.onerror = () => {
      const originalSrc = img.dataset.originalSrc || img.src;
      if (originalSrc && window.app && typeof window.app.proxyImageUrl === "function" && !img.dataset.proxyTried) {
        img.dataset.proxyTried = "1";
        img.src = window.app.proxyImageUrl(originalSrc);
        return;
      }

      handleImageError(img);
    };
  });
}

function renderRecommendationContent(mode) {
  const grid = document.querySelector(".recommendation-product-grid");
  if (!grid) return;

  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const products = getActiveRecommendationProducts(normalizedMode);

  grid.innerHTML = products.length
    ? products.slice(0, 12).map(product => renderRecommendationProductCard(product)).join("")
    : '<div class="recommendation-empty">Semua produk di kategori ini sudah dicek.</div>';

  setupProductImageErrorHandlers(grid);
}

function updateRecommendationContent(mode) {
  renderRecommendationContent(mode);
}

function animateRecommendationCardsEnter(profile) {
  if (!profile || profile.duration === 0) return;
  const cards = document.querySelectorAll('.recommendation-product-card');
  if (!cards.length) return;

  AnimeBridge.run(cards, {
    opacity: [0, 1],
    translateY: [profile.enterY, 0],
    scale: [profile.enterScale, 1],
    rotateX: [profile.rotateX, 0],
    delay: AnimeBridge.stagger(profile.staggerDelay, { grid: profile.grid, from: 'center' }),
    duration: profile.duration,
    easing: 'easeOutExpo',
  });
}

function animateRecommendationCardsExit(container, profile) {
  if (!profile || profile.duration === 0) return Promise.resolve();
  const cards = (container || document).querySelectorAll('.recommendation-product-card');
  if (!cards.length) return Promise.resolve();

  return new Promise((resolve) => {
    AnimeBridge.run(cards, {
      opacity: [1, 0],
      translateY: [0, -24],
      scale: [1, 0.92],
      duration: Math.round(profile.duration * 0.55),
      easing: 'easeInQuad',
      complete: resolve,
    }) || resolve();
  });
}

function getCategoryMotionProfile() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isMobile = window.matchMedia("(max-width: 700px)").matches;

  if (reduceMotion) {
    return {
      oldExit: 0,
      cloneMove: 0,
      zoom: 0,
      title: 0,
      enter: 0,
      stagger: 0,
      cloneScale: 1
    };
  }

  if (isMobile) {
    return {
      oldExit: 120,
      cloneMove: 260,
      zoom: 360,
      title: 220,
      enter: 280,
      stagger: 18,
      cloneScale: 9
    };
  }

  return {
    oldExit: 140,
    cloneMove: 320,
    zoom: 460,
    title: 260,
    enter: 340,
    stagger: 22,
    cloneScale: 13
  };
}

const getFastCategoryMotionProfile = getCategoryMotionProfile;
const getOrbMorphProfile = getCategoryMotionProfile;

function hardRenderRecommendationMode(mode) {
  const normalized = normalizeRecommendationMode(mode) || "all";
  activeRecommendationMode = normalized;
  reviewState.activeMode = normalized;
  recommendationTransitionRunning = false;
  isCategoryTransitioning = false;

  if (window.app) {
    window.app.state.recommendationMode = normalized;
    window.app.state.hasUserSelectedRecommendation = true;
  }

  updateRecommendationButtons(normalized);
  updateSingleRecommendationTitle(normalized);
  renderRecommendationContent(normalized);
  renderCheckedProductsBox(normalized);

  const stage = document.querySelector(".recommendation-stage");
  if (stage) {
    stage.dataset.activeMode = normalized;
    stage.classList.remove("is-camera-zooming", "is-category-zooming");
  }

  const panel = document.querySelector(".recommendation-active-panel");
  unlockElementHeight(panel);
}

async function selectRecommendationMode(nextMode, triggerButton) {
  nextMode = normalizeRecommendationMode(nextMode);
  if (!nextMode) return;
  if (nextMode === activeRecommendationMode && !isCategoryTransitioning) return;

  triggerButton = triggerButton || document.querySelector(`[data-recommendation-mode="${nextMode}"]`);

  const transitionId = ++categoryTransitionId;
  isCategoryTransitioning = true;
  recommendationTransitionRunning = true;

  const stage = document.querySelector(".recommendation-stage");
  const panel = document.querySelector(".recommendation-active-panel");
  const grid = document.querySelector(".recommendation-product-grid");
  const title = document.querySelector(".recommendation-active-title");

  if (!stage || !panel || !grid || !title || !triggerButton) {
    hardRenderRecommendationMode(nextMode);
    return;
  }

  const profile = getCategoryMotionProfile();

  try {
    stage.classList.add("is-camera-zooming");
    stage.dataset.activeMode = nextMode;

    lockElementHeight(panel);
    updateRecommendationButtons(nextMode);

    const clone = createCategoryZoomClone(triggerButton, nextMode);
    const glow = createCategoryZoomGlow(panel, nextMode);

    const oldCards = [...grid.querySelectorAll("[data-product-card], .recommendation-product-card")];

    AnimeBridge.run(oldCards, {
      opacity: [1, 0],
      translateY: [0, -16],
      scale: [1, 0.965],
      delay: AnimeBridge.stagger(10, { from: "center", reversed: true }),
      duration: profile.oldExit,
      easing: "easeInQuad"
    });

    await sleep(profile.oldExit * 0.7);
    if (transitionId !== categoryTransitionId) {
      cleanupCategoryZoom(clone, glow, panel, stage);
      return;
    }

    await animateCloneIntoPanel(clone, panel, profile);
    if (transitionId !== categoryTransitionId) {
      cleanupCategoryZoom(clone, glow, panel, stage);
      return;
    }

    await animateCloneZoomFill(clone, glow, nextMode, profile);
    if (transitionId !== categoryTransitionId) {
      cleanupCategoryZoom(clone, glow, panel, stage);
      return;
    }

    activeRecommendationMode = nextMode;
    reviewState.activeMode = nextMode;

    if (window.app) {
      window.app.state.recommendationMode = nextMode;
      window.app.state.hasUserSelectedRecommendation = true;
    }

    updateSingleRecommendationTitle(nextMode);
    renderRecommendationContent(nextMode);
    renderCheckedProductsBox(nextMode);

    await nextFrameTwice();
    if (transitionId !== categoryTransitionId) {
      cleanupCategoryZoom(clone, glow, panel, stage);
      return;
    }

    animateTitleEnter(title, profile);

    const newCards = [...grid.querySelectorAll("[data-product-card], .recommendation-product-card")];

    AnimeBridge.run(newCards, {
      opacity: [0, 1],
      translateY: [26, 0],
      scale: [0.965, 1],
      delay: AnimeBridge.stagger(profile.stagger, { start: 40, from: "center" }),
      duration: profile.enter,
      easing: "easeOutCubic"
    });

    await sleep(profile.enter + 80);

    cleanupCategoryZoom(clone, glow, panel, stage);
  } catch (error) {
    console.error("[CATEGORY_CAMERA_ZOOM] failed:", error);
    hardRenderRecommendationMode(nextMode);
  } finally {
    if (transitionId === categoryTransitionId) {
      isCategoryTransitioning = false;
      recommendationTransitionRunning = false;
    }
  }
}

function isTransitionStillActive(id) {
  return id === categoryTransitionId;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, Math.max(0, Number(ms) || 0)));
}

function resetCardInlineMotion(cards) {
  cards.forEach(card => {
    card.style.transform = "";
    card.style.opacity = "";
    card.style.boxShadow = "";
  });
}

function cancelAllHoverTimers() {
  activeHoverTimerIds.forEach(timer => clearTimeout(timer));
  activeHoverTimerIds.clear();

  activeHoverCards.forEach(card => {
    hoverTimers.delete(card);
    if (card.isConnected) {
      card.style.transform = "";
      card.style.opacity = "";
      card.style.boxShadow = "";
    }
  });
  activeHoverCards.clear();
}

function getEventElement(event) {
  return event?.target instanceof Element ? event.target : event?.target?.parentElement || null;
}

function animateActiveButtonPulse(button, profile) {
  if (!button || profile.panelDuration === 0) return;

  AnimeBridge.run(button, {
    scale: [1, 1.08],
    translateY: [0, -3],
    duration: 130,
    easing: "easeOutCubic",
    complete: () => {
      AnimeBridge.run(button, {
        scale: [1.08, 1],
        translateY: [-3, 0],
        duration: 130,
        easing: "easeOutCubic"
      });
    }
  });

  const icon = button.querySelector(".mode-icon");
  if (icon) {
    AnimeBridge.run(icon, {
      scale: [1, 1.35],
      duration: 150,
      easing: "easeOutBack",
      complete: () => {
        AnimeBridge.run(icon, {
          scale: [1.35, 1],
          duration: 170,
          easing: "easeOutCubic"
        });
      }
    });
  }
}

function animateFocusLogoPulse(focusLogo, profile) {
  if (!focusLogo || profile.panelDuration === 0) return;

  AnimeBridge.run(focusLogo, {
    scale: [1, profile.logoScale],
    opacity: [0.82, 1],
    duration: Math.round(profile.panelDuration * 0.48),
    easing: "easeOutCubic",
    complete: () => {
      AnimeBridge.run(focusLogo, {
        scale: [profile.logoScale, 1],
        opacity: [1, 1],
        duration: Math.round(profile.panelDuration * 0.52),
        easing: "easeOutCubic"
      });
    }
  });
}

function animatePanelPulse(panel, profile) {
  if (!panel || profile.panelDuration === 0) return;

  AnimeBridge.run(panel, {
    scale: [1, 1.01],
    translateY: [0, -4],
    duration: Math.round(profile.panelDuration * 0.5),
    easing: "easeOutCubic",
    complete: () => {
      AnimeBridge.run(panel, {
        scale: [1.01, 1],
        translateY: [-4, 0],
        duration: Math.round(profile.panelDuration * 0.5),
        easing: "easeOutCubic"
      });
    }
  });
}

function createCategoryZoomClone(button, mode) {
  const meta = RECOMMENDATION_MODES[mode];
  if (!meta || !button) return null;

  const rect = button.getBoundingClientRect();
  const clone = document.createElement("div");
  clone.className = "category-zoom-clone";
  clone.innerHTML = `
    <span class="category-zoom-clone-icon">${meta.icon}</span>
    <span class="category-zoom-clone-label">${meta.label}</span>
  `;

  clone.style.setProperty("--category-accent", meta.accent);
  clone.style.left = `${rect.left}px`;
  clone.style.top = `${rect.top}px`;
  clone.style.width = `${rect.width}px`;
  clone.style.height = `${rect.height}px`;

  document.body.appendChild(clone);
  return clone;
}

function createCategoryZoomGlow(panel, mode) {
  const meta = RECOMMENDATION_MODES[mode];
  if (!meta || !panel) return null;

  const glow = document.createElement("div");
  glow.className = "category-zoom-glow";
  glow.style.setProperty("--category-accent", meta.accent);
  panel.appendChild(glow);
  return glow;
}

async function animateCloneIntoPanel(clone, panel, profile) {
  if (!clone || !panel || profile.cloneMove === 0) return;

  const cloneRect = clone.getBoundingClientRect();
  const panelRect = panel.getBoundingClientRect();

  const targetX = panelRect.left + panelRect.width * 0.5 - (cloneRect.left + cloneRect.width * 0.5);
  const targetY = panelRect.top + panelRect.height * 0.32 - (cloneRect.top + cloneRect.height * 0.5);

  clone.style.transform = "translate(0px, 0px) scale(1)";

  AnimeBridge.run(clone, {
    translateX: [0, targetX],
    translateY: [0, targetY],
    scale: [1, 1.08],
    duration: profile.cloneMove,
    easing: "easeOutExpo"
  });

  await sleep(profile.cloneMove);
}

async function animateCloneZoomFill(clone, glow, mode, profile) {
  if (!clone || profile.zoom === 0) return;

  AnimeBridge.run(clone, {
    scale: [1.08, profile.cloneScale],
    opacity: [1, 0],
    duration: profile.zoom,
    easing: "easeInOutCubic"
  });

  if (glow) {
    AnimeBridge.run(glow, {
      opacity: [0, 1, 0],
      scale: [0.4, 1.25, 1.75],
      duration: profile.zoom,
      easing: "easeOutExpo"
    });
  }

  await sleep(Math.round(profile.zoom * 0.72));
}

function updateSingleRecommendationTitle(mode) {
  const meta = RECOMMENDATION_MODES[mode];
  const title = document.querySelector(".recommendation-active-title");

  if (title && meta) {
    title.textContent = meta.label;
  }

  document.querySelectorAll(".duplicate-category-title, .inner-category-title, .recommendation-panel-title").forEach(el => {
    if (el !== title) el.remove();
  });
}

function animateTitleEnter(title, profile) {
  if (!title || profile.title === 0) return;

  AnimeBridge.run(title, {
    opacity: [0, 1],
    translateX: [34, 0],
    translateY: [10, 0],
    duration: profile.title,
    easing: "easeOutCubic"
  });
}

function cleanupCategoryZoom(clone, glow, panel, stage) {
  if (clone && clone.parentNode) clone.parentNode.removeChild(clone);
  if (glow && glow.parentNode) glow.parentNode.removeChild(glow);

  unlockElementHeight(panel);

  if (stage) {
    stage.classList.remove("is-camera-zooming", "is-category-zooming");
  }
}

function lockElementHeight(element) {
  if (!element) return;
  const height = element.offsetHeight;
  if (height > 0) element.style.minHeight = `${height}px`;
}

function unlockElementHeight(element) {
  if (!element) return;
  requestAnimationFrame(() => {
    element.style.minHeight = "";
  });
}

function lockGridMinHeight(grid) {
  lockElementHeight(grid);
}

function unlockGridMinHeight(grid) {
  unlockElementHeight(grid);
}

function buildRecommendationProducts(mode) {
  if (!window.app) return [];
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const buckets = window.app.buildRecommendationBuckets();
  return buckets[normalizedMode] || [];
}

function getCachedRecommendationProducts(mode) {
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const key = `${recommendationCacheVersion}:${normalizedMode}`;

  if (recommendationProductCache.has(key)) {
    return recommendationProductCache.get(key);
  }

  const products = buildRecommendationProducts(normalizedMode);
  recommendationProductCache.set(key, products);

  return products;
}

function getRecommendationProducts(mode) {
  return getCachedRecommendationProducts(mode);
}

function cssEscapeValue(value) {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") {
    return CSS.escape(String(value));
  }

  return String(value).replace(/["\\]/g, "\\$&");
}

function nextFrameTwice() {
  return new Promise(resolve => {
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  });
}

function setupCheckedProductsLayout() {
  const container = document.querySelector(".checked-products-grid");
  if (!container) return;

  if (checkedLayout && checkedLayout.__marketspyContainer === container) return;

  if (checkedLayout && typeof checkedLayout.revert === "function") {
    checkedLayout.revert();
  }

  checkedLayout = AnimeBridge.createLayout(container, {
    children: ".checked-product-card",
    duration: 650,
    ease: "out(4)",
    delay: AnimeBridge.stagger(45),
    enterFrom: {
      opacity: 0,
      scale: 0.72,
      y: 42,
      filter: "blur(10px)"
    },
    leaveTo: {
      opacity: 0,
      scale: 0.82,
      y: -24,
      filter: "blur(8px)"
    },
    properties: ["boxShadow", "borderColor"]
  });

  if (checkedLayout) {
    checkedLayout.__marketspyContainer = container;
  }
}

function animateCheckedCardEnterFallback(card) {
  if (!card) return;

  AnimeBridge.run(card, {
    opacity: [0, 1],
    translateY: [42, 0],
    scale: [0.72, 1],
    filter: ["blur(10px)", "blur(0px)"],
    duration: 650,
    easing: "easeOutExpo"
  });
}

function getCheckedTrayRects(container) {
  const rects = new Map();
  if (!container) return rects;

  container.querySelectorAll(".checked-product-card").forEach(card => {
    const id = card.dataset.productId;
    if (id) rects.set(id, card.getBoundingClientRect());
  });

  return rects;
}

function animateCheckedTrayFlipFallback(firstRects, sourceRect, enteredId) {
  const container = document.querySelector(".checked-products-grid");
  if (!container) return;

  const cards = [...container.querySelectorAll(".checked-product-card")];

  cards.forEach(card => {
    const id = card.dataset.productId;
    const first = id ? firstRects.get(id) : null;
    const last = card.getBoundingClientRect();

    if (!first || id === enteredId) return;

    const dx = first.left - last.left;
    const dy = first.top - last.top;
    if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;

    card.style.transform = `translate(${dx}px, ${dy}px)`;
    card.style.transition = "transform 0s";

    requestAnimationFrame(() => {
      card.style.transition = "";
      AnimeBridge.run(card, {
        translateX: [dx, 0],
        translateY: [dy, 0],
        scale: [0.985, 1],
        duration: 620,
        easing: "easeOutExpo"
      });
    });
  });

  const enteredCard = cards.find(card => card.dataset.productId === enteredId);
  if (!enteredCard) return;

  if (sourceRect) {
    const last = enteredCard.getBoundingClientRect();
    const dx = sourceRect.left - last.left;
    const dy = sourceRect.top - last.top;

    enteredCard.style.opacity = "0.12";
    enteredCard.style.transform = `translate(${dx}px, ${dy}px) scale(0.72)`;
    enteredCard.style.filter = "blur(10px)";

    requestAnimationFrame(() => {
      enteredCard.style.opacity = "";
      enteredCard.style.transform = "";
      enteredCard.style.filter = "";

      AnimeBridge.run(enteredCard, {
        opacity: [0.12, 1],
        translateX: [dx, 0],
        translateY: [dy, 0],
        scale: [0.72, 1],
        filter: ["blur(10px)", "blur(0px)"],
        duration: 650,
        easing: "easeOutExpo"
      });
    });

    return;
  }

  animateCheckedCardEnterFallback(enteredCard);
}

function createCheckedProductCard(record) {
  const product = record.product || {};
  const card = document.createElement("article");
  card.className = `checked-product-card is-${record.result === "positive" ? "positive" : "negative"}`;
  card.dataset.productId = record.id;

  const badge = document.createElement("span");
  badge.className = `checked-product-badge is-${record.result === "positive" ? "positive" : "negative"}`;
  badge.textContent = record.result === "positive" ? "Benar" : "Salah";

  const title = document.createElement("h4");
  title.className = "checked-product-title";
  title.textContent = product.title || "Produk Tokopedia";

  const price = document.createElement("p");
  price.className = "checked-product-price";
  price.textContent = formatProductPrice(product);

  const meta = document.createElement("p");
  meta.className = "checked-product-meta";
  const modeLabel = RECOMMENDATION_MODES[record.sourceMode]?.label || "Semua Barang";
  meta.textContent = `${modeLabel} | ${new Date(record.reviewedAt).toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit"
  })}`;

  card.append(badge, title, price, meta);
  return card;
}

function renderCheckedProductsBox(mode) {
  setupCheckedProductsLayout();

  const box = document.querySelector(".checked-products-box");
  const grid = document.querySelector(".checked-products-grid");
  const count = document.querySelector(".checked-products-count");
  if (!box || !grid) return;

  const records = getCheckedProductsForMode(mode);
  if (count) count.textContent = `${records.length} produk`;

  grid.innerHTML = "";

  if (!records.length) {
    const empty = document.createElement("div");
    empty.className = "checked-products-empty";
    empty.textContent = "Belum ada produk yang dicek.";
    grid.appendChild(empty);
  } else {
    records.forEach(record => grid.appendChild(createCheckedProductCard(record)));
  }

  if (checkedLayout && typeof checkedLayout.refresh === "function") {
    requestAnimationFrame(() => checkedLayout.refresh());
  }
}

function animateActiveCardExit(card) {
  return new Promise(resolve => {
    if (!card) {
      resolve();
      return;
    }

    AnimeBridge.run(card, {
      opacity: [1, 0],
      scale: [1, 0.72],
      translateY: [0, 34],
      rotateZ: [0, 2],
      filter: ["blur(0px)", "blur(8px)"],
      duration: 420,
      easing: "easeInExpo",
      complete: resolve
    }) || resolve();
  });
}

function pulseCheckedBox() {
  const box = document.querySelector(".checked-products-box");
  if (!box) return;

  AnimeBridge.run(box, {
    scale: [1, 1.015, 1],
    boxShadow: [
      "0 0 0 rgba(34,211,238,0)",
      "0 0 54px rgba(34,211,238,0.18)",
      "0 0 0 rgba(34,211,238,0)"
    ],
    duration: 720,
    easing: "easeOutExpo"
  });
}

async function moveProductToCheckedTray(product, result, extra = {}) {
  const id = markProductAsReviewed(product, result, extra);
  if (!id) return;

  const sourceCard = document.querySelector(
    `.recommendation-product-card[data-product-id="${cssEscapeValue(id)}"]`
  );
  const sourceRect = sourceCard ? sourceCard.getBoundingClientRect() : null;
  const checkedGrid = document.querySelector(".checked-products-grid");
  const firstRects = getCheckedTrayRects(checkedGrid);

  await animateActiveCardExit(sourceCard);

  renderRecommendationContent(activeRecommendationMode);
  renderCheckedProductsBox(activeRecommendationMode);

  await nextFrameTwice();

  const checkedCard = document.querySelector(
    `.checked-product-card[data-product-id="${cssEscapeValue(id)}"]`
  );

  if (checkedLayout && typeof checkedLayout.refresh === "function") {
    checkedLayout.refresh();
  } else if (checkedCard) {
    animateCheckedTrayFlipFallback(firstRects, sourceRect, id);
  }

  pulseCheckedBox();
  setupAdaptiveScrollBehavior();
}

function openRecommendationProductModal(product, sourceCard) {
  const mode = activeRecommendationMode || "all";
  const queue = getActiveRecommendationProducts(mode);
  const target = product || queue[0];

  if (!target) {
    showSmallToast("Tidak ada produk rekomendasi yang bisa direview.");
    return;
  }

  window.__ACTIVE_MODAL_SOURCE_CARD__ = sourceCard || null;
  openProductDetailModal(target, queue);
}

function showRecommendationDialogWithAnimation() {
  const dialog = document.querySelector("#recommendation-product-dialog");
  if (!dialog) return;

  if (!dialog.open) dialog.showModal();

  AnimeBridge.run(".recommendation-modal-card", {
    opacity: [0, 1],
    translateY: [56, 0],
    scale: [0.88, 1],
    duration: 1000,
    easing: "easeOutExpo"
  });

  AnimeBridge.run(".recommendation-modal-image-wrap", {
    opacity: [0, 1],
    translateX: [-48, 0],
    scale: [0.96, 1],
    duration: 1000,
    delay: 120,
    easing: "easeOutExpo"
  });

  AnimeBridge.run(".recommendation-modal-content > *", {
    opacity: [0, 1],
    translateX: [36, 0],
    delay: AnimeBridge.stagger(70, { start: 180 }),
    duration: 850,
    easing: "easeOutExpo"
  });
}

function resolveProductImage(product) {
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
    product?.media?.url
  ];

  for (const value of candidates) {
    if (!value) continue;

    let url = String(value).trim();

    if (!url) continue;
    if (url.startsWith("//")) url = `https:${url}`;
    if (/^https?:\/\//i.test(url)) return url;
  }

  return "";
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatRupiah(value) {
  if (window.app && typeof window.app.formatRupiah === "function") {
    return window.app.formatRupiah(value);
  }
  const number = Number(value || 0);
  if (!number) return 'Harga tidak tersedia';
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(number);
}

function formatProductPrice(product) {
  const numeric = product?.price_value ?? product?.priceNumber ?? product?.price_val;
  if (Number(numeric) > 0) return formatRupiah(numeric);
  return product?.price || product?.price_text || product?.price_raw || "Harga tidak tersedia";
}

function setText(selector, value) {
  const el = document.querySelector(selector);
  if (el) el.textContent = value;
}

function fillRecommendationModal(product) {
  const imageUrl = resolveProductImage(product);

  const imgWrap = document.querySelector(".recommendation-modal-image-wrap");

  if (imgWrap) {
    if (imageUrl) {
      imgWrap.innerHTML = `
        <img
          class="recommendation-modal-image"
          src="${escapeHtml(imageUrl)}"
          alt="Gambar produk"
          loading="lazy"
          decoding="async"
        />
      `;

      const newImg = imgWrap.querySelector("img");
      newImg.addEventListener("error", () => {
        imgWrap.innerHTML = `
          <div class="image-placeholder">
            <strong>Tidak ada gambar</strong>
            <span>Gambar tidak tersedia</span>
          </div>
        `;
      }, { once: true });
    } else {
      imgWrap.innerHTML = `
        <div class="image-placeholder">
          <strong>Tidak ada gambar</strong>
          <span>Gambar tidak tersedia</span>
        </div>
      `;
    }
  }

  setText(".recommendation-modal-kicker", "DETAIL REKOMENDASI");
  setText(".recommendation-modal-title", product?.title || "-");
  setText(".recommendation-modal-store", product?.storeName || product?.shop_name || product?.shop || product?.store || "");
  setText(".recommendation-modal-price", formatProductPrice(product));
  setText(".recommendation-modal-rating", `⭐ ${product?.rating || "-"}`);
  setText(".recommendation-modal-sold", `🛍️ ${product?.sold || product?.sold_text || "0 terjual"}`);
  setText(".recommendation-modal-confidence", `🧠 Keyakinan AI: ${product?.confidenceScore ?? product?.confidence ?? product?.ai_confidence ?? product?.relevance_score ?? "-"}`);

  const openBtn = document.querySelector("#recommendation-product-dialog .open-product-btn");
  if (openBtn) {
    openBtn.textContent = "Buka Produk";
    openBtn.href = product?.url || "#";
  }

  const reasonGrid = document.querySelector(".modal-feedback-reason-grid");
  if (reasonGrid) {
    reasonGrid.innerHTML = "";
    const reasons = [
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
    reasons.forEach(reason => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "feedback-reason-chip modal-feedback-reason-chip";
      chip.dataset.reason = reason;
      chip.textContent = reason;
      chip.addEventListener("click", (e) => {
        e.preventDefault();
        chip.classList.toggle("is-selected");
      });
      reasonGrid.appendChild(chip);
    });
  }
}

function getNextModalProduct() {
  if (!activeModalProducts.length) return null;

  for (let i = activeModalIndex + 1; i < activeModalProducts.length; i++) {
    const candidate = activeModalProducts[i];
    if (!isProductReviewed(candidate)) {
      activeModalIndex = i;
      return candidate;
    }
  }

  return null;
}

function closeRecommendationProductModal() {
  return new Promise(resolve => {
    closeProductDetailModal();
    activeModalProduct = null;
    window.__ACTIVE_MODAL_PRODUCT__ = null;
    window.__ACTIVE_MODAL_SOURCE_CARD__ = null;
    window.setTimeout(resolve, 240);
  });
}

async function handleModalFeedback(type, extra = {}) {
  if (feedbackSubmitting || modalTransitionRunning) return;
  if (!activeModalProduct) return;

  feedbackSubmitting = true;

  const product = activeModalProduct;
  const productId = getProductReviewId(product);

  try {
    await sendFeedback({
      product_id: productId,
      feedback_type: type,
      reasons: extra.reasons || [],
      note: extra.note || ""
    });

    await moveProductToCheckedTray(product, type, extra);

    const nextProduct = getNextModalProduct();

    if (nextProduct) {
      await transitionModalToNextProduct(nextProduct);
    } else {
      await closeRecommendationProductModal();
      showSmallToast("Semua produk di kategori ini sudah dicek.");
    }
  } catch (error) {
    console.error("[FEEDBACK] modal feedback failed:", error);
    showSmallToast("Feedback gagal dikirim. Coba lagi.");
  } finally {
    feedbackSubmitting = false;
  }
}

function transitionModalToNextProduct(nextProduct) {
  return new Promise(resolve => {
    modalTransitionRunning = true;
    let settled = false;

    const finish = () => {
      if (settled) return;
      settled = true;
      modalTransitionRunning = false;
      resolve();
    };

    const contentTargets = document.querySelectorAll(
      ".recommendation-modal-image-wrap, .recommendation-modal-content > *"
    );

    AnimeBridge.run(contentTargets, {
      opacity: [1, 0],
      translateX: [0, -42],
      scale: [1, 0.96],
      filter: ["blur(0px)", "blur(8px)"],
      delay: AnimeBridge.stagger(35, { reversed: true }),
      duration: 360,
      easing: "easeInExpo",
      complete: () => {
        activeModalProduct = nextProduct;
        window.__ACTIVE_MODAL_PRODUCT__ = nextProduct;

        fillRecommendationModal(nextProduct);
        resetModalFeedbackPanel();

        requestAnimationFrame(() => {
          const newTargets = document.querySelectorAll(
            ".recommendation-modal-image-wrap, .recommendation-modal-content > *"
          );
          const fallbackTimer = window.setTimeout(finish, 1200);

          AnimeBridge.run(newTargets, {
            opacity: [0, 1],
            translateX: [48, 0],
            scale: [0.96, 1],
            filter: ["blur(8px)", "blur(0px)"],
            delay: AnimeBridge.stagger(55, { start: 80 }),
            duration: 720,
            easing: "easeOutExpo",
            complete: () => {
              window.clearTimeout(fallbackTimer);
              finish();
            }
          }) || (() => {
            window.clearTimeout(fallbackTimer);
            finish();
          })();
        });
      }
    }) || (() => {
      activeModalProduct = nextProduct;
      fillRecommendationModal(nextProduct);
      resetModalFeedbackPanel();
      finish();
    })();
  });
}

function resetModalFeedbackPanel() {
  const panel = document.querySelector(".modal-feedback-reason-panel");
  if (panel) panel.hidden = true;

  document
    .querySelectorAll(".modal-feedback-reason-chip, .feedback-reason-chip")
    .forEach(chip => chip.classList.remove("is-selected"));

  const note = document.querySelector(".modal-feedback-note");
  if (note) note.value = "";
}

function revealModalReasonPanel() {
  const panel = document.querySelector(".modal-feedback-reason-panel");
  if (!panel) return;

  panel.hidden = false;

  AnimeBridge.run(panel, {
    opacity: [0, 1],
    translateY: [24, 0],
    duration: 650,
    easing: "easeOutExpo"
  });

  const chips = panel.querySelectorAll(".feedback-reason-chip, .modal-feedback-reason-chip");
  if (chips.length > 0) {
    AnimeBridge.run(chips, {
      opacity: [0, 1],
      translateY: [16, 0],
      scale: [0.94, 1],
      delay: AnimeBridge.stagger(45),
      duration: 650,
      easing: "easeOutExpo"
    });
  }
}

function collectModalSelectedReasons() {
  const panel = document.querySelector(".modal-feedback-reason-panel");
  if (!panel) return [];
  const selectedChips = panel.querySelectorAll(".feedback-reason-chip.is-selected, .modal-feedback-reason-chip.is-selected");
  return Array.from(selectedChips).map(chip => chip.dataset.reason || chip.textContent);
}

function collectModalFeedbackNote() {
  const note = document.querySelector(".modal-feedback-note");
  return note ? note.value.trim() : "";
}

async function sendFeedback(data) {
  const productId = String(data.product_id);
  const type = data.feedback_type;
  const reasons = data.reasons || [];
  const note = data.note || "";

  const product = (window.__MARKETSPY_PRODUCTS__ || []).find(p => getProductReviewId(p) === productId)
    || (activeModalProduct && getProductReviewId(activeModalProduct) === productId ? activeModalProduct : {})
    || {};
  const searchId = window.app?.state?.searchId || "unknown";
  
  const payload = {
    search_id: searchId,
    product_id: productId,
    product_title: product.title || "",
    user_action: type === "positive" ? "benar" : "salah",
    feedback_type: type,
    selected_reasons: reasons,
    reasons: reasons,
    custom_reason: note,
    note: note,
    corrected_label: type === "positive" ? "relevan" : "tidak_relevan",
    ai_label: product.ai_label || (product.ai_decision === false ? 'tidak_relevan' : 'relevan'),
    ai_confidence: product.confidenceScore ?? product.ai_confidence ?? product.relevance_score ?? 0,
    rule_score: product.rule_score ?? 0,
    semantic_score: product.semantic_score ?? 0,
    combined_score: product.combined_score ?? 0,
    learned_adjustment: product.learned_adjustment ?? 0,
    confidence: product.confidenceScore ?? product.confidence ?? product.ai_confidence ?? product.relevance_score ?? 0,
    learning_scope_hint: type === "positive" ? "exact_query" : "query_intent",
    model_used: product._model || product.model_used || '',
    ai_reason: product.relevanceReason || product.ai_reason || product.reason || '',
    sort_mode: window.app?.state?.sortMode || 'terbaik',
    decision_source: product.ai_source || product.decision_source || '',
    query_intent: product.query_intent || window.app?.state?.metadata?.query_intent || '',
    product: {
      id: product.id || '',
      title: product.title || '',
      price_value: product.priceNumber ?? product.price_value ?? 0,
      price: product.priceNumber ?? product.price_value ?? 0,
      store: product.storeName || product.shop_name || product.shop || '',
      url: product.url || product.product_url || '',
      image: product.image || product.image_url || '',
      image_url: product.image_url || product.image || '',
      has_image: Boolean(product.image_url || product.image),
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
    query: window.app?.state?.query || '',
    timestamp: new Date().toISOString()
  };

  const res = await fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const responseData = await res.json();
  if (!responseData.success) {
    throw new Error(responseData.error || "Gagal menyimpan feedback");
  }

  const card = Array.from(document.querySelectorAll('.product-card'))
    .find((item) => item.dataset.id === productId || item.dataset.productId === productId);
  if (card) {
    card.classList.add('feedback-sent');
    card.title = `Feedback: ${payload.user_action}`;
    const badges = card.querySelector('.product-badges');
    if (badges && !badges.querySelector('.feedback-accepted-badge')) {
      const badge = document.createElement('span');
      badge.className = 'feedback-accepted-badge product-badge';
      badge.textContent = type === 'positive' ? 'Benar' : 'Feedback diterima';
      badges.appendChild(badge);
    }
  }

  showSmallToast("Feedback disimpan");
  return true;
}

function showSmallToast(message) {
  if (window.app && typeof window.app.showToast === "function") {
    window.app.showToast(message);
    return;
  }
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

async function handleGridFeedback(productId, type, card, extra = {}) {
  if (!productId || !card) return;

  try {
    await sendFeedback({
      product_id: productId,
      feedback_type: type,
      reasons: extra.reasons || [],
      note: extra.note || ""
    });

    reviewedProductIds.add(String(productId));

    animateGridCardExitAndFocusNext(card);
  } catch (error) {
    console.error("[FEEDBACK] grid feedback failed:", error);
    showSmallToast("Feedback gagal dikirim. Coba lagi.");
  }
}

function animateGridCardExitAndFocusNext(card) {
  if (!card) return;

  const container = card.closest("#products-grid, .products-grid");
  if (!container) {
    card.remove();
    return;
  }

  const beforeCards = [...container.children];
  const firstRects = new Map();

  beforeCards.forEach(el => {
    firstRects.set(el, el.getBoundingClientRect());
  });

  AnimeBridge.run(card, {
    opacity: [1, 0],
    scale: [1, 0.72],
    translateY: [0, -28],
    rotateZ: [0, -3],
    filter: ["blur(0px)", "blur(8px)"],
    duration: 420,
    easing: "easeInExpo",
    complete: () => {
      const nextCard = card.nextElementSibling;
      if (nextCard && typeof nextCard.focus === "function") {
        nextCard.focus();
      }

      card.remove();

      const afterCards = [...container.children];

      afterCards.forEach(el => {
        const first = firstRects.get(el);
        const last = el.getBoundingClientRect();

        if (!first) return;

        const dx = first.left - last.left;
        const dy = first.top - last.top;

        if (!dx && !dy) return;

        el.style.transform = `translate(${dx}px, ${dy}px)`;
        el.style.transition = "transform 0s";

        requestAnimationFrame(() => {
          el.style.transition = "";

          AnimeBridge.run(el, {
            translateX: [dx, 0],
            translateY: [dy, 0],
            scale: [0.98, 1],
            duration: 620,
            easing: "easeOutExpo"
          });
        });
      });
    }
  }) || (() => {
    card.remove();
  })();
}

function getScrollContainer() {
  return (
    document.querySelector(".app-scroll-container") ||
    document.querySelector(".main-scroll-container") ||
    document.querySelector("[data-scroll-container]") ||
    document.scrollingElement ||
    document.documentElement
  );
}

function setupAdaptiveScrollBehavior() {
  const container = getScrollContainer();
  const animeGlobal = window.anime;

  if (adaptiveScrollObserver) {
    adaptiveScrollObserver.disconnect();
    adaptiveScrollObserver = null;
  }

  if (adaptiveScrollAnimation && typeof adaptiveScrollAnimation.pause === "function") {
    adaptiveScrollAnimation.pause();
  }
  adaptiveScrollAnimation = null;

  const onScrollFn =
    typeof window.onScroll === "function"
      ? window.onScroll
      : animeGlobal?.onScroll;

  const targets = [
    ".recommendation-stage",
    ".checked-products-box",
    ".results-grid .product-card"
  ];

  const availableTargets = [...new Set(
    targets
      .flatMap(selector => [...document.querySelectorAll(selector)])
      .filter(Boolean)
  )];

  if (!availableTargets.length) return;

  if (
    typeof onScrollFn === "function" &&
    animeGlobal &&
    typeof animeGlobal.animate === "function"
  ) {
    adaptiveScrollAnimation = animeGlobal.animate(availableTargets, {
      opacity: [0.72, 1],
      translateY: [48, 0],
      scale: [0.965, 1],
      delay: animeGlobal.stagger ? animeGlobal.stagger(35) : 0,
      duration: 720,
      easing: "easeOutExpo",
      autoplay: onScrollFn({
        container,
        target: availableTargets,
        axis: "y",
        enter: "bottom top",
        leave: "top bottom",
        sync: 0.35
      })
    });

    return;
  }

  setupIntersectionScrollFallback(availableTargets, container);
}

function setupIntersectionScrollFallback(targets, container) {
  if (!('IntersectionObserver' in window)) {
    targets.forEach(el => {
      el.style.opacity = "1";
      el.style.transform = "none";
    });
    return;
  }

  const root =
    container === document.documentElement ||
    container === document.scrollingElement
      ? null
      : container;

  adaptiveScrollObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;

      const el = entry.target;

      if (el.dataset.scrollAnimated === "true") {
        observer.unobserve(el);
        return;
      }

      el.dataset.scrollAnimated = "true";

      AnimeBridge.run(el, {
        opacity: [0.72, 1],
        translateY: [48, 0],
        scale: [0.965, 1],
        duration: 680,
        easing: "easeOutExpo"
      });

      observer.unobserve(el);
    });
  }, {
    root,
    threshold: 0.12,
    rootMargin: "0px 0px -8% 0px"
  });

  targets.forEach(el => {
    if (el.dataset.scrollAnimated === "true") return;
    el.style.opacity = "0.72";
    el.style.transform = "translateY(48px) scale(0.965)";
    adaptiveScrollObserver.observe(el);
  });
}

function setupOutsideProductScrollAnimations() {
  setupAdaptiveScrollBehavior();
}

function setupProductHoverStagger() {
  /* Hover uses CSS-only on recommendation cards for instant, sharp feedback. */
}

function animateCardHoverIn(card) {
  if (!card || !card.isConnected) return;
  if (card.closest(".recommendation-stage.is-fast-switching")) return;

  const container = card.closest(
    ".recommendation-product-grid, .checked-products-grid, .results-grid"
  );

  const siblings = container
    ? [...container.querySelectorAll(".recommendation-product-card, .checked-product-card, .product-card")]
        .filter(item => item !== card)
    : [];

  AnimeBridge.run(card, {
    scale: [1, 1.045],
    translateY: [0, -6],
    boxShadow: [
      "0 12px 40px rgba(2,8,23,0.24)",
      "0 26px 80px rgba(59,130,246,0.28)"
    ],
    duration: 420,
    easing: "easeOutExpo"
  });

  AnimeBridge.run(siblings, {
    scale: [1, 0.985],
    opacity: [1, 0.88],
    delay: AnimeBridge.stagger(18, { from: "center" }),
    duration: 360,
    easing: "easeOutExpo"
  });
}

function animateCardHoverOut(card) {
  if (!card || !card.isConnected) return;
  if (card.closest(".recommendation-stage.is-fast-switching")) return;

  const container = card.closest(
    ".recommendation-product-grid, .checked-products-grid, .results-grid"
  );

  const cards = container
    ? container.querySelectorAll(".recommendation-product-card, .checked-product-card, .product-card")
    : [card];

  AnimeBridge.run(cards, {
    scale: 1,
    translateY: 0,
    opacity: 1,
    boxShadow: "0 12px 40px rgba(2,8,23,0.20)",
    delay: AnimeBridge.stagger(12),
    duration: 360,
    easing: "easeOutExpo"
  });
}

if (!window.__pasarIntaiCategoryEventsBound) {
  window.__pasarIntaiCategoryEventsBound = true;

  document.addEventListener("click", event => {
    const button = event.target.closest("[data-recommendation-mode]");
    if (!button) return;

    const mode = normalizeRecommendationMode(button.dataset.recommendationMode);
    if (!mode) return;

    selectRecommendationMode(mode, button);
  });
}

// Delegated modal feedback click listener
if (!window.__MARKETSPY_MODAL_FEEDBACK_BOUND__) {
  window.__MARKETSPY_MODAL_FEEDBACK_BOUND__ = true;

  document.addEventListener("click", async event => {
    const target = getEventElement(event);
    const correctBtn = target?.closest("[data-modal-feedback-correct]");
    if (correctBtn) {
      event.preventDefault();
      await handleModalFeedback("positive");
      return;
    }

    const wrongBtn = target?.closest("[data-modal-feedback-wrong]");
    if (wrongBtn) {
      event.preventDefault();

      const panel = document.querySelector(".modal-feedback-reason-panel");

      if (panel && panel.hidden) {
        revealModalReasonPanel();
        return;
      }

      const reasons = collectModalSelectedReasons();
      const note = collectModalFeedbackNote();

      await handleModalFeedback("negative", {
        reasons: reasons.length ? reasons : ["Ditandai salah oleh user"],
        note
      });

      return;
    }

    const saveWrongBtn = target?.closest("[data-modal-feedback-save]");
    if (saveWrongBtn) {
      event.preventDefault();

      const reasons = collectModalSelectedReasons();
      const note = collectModalFeedbackNote();

      await handleModalFeedback("negative", {
        reasons: reasons.length ? reasons : ["Ditandai salah oleh user"],
        note
      });

      return;
    }

    const cancelBtn = target?.closest("[data-modal-feedback-cancel]");
    if (cancelBtn) {
      event.preventDefault();
      const panel = document.querySelector(".modal-feedback-reason-panel");
      if (panel) panel.hidden = true;
      return;
    }
  });
}

const PROGRESS_STAGE_TEXT = {
  idle: "Menunggu proses...",
  start: "Menyiapkan mesin scraper...",
  opening_page: "Membuka halaman marketplace...",
  scraping: "Mengambil data produk...",
  scrolling: "Membaca produk tambahan...",
  dedupe: "Membersihkan produk duplikat...",
  budget: "Mengecek rentang budget...",
  semantic: "Mengecek relevansi produk...",
  ai: "AI sedang audit kandidat...",
  ranking: "Menyusun rekomendasi terbaik...",
  done: "Selesai — hasil siap ditampilkan",
  error: "Pipeline error — cek log"
};

let lastProgressStage = null;
let activeScrambleFrame = null;

function getProgressStage(progress) {
  if (progress?.done && progress?.error) return "error";
  if (progress?.done) return "done";

  const raw = String(
    progress?.stage ||
    progress?.status ||
    progress?.statusText ||
    ""
  ).toLowerCase();

  if (raw.includes("open") || raw.includes("page")) return "opening_page";
  if (raw.includes("scroll")) return "scrolling";
  if (raw.includes("scrap")) return "scraping";
  if (raw.includes("dedupe") || raw.includes("duplicate")) return "dedupe";
  if (raw.includes("budget")) return "budget";
  if (raw.includes("semantic")) return "semantic";
  if (raw.includes("ai") || raw.includes("classifier")) return "ai";
  if (raw.includes("rank") || raw.includes("recommend")) return "ranking";
  if (raw.includes("done") || raw.includes("complete") || raw.includes("success")) return "done";
  if (raw.includes("error") || raw.includes("failed")) return "error";

  const pct = Number(progress?.progress_percent ?? progress?.percentage ?? progress?.percent ?? 0);
  if (pct <= 5) return "start";
  if (pct <= 25) return "scraping";
  if (pct <= 45) return "dedupe";
  if (pct <= 60) return "budget";
  if (pct <= 78) return "semantic";
  if (pct <= 92) return "ai";
  if (pct < 100) return "ranking";
  return "done";
}

function startScrapingDrawableAnimation() {
  if (runningDrawableAnimation) return;

  const target = document.querySelector(".scrape-runner-path");
  if (!target) return;

  const animeGlobal = window.anime;
  const svgObj = window.svg || animeGlobal?.svg;

  if (svgObj && typeof svgObj.createDrawable === "function") {
    const [drawable] = svgObj.createDrawable(target);

    runningDrawableAnimation = AnimeBridge.run(drawable, {
      draw: ["0 0", "0 1", "1 1"],
      duration: 1800,
      loop: true,
      easing: "easeInOutSine"
    });

    return;
  }

  const length = target.getTotalLength();
  target.style.strokeDasharray = String(length);
  target.style.strokeDashoffset = String(length);

  runningDrawableAnimation = AnimeBridge.run(target, {
    strokeDashoffset: [length, 0],
    duration: 1600,
    loop: true,
    direction: "alternate",
    easing: "easeInOutSine"
  });
}

function stopScrapingDrawableAnimation() {
  if (runningDrawableAnimation && typeof runningDrawableAnimation.pause === "function") {
    runningDrawableAnimation.pause();
  }

  runningDrawableAnimation = null;
}

function syncScrapingDrawableAnimation(progress) {
  const stage = getProgressStage(progress || {});
  const hasStarted = Boolean(
    progress?.started_at_epoch_ms ||
    window.app?.state?.searchId ||
    Number(progress?.progress_percent ?? progress?.percent ?? 0) > 0
  );

  if (progress?.done || stage === "done" || stage === "error" || stage === "idle" || !hasStarted) {
    stopScrapingDrawableAnimation();
    return;
  }

  startScrapingDrawableAnimation();
}

function syncTopStatusFromProgress(progress) {
  if (!progress) return;

  if (progress.done) {
    setTopStatusWord(progress.error ? "error" : "done");
    return;
  }

  const stage = getProgressStage(progress);
  if (["error", "failed", "blocked"].includes(stage)) {
    setTopStatusWord("error");
    return;
  }

  if (stage !== "idle" && stage !== "done") {
    setTopStatusWord("running");
  }
}

function updateProgressStage(progress) {
  const nextStage = getProgressStage(progress);

  if (nextStage === lastProgressStage) return;

  lastProgressStage = nextStage;

  const text = PROGRESS_STAGE_TEXT[nextStage] || PROGRESS_STAGE_TEXT.start;

  // Update container data-progress-stage attribute
  const container = document.querySelector(".progress-clean-panel");
  if (container) {
    container.setAttribute("data-progress-stage", nextStage);
  }

  scrambleProgressTo(text, nextStage);
}

function scrambleProgressTo(targetText, stage) {
  const el = document.querySelector("#progressScrambleText");
  if (!el) return;

  if (activeScrambleFrame) {
    cancelAnimationFrame(activeScrambleFrame);
    activeScrambleFrame = null;
  }

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reduceMotion) {
    el.textContent = targetText;
    return;
  }

  const chars = "01AI<>SCRAPE{}[]#$%";
  const duration = stage === "done" || stage === "error" ? 650 : 850;
  const start = performance.now();

  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const reveal = Math.floor(targetText.length * progress);

    let output = "";

    for (let i = 0; i < targetText.length; i++) {
      output += i < reveal
        ? targetText[i]
        : chars[Math.floor(Math.random() * chars.length)];
    }

    el.textContent = output;

    if (progress < 1) {
      activeScrambleFrame = requestAnimationFrame(frame);
    } else {
      el.textContent = targetText;
      activeScrambleFrame = null;
    }
  }

  activeScrambleFrame = requestAnimationFrame(frame);
}

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

const RECOMMENDATION_SORT_MODES = [
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
      recommendationSourceProducts: [],
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
      recommendationMode: 'all',
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
    this.bindTargetPriorityInfo();
    setupProductHoverStagger();
    this.fetchAiStatus();
  }

  bindTargetPriorityInfo() {
    const toggleBtn = document.querySelector('[data-toggle-target-priority-info]');
    const content = document.querySelector('.target-priority-info-box .info-content');
    if (!toggleBtn || !content) return;

    toggleBtn.addEventListener('click', () => {
      const isHidden = content.hasAttribute('hidden');
      if (isHidden) {
        content.removeAttribute('hidden');
        content.style.height = '0px';
        content.style.opacity = '0';
        content.style.overflow = 'hidden';
        
        const height = content.scrollHeight;
        
        AnimeBridge.run(content, {
          height: [0, height],
          opacity: [0, 1],
          duration: 350,
          easing: 'easeOutQuad',
          complete: () => {
            content.style.height = 'auto';
            content.style.overflow = '';
          }
        });
        toggleBtn.classList.add('is-active');
      } else {
        content.style.overflow = 'hidden';
        const height = content.scrollHeight;
        AnimeBridge.run(content, {
          height: [height, 0],
          opacity: [1, 0],
          duration: 300,
          easing: 'easeOutQuad',
          complete: () => {
            content.setAttribute('hidden', '');
            content.style.height = '';
          }
        });
        toggleBtn.classList.remove('is-active');
      }
    });
  }

  show(panelId) {
    this.panels.forEach((id) => {
      const el = this.$(id);
      if (el) el.classList.toggle('hidden', id !== panelId);
    });
  }

  setStatus(text, cls) {
    const classMap = {
      "status-idle": "idle",
      "status-running": "running",
      "status-done": "done",
      "status-error": "error"
    };
    const textMap = {
      Menunggu: "idle",
      Siap: "idle",
      Berjalan: "running",
      Selesai: "done",
      Gagal: "error",
      Error: "error",
      Diblokir: "error"
    };

    setTopStatusWord(classMap[cls] || textMap[text] || "idle");
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
    badge.textContent = status?.ok ? 'Siap' : 'Rules saja';
    badge.className = `ai-status-badge ${status?.ok ? 'is-ready' : 'is-missing'}`;
    message.textContent = status?.ok
      ? (status.message || 'AI Orchestrator siap')
      : 'Model AI belum terinstall. Jalankan: ollama pull gemma3:4b';
    classifier.textContent = status?.classifier || 'Rules saja';
    semantic.textContent = capabilities.semantic ? 'nomic-embed-text terpasang' : 'nomic-embed-text belum ada';
    json.textContent = capabilities.json_repair ? 'phi4-mini terpasang' : 'phi4-mini belum ada';

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
    this.setStatus('Berjalan', 'status-running');
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
      startScrapingDrawableAnimation();
      this.startPolling();
    } catch (err) {
      stopScrapingDrawableAnimation();
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

  startProgressAnimation() {}
  stopProgressAnimation() {}
  startScrambleProgress() {}
  stopScrambleProgress() {}

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
    stopScrapingDrawableAnimation();
    this.state.progressStartedAtMs = null;
    this.state.estimatedCompletionEpochMs = null;
    this.state.localElapsedSeconds = 0;
    this.state.localEtaSeconds = null;
    this.state.lastEtaFallbackSignature = null;
    this.state.lastProgress = null;
    
    // Reset staged progress scramble
    lastProgressStage = null;
    if (activeScrambleFrame) {
      cancelAnimationFrame(activeScrambleFrame);
      activeScrambleFrame = null;
    }
    const scrambleEl = document.querySelector("#progressScrambleText");
    if (scrambleEl) {
      scrambleEl.textContent = "Menunggu proses...";
    }

    this.renderProgress({
      percent: 0,
      progress_percent: 0,
      stage: 'idle',
      phase: 'idle',
      message: 'Menunggu...',
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
      logs: [{ stage: 'idle', message: 'Menunggu...' }],
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

    updateProgressStage(progress);
    syncScrapingDrawableAnimation(progress);
    syncTopStatusFromProgress(progress);
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
      idle: 'Menunggu',
      preparing: 'Menyiapkan',
      scraping: 'Mengambil data',
      completed: 'Selesai',
      blocked: 'Diblokir',
      queued: 'Menunggu',
      initializing: 'Inisialisasi',
      engine_selecting: 'Memilih engine',
      launching_browser: 'Membuka browser',
      opening_page: 'Membuka halaman',
      scrolling: 'Menggulir',
      extracting: 'Mengambil data',
      puppeteer_starting: 'Puppeteer mulai',
      puppeteer_opening: 'Puppeteer membuka',
      puppeteer_query: 'Query Puppeteer',
      puppeteer_retry: 'Puppeteer ulang',
      switching_to_rollback: 'Pindah ke Selenium',
      rollback_browser_starting: 'Selenium mulai',
      rollback_opening: 'Selenium membuka',
      rollback_extracting: 'Selenium mengambil data',
      compare_filtering: 'Filter perbandingan',
      deduplicating: 'Dedup',
      budget_filtering: 'Filter budget',
      ai_filtering: 'AI Orchestrator',
      ranking: 'Ranking',
      recommendation_building: 'Rekomendasi',
      finalizing: 'Finalisasi',
      done: 'Selesai',
      error: 'Error',
      failed: 'Gagal',
      cancelled: 'Dibatalkan',
    };
    return labels[stage] || stage || 'Memproses';
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
    this.setStatus('Selesai', 'status-done');
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
    this.state.recommendationMode = 'all';
    this.state.hasUserSelectedRecommendation = false;
    this.state.autoExpandedOnce = false;
    activeRecommendationMode = 'all';
    activeModalMode = null;
    activeModalProducts = [];
    activeModalIndex = 0;
    activeModalProduct = null;
    resetReviewState();

    this.applySortMode(this.state.sortMode, false);
    this.state.recommendationSourceProducts = [...this.state.products];
    invalidateRecommendationCache();
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
        ? `<span class="compare-fail">Halaman asli: tidak - ${this.esc(item.error_type || 'tidak diketahui')}</span>`
        : pageOpened === true
          ? '<span class="compare-ok">Halaman asli: ya</span>'
          : '<span class="compare-warn">Halaman asli: tidak diketahui</span>';

      const debugFiles = (item.debug_files || []).filter(Boolean);
      const debugHtml = debugFiles.length
        ? `<div class="debug-files">${debugFiles.map(f => `<code>${this.esc(f)}</code>`).join('')}</div>`
        : '';

      card.innerHTML = `
        <strong class="compare-engine">${this.esc(item.engine)}</strong>
        ${pageStatus}
        <div class="compare-stats">
          <span>Scrape mentah: <b>${item.raw_scraped ?? item.raw_count ?? 0}</b></span>
          <span>Budget lolos: <b>${item.budget_valid_count ?? 0}</b></span>
          <span>Semantik dicek: <b>${item.result_metadata?.semantic_checked ?? 0}</b></span>
          <span>AI dicek: <b>${item.result_metadata?.classifier_checked ?? item.result_metadata?.ai_checked ?? 0}</b></span>
          <span>AI diterima: <b>${item.ai_accepted_count ?? item.result_metadata?.ai_accepted_count ?? 0}</b></span>
          <span>Durasi: ${item.duration_seconds ?? item.duration ?? 0}s</span>
          <span>Status: ${item.ok ? 'OK' : 'Gagal'}</span>
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
    this.state.recommendationMode = 'all';
    activeRecommendationMode = 'all';
    activeModalMode = null;
    activeModalProducts = [];
    activeModalIndex = 0;
    activeModalProduct = null;
    resetReviewState();
    this.state.recommendationSourceProducts = [...this.state.products];
    invalidateRecommendationCache();
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
      status.textContent = displayed >= requested ? 'Target terpenuhi' : 'Sebagian';
      status.className = `status-badge ${displayed >= requested ? 'status-done' : 'status-running'}`;
    }
  }

  renderRecommendations() {
    const panel = this.$('recommendations-panel');
    if (!panel) return;

    if (!this.state.products.length) {
      panel.classList.add('hidden');
      return;
    }

    panel.classList.remove('hidden');
    const activeMode = normalizeRecommendationMode(this.state.recommendationMode) || 'all';
    activeRecommendationMode = activeMode;
    reviewState.activeMode = activeMode;
    
    // Set active mode on stage
    const stage = document.querySelector('.recommendation-stage');
    if (stage) {
      stage.dataset.activeMode = activeMode;
    }

    this.updateRecommendationButtons(activeMode);
    updateRecommendationTitle(activeMode);
    updateRecommendationLogo(activeMode);

    this.updateRecommendationPanels(activeMode);

    renderRecommendationContent(activeMode);
    renderCheckedProductsBox(activeMode);
    setupAdaptiveScrollBehavior();
  }

  buildRecommendationBuckets() {
    const list = [
      ...(this.state.recommendationSourceProducts?.length
        ? this.state.recommendationSourceProducts
        : this.state.products)
    ];
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
    const sold = (p) => number(p.soldCount ?? p.sold_count);

    return {
      all: [...list],
      terbaik: [...list].sort((a, b) =>
        rating(b) - rating(a)
        || confidence(b) - confidence(a)
        || sold(b) - sold(a)
      ),
      termurah: [...list].sort((a, b) =>
        price(a) - price(b)
        || rating(b) - rating(a)
      ),
      trusted: [...list].sort((a, b) =>
        sold(b) - sold(a)
        || rating(b) - rating(a)
        || confidence(b) - confidence(a)
      ),
    };
  }

  createRecommendationMiniCard(product) {
    const item = this.normalizeProduct(product);
    const card = document.createElement('div');
    card.className = 'recommendation-product-card';
    const id = getProductReviewId(item);
    card.dataset.productId = id;
    card.dataset.id = id;

    const imgWrap = document.createElement('div');
    imgWrap.className = 'recommendation-product-image-wrap';

    const imageUrl = this.resolveProductImage(item);
    
    if (!imageUrl) {
      const placeholder = document.createElement("div");
      placeholder.className = "image-placeholder";
      placeholder.textContent = "Tidak ada gambar";
      imgWrap.classList.add("is-image-missing");
      imgWrap.appendChild(placeholder);
    } else {
      const img = document.createElement('img');
      img.className = 'recommendation-product-image';
      img.src = imageUrl;
      img.alt = item.title || 'Gambar produk';
      img.loading = 'lazy';
      img.onerror = () => {
        if (imageUrl && !img.dataset.proxyTried) {
          img.dataset.proxyTried = '1';
          img.src = this.proxyImageUrl(imageUrl);
          return;
        }
        handleImageError(img);
      };
      imgWrap.appendChild(img);
    }

    const details = document.createElement('div');
    details.className = 'recommendation-product-card-details';
    
    const h4 = document.createElement('h4');
    h4.className = 'recommendation-product-title';
    h4.textContent = item.title || 'Produk Tokopedia';
    
    const strong = document.createElement('div');
    strong.className = 'recommendation-product-price';
    strong.textContent = item.price || '';
    
    const span = document.createElement('div');
    span.className = 'recommendation-product-meta';
    const ratingStr = item.rating ? `⭐ ${item.rating}` : '';
    const soldStr = item.sold || item.sold_text || item.soldCount || item.sold_count ? `${item.sold || item.sold_text || item.soldCount || item.sold_count} terjual` : '';
    span.textContent = [ratingStr, soldStr].filter(Boolean).join(' | ');

    details.append(h4, strong, span);
    card.append(imgWrap, details);

    return card;
  }

  toggleRecommendations() {
    this.state.recommendationsOpen = true;
    this.renderRecommendations();
    this.expandRecommendationStage(true);
  }

  animateRecommendationProductsEnter(scopeOptions = {}) {
    const profile = getRecommendationMotionProfile();
    animateRecommendationCardsEnter(profile);
  }

  animateRecommendationProductsExit() {
    const profile = getRecommendationMotionProfile();
    return animateRecommendationCardsExit(null, profile);
  }

  async selectRecommendation(nextMode, triggerEl = null) {
    await selectRecommendationMode(nextMode, triggerEl);
  }

  updateRecommendationButtons(nextMode) {
    updateRecommendationButtons(nextMode);
  }

  updateRecommendationPanels(nextMode) {}
  renderSidePanelContent(panel, modeKey) {}
  animateSidePanels() {}

  updateRecommendationContent(nextMode) {
    const mode = normalizeRecommendationMode(nextMode) || 'all';
    renderRecommendationContent(mode);
    renderCheckedProductsBox(mode);

    setupAdaptiveScrollBehavior();
  }

  animateRecommendationStage() {
    if (!this.canAnimate()) return;
    const activePanel = document.querySelector('.recommendation-active-panel');
    const cards = document.querySelectorAll('.recommendation-product-card');
    
    AnimeBridge.run([activePanel].filter(Boolean), {
      opacity: [0, 1],
      translateY: [24, 0],
      scale: [0.96, 1],
      delay: AnimeBridge.stagger(70),
      duration: 650,
      easing: 'easeOutExpo',
    });
    
    const profile = getRecommendationMotionProfile();
    this.animateRecommendationProductsEnter(profile);
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
    AnimeBridge.run(stage, {
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
    const visibleProducts = this.state.products.filter((product) => {
      const id = getProductReviewId(product);
      return !reviewedProductIds.has(id);
    });

    if (!visibleProducts.length) {
      grid.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">?</div>
          <strong>Tidak ada produk valid untuk pilihan ini.</strong>
          <span>Coba naikkan toleransi budget, kurangi filter, atau aktifkan target-first mode.</span>
        </div>
      `;
      return;
    }
    for (const product of visibleProducts) {
      grid.appendChild(this.createCard(product));
    }
    setupOutsideProductScrollAnimations();
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
    icon.textContent = 'Tidak ada gambar';
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
    img.alt = product.title || 'Gambar produk';
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
      || (aiNumeric >= 0.85 ? 'Tinggi' : aiNumeric >= 0.70 ? 'Sedang' : 'Rendah');
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
      handleGridFeedback(id, 'positive', card);
    });

    const wrongBtn = document.createElement('button');
    wrongBtn.className = 'card-action-btn is-wrong';
    wrongBtn.dataset.feedbackWrong = 'true';
    wrongBtn.dataset.noModal = 'true';
    wrongBtn.textContent = 'Salah';
    wrongBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      e.preventDefault();
      handleGridFeedback(id, 'negative', card, { reasons: ['Ditandai salah oleh user'] });
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
      confEl.textContent = (aiValue != null && Number.isFinite(aiNumeric)) ? `🧠 Keyakinan AI: ${aiNumeric.toFixed(2)}` : '';
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
    if (window.__MARKETSPY_PRODUCT_DIALOG_BOUND__) return;
    window.__MARKETSPY_PRODUCT_DIALOG_BOUND__ = true;

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
    if (window.__MARKETSPY_CARD_CLICK_BOUND__) return;
    window.__MARKETSPY_CARD_CLICK_BOUND__ = true;

    document.addEventListener("click", (event) => {
      const target = getEventElement(event);
      const card = target?.closest(".product-card, .recommendation-product-card");
      if (!card) return;

      const clickedAction = target?.closest("button, a, [data-no-modal]");
      if (clickedAction) return;

      if (card.classList.contains("recommendation-product-card")) {
        return;
      }
    });
  }

  openRecommendationProductModal(product, sourceCardEl) {
    return openRecommendationProductModal(product, sourceCardEl);
  }

  closeRecommendationProductModal() {
    return closeRecommendationProductModal();
  }

  fillRecommendationProductModal(product) {
    return fillRecommendationModal(product);
  }

  revealModalReasonPanel() {
    return revealModalReasonPanel();
  }

  bindRecommendationModalEvents() {
    const dialog = document.querySelector("#recommendation-product-dialog");
    if (!dialog) return;
    if (window.__MARKETSPY_RECOMMENDATION_DIALOG_CLOSE_BOUND__) return;
    window.__MARKETSPY_RECOMMENDATION_DIALOG_CLOSE_BOUND__ = true;

    dialog.querySelector("[data-recommendation-modal-close]")?.addEventListener("click", () => {
      closeRecommendationProductModal();
    });

    dialog.addEventListener("click", (e) => {
      if (e.target === dialog) {
        closeRecommendationProductModal();
      }
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

  _openFeedbackModal(productId) {
    const product = this.state.products.find(
      (p) => String(p.id || p.url || p.title || '') === String(productId)
    );
    if (!product) return;
    const card = Array.from(document.querySelectorAll('.product-card'))
      .find((item) => item.dataset.id === String(productId) || item.dataset.productId === String(productId));
    this.openProductModal(product, card);
    this.revealReasonPanel();
  }

  /* ─── FLIP card exit animation for review queue ─── */
  animateCardExitAndRelayout(card) {
    if (!card) return;
    const grid = card.parentElement;
    if (!grid) { card.remove(); return; }

    // FLIP: snapshot old positions of siblings
    const siblings = Array.from(grid.querySelectorAll('.product-card, .recommendation-product-card'))
      .filter((el) => el !== card);
    const oldRects = new Map();
    siblings.forEach((el) => oldRects.set(el, el.getBoundingClientRect()));

    // Animate the card out
    if (this.canAnimate()) {
      AnimeBridge.run(card, {
        opacity: [1, 0],
        scale: [1, 0.85],
        translateX: [0, -40],
        duration: 420,
        easing: 'easeInQuad',
        complete: () => {
          card.remove();
          this._flipRelayout(grid, siblings, oldRects);
        },
      });
    } else {
      card.remove();
    }
  }

  _flipRelayout(grid, siblings, oldRects) {
    if (!this.canAnimate() || !siblings.length) return;
    siblings.forEach((el) => {
      const oldRect = oldRects.get(el);
      if (!oldRect) return;
      const newRect = el.getBoundingClientRect();
      const dx = oldRect.left - newRect.left;
      const dy = oldRect.top - newRect.top;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
      AnimeBridge.run(el, {
        translateX: [dx, 0],
        translateY: [dy, 0],
        duration: 450,
        easing: 'easeOutExpo',
      });
    });
  }

  showError(message) {
    this.stopPolling();
    this.stopElapsedTimer();
    stopScrapingDrawableAnimation();
    this.setStatus(this.isBlockedMessage(message) ? 'Diblokir' : 'Gagal', 'status-error');
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
    stopScrapingDrawableAnimation();
    if (this.recommendationObserver) this.recommendationObserver.disconnect();
    this.setStatus('Menunggu', 'status-idle');
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

// ========== PRODUCT DETAIL MODAL JS BEHAVIOR ==========

let activeDetailProduct = null;
let activeReviewQueue = [];
let activeReviewIndex = 0;

function getProductId(product) {
  return String(product?.id || product?.url || product?.product_url || product?.title || "");
}

function openProductDetailModal(product, queue = []) {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal || !product) return;

  activeDetailProduct = product;
  activeReviewQueue = Array.isArray(queue) && queue.length ? queue : [product];
  activeReviewIndex = Math.max(0, activeReviewQueue.findIndex(item => getProductId(item) === getProductId(product)));

  renderProductDetail(product);

  modal.hidden = false;
  document.documentElement.classList.add("modal-open");
  document.body.classList.add("modal-open");

  animateProductDetailModalOpen();

  const closeButton = modal.querySelector("[data-close-product-modal]");
  if (closeButton) closeButton.focus({ preventScroll: true });
}

function closeProductDetailModal() {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal) return;

  animateProductDetailModalClose(() => {
    modal.hidden = true;
    document.documentElement.classList.remove("modal-open");
    document.body.classList.remove("modal-open");
  });
}

function renderProductDetail(product) {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal || !product) return;

  const title = modal.querySelector(".product-detail-title");
  const subtitle = modal.querySelector(".product-detail-subtitle");
  const price = modal.querySelector(".product-detail-price");
  const meta = modal.querySelector(".product-detail-meta");
  const img = modal.querySelector(".product-detail-image");
  const placeholder = modal.querySelector(".product-detail-image-placeholder");
  const openLink = modal.querySelector(".feedback-open");

  if (title) title.textContent = product.title || product.name || "Produk tanpa nama";
  if (subtitle) subtitle.textContent = product.store_name || product.shop_name || product.storeName || product.shop || product.reason || "";
  if (price) price.textContent = formatRupiah(product.price_value || product.priceNumber || product.price || 0);

  if (meta) {
    const rating = product.rating || product.star || "-";
    const sold = product.sold || product.sold_count || product.soldCount || "-";
    const confidence = product.ai_confidence || product.confidenceScore || product.confidence || product.combined_score || null;

    meta.innerHTML = `
      <span>⭐ ${escapeHtml(String(rating))}</span>
      <span>🛍️ ${escapeHtml(String(sold))} terjual</span>
      ${confidence ? `<span>🧠 Keyakinan AI: ${escapeHtml(String(confidence))}</span>` : ""}
    `;
  }

  const imageUrl = product.image_url || product.image || product.img || "";

  if (img && placeholder) {
    if (imageUrl) {
      img.src = imageUrl;
      img.alt = product.title || "Gambar produk";
      img.classList.remove("is-hidden");
      placeholder.classList.add("is-hidden");
      
      img.onerror = () => {
        img.classList.add("is-hidden");
        placeholder.classList.remove("is-hidden");
      };
    } else {
      img.removeAttribute("src");
      img.classList.add("is-hidden");
      placeholder.classList.remove("is-hidden");
    }
  }

  if (openLink) {
    const url = product.url || product.link || "#";
    openLink.href = url;
    openLink.toggleAttribute("aria-disabled", !url || url === "#");
  }
}

function animateProductDetailModalOpen() {
  const modal = document.querySelector(".product-detail-modal");
  if (!modal) return;

  AnimeBridge.run(modal, {
    opacity: [0, 1],
    translateY: [28, 0],
    scale: [0.96, 1],
    duration: 1000,
    easing: "easeOutExpo"
  });
}

function animateProductDetailModalClose(done) {
  const modal = document.querySelector(".product-detail-modal");
  if (!modal) {
    if (typeof done === "function") done();
    return;
  }

  const animation = AnimeBridge.run(modal, {
    opacity: [1, 0],
    translateY: [0, 18],
    scale: [1, 0.97],
    duration: 220,
    easing: "easeInQuad"
  });

  setTimeout(() => {
    if (typeof done === "function") done();
  }, 230);
}

function goToNextReviewProduct() {
  const queue = getActiveRecommendationProducts(activeRecommendationMode);

  if (!queue.length) {
    closeProductDetailModal();
    return;
  }

  activeReviewQueue = queue;
  activeReviewIndex = 0;
  activeDetailProduct = queue[0];

  renderProductDetail(queue[0]);

  const content = document.querySelector(".product-detail-content");
  if (content) content.scrollTop = 0;

  AnimeBridge.run(".product-detail-modal", {
    opacity: [0.72, 1],
    translateX: [18, 0],
    duration: 260,
    easing: "easeOutCubic"
  });
}

// Setup product detail modal event listeners
if (!window.__pasarIntaiProductModalEventsBound) {
  window.__pasarIntaiProductModalEventsBound = true;

  document.addEventListener("click", event => {
    const close = event.target.closest("[data-close-product-modal]");
    if (close) {
      closeProductDetailModal();
      return;
    }

    const backdrop = event.target.closest("[data-product-modal]");
    const dialog = event.target.closest(".product-detail-modal");

    if (backdrop && !dialog) {
      closeProductDetailModal();
      return;
    }

    const feedbackButton = event.target.closest("[data-feedback-answer]");
    if (feedbackButton) {
      const answer = feedbackButton.dataset.feedbackAnswer;
      sendFeedback({
        product_id: getProductId(activeDetailProduct),
        feedback_type: answer,
        reasons: [],
        note: ""
      }).then(async () => {
        await moveProductToCheckedTray(activeDetailProduct, answer, {});
        goToNextReviewProduct();
      });
      return;
    }

    const productCard = event.target.closest("[data-product-card]");
    if (productCard) {
      const productId = productCard.dataset.productId;
      const product = findProductById(productId);
      const queue = getActiveRecommendationProducts(activeRecommendationMode);
      if (product) openProductDetailModal(product, queue);
    }
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      const modal = document.querySelector("[data-product-modal]");
      if (modal && !modal.hidden) closeProductDetailModal();
    }
  });
}

function findProductById(productId) {
  const id = String(productId || "");
  if (!id) return null;

  const queue = getActiveRecommendationProducts(activeRecommendationMode);
  const fromQueue = queue.find(item => getProductId(item) === id);
  if (fromQueue) return fromQueue;

  return window.__MARKETSPY_PRODUCTS__?.find(item => getProductId(item) === id) || null;
}

let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new ScraperApp();
  window.app = app;
  window.openRecommendationProductModal = openRecommendationProductModal;
  window.closeRecommendationProductModal = closeRecommendationProductModal;
  setTopStatusWord("idle");
});
