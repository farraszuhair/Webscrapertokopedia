/**
 * Tokopedia Scraper frontend controller - MarketSpy AI UI
 *
 * State management and helper functions untuk rendering produk dan feedback.
 */

/* ─── HELPER FUNCTIONS ─── */

function formatPrice(value) {
  if (!value) return 'Harga tidak tersedia';
  const num = Number(value);
  if (!num) return 'Harga tidak tersedia';
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(num);
}

function formatDiscount(oldPrice, newPrice) {
  const old = Number(oldPrice);
  const newVal = Number(newPrice);
  if (old <= 0 || newVal <= 0 || newVal >= old) return '';
  const percent = Math.round((1 - newVal / old) * 100);
  return `Hemat ${percent}%`;
}

function parseCountValue(value) {
  if (value == null || value === '') return 0;
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0;

  const text = String(value).toLowerCase().trim();
  const match = text.match(/(\d+(?:[.,]\d+)?)\s*(rb|ribu|k|jt|juta|m)?/i);
  if (!match) return 0;

  const base = Number.parseFloat(match[1].replace(',', '.'));
  if (!Number.isFinite(base)) return 0;

  const unit = match[2] || '';
  if (['rb', 'ribu', 'k'].includes(unit)) return Math.round(base * 1000);
  if (['jt', 'juta', 'm'].includes(unit)) return Math.round(base * 1000000);
  return Math.round(base);
}

function formatOneDecimal(value) {
  return Number(value)
    .toFixed(1)
    .replace(/\.0$/, '')
    .replace('.', ',');
}

function formatRatingValue(rating) {
  const numeric = Number(String(rating ?? '').replace(',', '.')) || 0;
  if (!numeric) return '';
  return Number.isInteger(numeric) ? String(numeric) : formatOneDecimal(numeric);
}

function formatCompactReviewCount(value) {
  const count = parseCountValue(value);
  if (!count) return '';
  if (count >= 1000000) return `${formatOneDecimal(count / 1000000)}jt`;
  if (count >= 1000) return `${formatOneDecimal(count / 1000)}rb`;
  if (count >= 100) return `${count}+`;
  return String(count);
}

function formatCompactSoldCount(value) {
  const count = parseCountValue(value);
  const raw = String(value || '').trim();

  if (!count && raw) {
    return normalizeSoldText(raw);
  }

  if (!count) return '';
  if (count >= 1000000) return `${formatOneDecimal(count / 1000000)}jt terjual`;
  if (count >= 1000) return `${formatOneDecimal(count / 1000)}rb terjual`;
  if (count >= 100) return `${count}+ terjual`;
  return `${count} terjual`;
}

function normalizeSoldText(value) {
  if (!value) return "";
  let text = String(value).trim().replace(/\s+/g, " ");
  text = text.replace(/\s*terjual\s*terjual/gi, " terjual").trim();
  if (!/terjual/i.test(text)) text += " terjual";
  return text;
}

function hasRealAiSource(product) {
  const source = String(
    product?.decision_source ||
    product?.ai_source ||
    product?.model_used ||
    product?.selected_classifier ||
    ''
  ).toLowerCase();
  if (/(llm|ollama|classifier|semantic|model|ai)/i.test(source)) return true;
  if (/rule|fallback/i.test(source)) return false;
  return Boolean(window.app?.state?.aiStatus?.ok);
}

function isRulesFallback(product) {
  const source = String(product?.decision_source || product?.ai_source || '').toLowerCase();
  if (/rule|fallback/i.test(source) && !/(llm|ollama|classifier|semantic|ai)/i.test(source)) return true;
  if (window.app?.state?.aiStatus && window.app.state.aiStatus.ok === false) return true;
  return false;
}

function formatRating(rating, reviewCount) {
  const ratingText = formatRatingValue(rating);
  if (!ratingText) return '';
  const countStr = formatCompactReviewCount(reviewCount);
  return countStr ? `⭐ ${ratingText} (${countStr})` : `⭐ ${ratingText}`;
}

function formatSoldCount(sold) {
  return formatCompactSoldCount(sold);
}

function formatDecisionLabel(product) {
  const raw = product?.ai_confidence ?? 
              product?.confidence ?? 
              product?.combined_score ?? 
              product?.semantic_score ??
              product?.relevance_score ?? 
              product?.confidenceScore ??
              null;

  const numeric = Number(raw);
  const source = String(product?.decision_source || product?.ai_source || product?.source || '').toLowerCase();
  const isRules = /rule|fallback/.test(source) && !/(llm|ollama|classifier|model|ai)/.test(source);
  const aiEnabled =
    product?.ai_checked === true ||
    product?.ai_used === true ||
    product?.decision_source === "ai" ||
    product?.source === "ai" ||
    hasRealAiSource(product);

  if (Number.isFinite(numeric) && numeric > 0 && ((aiEnabled && !isRules) || !isRules)) {
    const percent = numeric <= 1 ? Math.round(numeric * 100) : Math.round(numeric);
    return `Keyakinan AI: ${Math.max(0, Math.min(100, percent))}%`;
  }

  return "Validasi: Rules";
}

function formatAiConfidence(product) {
  return formatDecisionLabel(product);
}

function formatRatingMeta(product) {
  const rating = Number(product?.rating) || 0;
  const reviewCount = product?.review_count || product?.rating_count || product?.reviewCount || product?.ratingCount || 0;
  const sold = product?.sold_count || product?.soldCount || product?.sold || product?.sold_text || '';
  const ratingText = formatRatingValue(rating);

  if (ratingText) {
    const reviewText = formatCompactReviewCount(reviewCount);
    if (reviewText) return `⭐ ${ratingText} (${reviewText})`;

    const soldText = formatCompactSoldCount(sold);
    return soldText ? `⭐ ${ratingText} (${soldText})` : `⭐ ${ratingText}`;
  }

  const soldText = formatCompactSoldCount(sold);
  return soldText ? `Terjual ${soldText.replace(/\s*terjual$/i, '')}` : '';
}

function getProductPriceNumber(product) {
  const direct = product?.priceNumber ?? product?.price_value ?? product?.price_val;
  const directNumber = Number(direct);
  if (Number.isFinite(directNumber) && directNumber > 0) return directNumber;

  const raw = String(product?.price_raw || product?.price_text || product?.price || '').replace(/[^\d]/g, '');
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

function getActiveBudgetInfo() {
  return window.app?.state?.budgetInfo || null;
}

function isProductOverbudget(product) {
  const budgetInfo = getActiveBudgetInfo();
  const maxBudget = Number(budgetInfo?.max ?? budgetInfo?.maxBudget ?? budgetInfo?.max_budget ?? 0);
  if (!Number.isFinite(maxBudget) || maxBudget <= 0) return false;
  const price = getProductPriceNumber(product);
  return price > maxBudget;
}

function normalizeProductImageCandidate(value) {
  if (!value) return "";
  let url = "";
  if (typeof value === "object") {
    url = String(
      value.url ||
      value.image_url ||
      value.imageUrl ||
      value.image ||
      value.thumbnail_url ||
      value.thumbnailUrl ||
      value.thumbnail ||
      value.src ||
      ""
    ).trim();
  } else {
    url = String(value).trim();
  }

  if (!url) return "";
  if (["undefined", "null", "noimage"].includes(url.toLowerCase().replace(/\s+/g, ""))) return "";
  if (url.startsWith("//")) url = `https:${url}`;
  if (/^https?:\/\//i.test(url) || /^data:image\//i.test(url)) return url;
  return "";
}

function getProductImageUrl(product) {
  const candidates = [
    product?.image_url,
    product?.imageUrl,
    product?.image,
    product?.thumbnail_url,
    product?.thumbnailUrl,
    product?.thumbnail,
    product?.thumb,
    product?.img,
    product?.picture,
    product?.photo,
    product?.product_image,
    product?.original_image_url,
    product?.media_url,
    Array.isArray(product?.images) ? product.images[0] : null,
    Array.isArray(product?.media) ? product.media[0]?.url : product?.media?.url,
    Array.isArray(product?.pictures) ? product.pictures[0]?.url : null,
    product?.media?.image,
    product?.media?.thumbnail,
  ];

  for (const candidate of candidates) {
    const url = normalizeProductImageCandidate(candidate);
    if (url) return url;
  }
  return "";
}

function getProductImage(product) {
  return getProductImageUrl(product);
}

function canProxyImageUrl(url) {
  return /^https?:\/\//i.test(String(url || ""));
}

function renderImagePlaceholderHtml(message = "Gambar tidak tersedia") {
  return `
    <div class="product-image-placeholder" aria-hidden="true">
      <strong>${escapeHtml(message)}</strong>
      <span>Produk tetap bisa dibuka lewat detail.</span>
    </div>
  `;
}

function renderProductImage(product, options = {}) {
  const imageUrl = getProductImageUrl(product);
  const className = options.className || "product-image";
  const title = product?.title || product?.name || "Gambar produk";

  if (!imageUrl) {
    return renderImagePlaceholderHtml("Gambar tidak tersedia");
  }

  return `
    <img
      class="${escapeHtml(className)}"
      src="${escapeHtml(imageUrl)}"
      data-original-src="${escapeHtml(imageUrl)}"
      alt="${escapeHtml(title)}"
      loading="lazy"
      decoding="async"
      referrerpolicy="no-referrer"
    />
    <div class="product-image-placeholder is-hidden" aria-hidden="true">
      <strong>Gambar gagal dimuat</strong>
      <span>Produk tetap bisa dibuka lewat detail.</span>
    </div>
  `;
}

function normalizeCategoryNumber(value) {
  const parsed = Number(String(value ?? '').replace(',', '.'));
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeRating(value) {
  const rating = normalizeCategoryNumber(value);
  if (rating <= 0) return 0;
  return Math.min(rating, 5) / 5;
}

function normalizeCount(value) {
  return Math.max(0, parseCountValue(value));
}

function normalizeConfidence(product) {
  const raw = product?.confidenceScore
    ?? product?.confidence
    ?? product?.ai_confidence
    ?? product?.combined_score
    ?? product?.semantic_score
    ?? product?.relevance_score
    ?? 0;
  const numeric = normalizeCategoryNumber(raw);
  if (numeric <= 0) return 0;
  return Math.min(numeric > 1 ? numeric / 100 : numeric, 1);
}

function parseCompactCount(value) {
  return parseCountValue(value);
}

function isRelevantProduct(product) {
  if (!product) return false;
  const title = String(product.title || product.name || '').trim();
  if (!title) return false;
  if (product.ai_decision === false || product.is_relevant === false || product.relevant === false) return false;

  const label = String(product.ai_label || product.relevance_label || product.label || '').toLowerCase();
  if (label.includes('tidak_relevan') || label.includes('irrelevant')) return false;
  return true;
}

function getBestProducts(products) {
  return [...(products || [])]
    .filter(isRelevantProduct)
    .sort((a, b) => getBestScore(b) - getBestScore(a));
}

function getBestScore(product) {
  const rating = Number(String(product?.rating || 0).replace(",", ".")) || 0;
  const sold = parseCompactCount(product?.sold_count || product?.soldCount || product?.sold || product?.sold_text);
  const reviews = parseCompactCount(product?.review_count || product?.rating_count || product?.reviewCount || product?.ratingCount || product?.review_text);
  const confidenceRaw = Number(product?.ai_confidence ?? product?.confidence ?? product?.combined_score ?? product?.confidenceScore ?? 0);
  const confidence = confidenceRaw > 1 ? confidenceRaw / 100 : confidenceRaw;
  const budgetBonus = product?.budget_status === "in_budget" || product?.budget_decision === "in_budget" ? 10 : 0;
  const imageBonus = getProductImageUrl(product) ? 3 : 0;

  return (
    rating * 30 +
    Math.log10(sold + 1) * 18 +
    Math.log10(reviews + 1) * 15 +
    confidence * 25 +
    budgetBonus +
    imageBonus
  );
}

function getBestReason(product) {
  const rating = Number(String(product?.rating || 0).replace(",", ".")) || 0;
  const sold = parseCompactCount(product?.sold_count || product?.soldCount || product?.sold || product?.sold_text);
  const reviews = parseCompactCount(product?.review_count || product?.rating_count || product?.reviewCount || product?.ratingCount || product?.review_text);
  const confidence = Number(product?.ai_confidence ?? product?.confidence ?? product?.combined_score ?? product?.confidenceScore ?? 0);
  const budgetStatus = product?.budget_status || product?.budget_decision;

  if (rating >= 4.8 && sold >= 1000) {
    return "Dipilih karena rating tinggi dan penjualan kuat.";
  }

  if (rating >= 4.8 && reviews >= 100) {
    return "Dipilih karena rating tinggi dan ulasan cukup banyak.";
  }

  if (confidence >= 0.85 || confidence >= 85) {
    return "Dipilih karena skor rekomendasi paling kuat.";
  }

  if (budgetStatus === "in_budget" && rating >= 4.5) {
    return "Dipilih karena masuk budget dan rating bagus.";
  }

  if (sold >= 500) {
    return "Dipilih karena performa penjualan cukup kuat.";
  }

  return "Dipilih karena paling cocok dengan pencarian dibanding kandidat lain.";
}

function getCheapestProducts(products) {
  return [...(products || [])]
    .filter(isRelevantProduct)
    .filter(product => getProductPriceNumber(product) > 0)
    .sort((a, b) => getProductPriceNumber(a) - getProductPriceNumber(b));
}

function getTrustedProducts(products) {
  return [...(products || [])]
    .filter(isRelevantProduct)
    .sort((a, b) => {
      const trustA =
        normalizeCount(a.sold_count || a.soldCount || a.sold || a.sold_text) * 0.04 +
        normalizeCount(a.review_count || a.rating_count || a.reviewCount || a.ratingCount) * 0.05 +
        normalizeRating(a.rating) * 25 +
        normalizeConfidence(a) * 20 +
        (a.is_official || a.is_mall || a.is_power_merchant ? 20 : 0);

      const trustB =
        normalizeCount(b.sold_count || b.soldCount || b.sold || b.sold_text) * 0.04 +
        normalizeCount(b.review_count || b.rating_count || b.reviewCount || b.ratingCount) * 0.05 +
        normalizeRating(b.rating) * 25 +
        normalizeConfidence(b) * 20 +
        (b.is_official || b.is_mall || b.is_power_merchant ? 20 : 0);

      return trustB - trustA;
    });
}

function getCategoryProducts(category) {
  if (!window.app || !window.app.buildRecommendationBuckets) return [];
  const normalizedMode = normalizeRecommendationMode(category) || "all";
  const buckets = window.app.buildRecommendationBuckets();
  return buckets[normalizedMode] || [];
}

/* ─── ANIMATION & TRANSFORM ─── */

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

  return { run, timeline, stagger, createLayout, stop };
})();

function getRecommendationMotionProfile() {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  return {
    duration: reduceMotion ? 0 : 300,
    enterY: 18,
    enterScale: 0.985,
    rotateX: 0,
    staggerDelay: reduceMotion ? 0 : 18,
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





let activeRecommendationMode = "all";
let recommendationCacheVersion = 0;
let recommendationProductCache = new Map();

let activeModalMode = null;
let activeModalProducts = [];
let activeModalIndex = 0;
let activeModalProduct = null;
let modalTransitionRunning = false;
let feedbackSubmitting = false;
const reviewedProductIds = new Set();
const rejectedProductIds = new Set();
const hoverTimers = new WeakMap();
const activeHoverTimerIds = new Set();
const activeHoverCards = new Set();
let checkedLayout = null;
let adaptiveScrollObserver = null;
let adaptiveScrollAnimation = null;

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
  return String(product?.id || product?.url || product?.product_url || product?.title || "").trim();
}

function getProductUrlId(product) {
  return String(product?.url || product?.product_url || "").trim();
}

function productIdentityMatches(a, b) {
  const aId = getProductReviewId(a);
  const bId = getProductReviewId(b);
  if (aId && bId && aId === bId) return true;

  const aUrl = getProductUrlId(a);
  const bUrl = getProductUrlId(b);
  return Boolean(aUrl && bUrl && aUrl === bUrl);
}

function normalizeFeedbackResult(value) {
  const normalized = String(value || "").toLowerCase().trim();
  if (["positive", "benar", "correct", "true"].includes(normalized)) return "positive";
  if (["negative", "salah", "wrong", "false"].includes(normalized)) return "negative";
  return "negative";
}

function getFeedbackStateList(key) {
  const state = window.app?.state;
  if (!state) return [];
  if (!Array.isArray(state[key])) state[key] = [];
  return state[key];
}

function findFeedbackStateIndex(list, product) {
  return list.findIndex(item => productIdentityMatches(item, product));
}

function findFeedbackStateProduct(key, product) {
  const list = getFeedbackStateList(key);
  const index = findFeedbackStateIndex(list, product);
  return index >= 0 ? list[index] : null;
}

function removeFeedbackStateProduct(key, product) {
  const list = getFeedbackStateList(key);
  const index = findFeedbackStateIndex(list, product);
  if (index >= 0) list.splice(index, 1);
}

function upsertFeedbackStateProduct(key, product, feedbackData) {
  const list = getFeedbackStateList(key);
  const payload = { ...(product || {}), ...feedbackData };
  const index = findFeedbackStateIndex(list, payload);
  if (index >= 0) {
    list[index] = { ...list[index], ...payload };
  } else {
    list.push(payload);
  }
}

function isProductReviewed(product) {
  if (!product) return false;
  return Boolean(findFeedbackStateProduct("reviewedProducts", product));
}

function isProductRejected(product) {
  if (!product) return false;
  const id = getProductReviewId(product);
  return Boolean(findFeedbackStateProduct("rejectedProducts", product) || (id && rejectedProductIds.has(id)));
}

function isProductFeedbackHandled(product) {
  return isProductReviewed(product) || isProductRejected(product);
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
  rejectedProductIds.clear();
  if (window.app?.state) {
    window.app.state.reviewedProducts = [];
    window.app.state.rejectedProducts = [];
  }
  invalidateRecommendationCache();
}

function markProductAsReviewed(product, result, extra = {}) {
  const id = getProductReviewId(product);
  if (!id) return "";
  const normalizedResult = normalizeFeedbackResult(result);
  const reviewedAt = new Date().toISOString();
  const sourceMode = activeRecommendationMode || "all";

  if (!reviewState.checkedById.has(id)) {
    reviewState.checkedOrder.push(id);
  }

  reviewState.checkedById.set(id, {
    id,
    product,
    result: normalizedResult,
    reasons: extra.reasons || [],
    note: extra.note || "",
    reviewedAt,
    sourceMode
  });

  if (normalizedResult === "positive") {
    reviewedProductIds.add(id);
    rejectedProductIds.delete(id);
    removeFeedbackStateProduct("rejectedProducts", product);
    upsertFeedbackStateProduct("reviewedProducts", product, {
      feedback: "benar",
      reviewedAt,
      sourceCategory: sourceMode,
      reasons: extra.reasons || [],
      note: extra.note || ""
    });
  } else {
    rejectedProductIds.add(id);
    reviewedProductIds.delete(id);
    removeFeedbackStateProduct("reviewedProducts", product);
    upsertFeedbackStateProduct("rejectedProducts", product, {
      feedback: "salah",
      rejectedAt: reviewedAt,
      sourceCategory: sourceMode,
      reasons: extra.reasons || [],
      note: extra.note || ""
    });
  }

  invalidateRecommendationCache();
  return id;
}

function getActiveRecommendationProducts(mode) {
  return getRecommendationProducts(mode).filter(product => {
    return !isProductFeedbackHandled(product);
  });
}

function getCheckedProductsForMode(mode) {
  const normalizedMode = normalizeRecommendationMode(mode) || "all";
  const records = reviewState.checkedOrder
    .map(id => reviewState.checkedById.get(id))
    .filter(Boolean);

  if (normalizedMode === "all") {
    return records.filter(record => record.result === "positive");
  }

  const modeProductIds = new Set(
    getRecommendationProducts(normalizedMode).map(product => getProductReviewId(product))
  );

  return records.filter(record => {
    if (record.result !== "positive") return false;
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

function updateSingleRecommendationTitle(mode) {
  updateRecommendationTitle(mode);
}

function updateRecommendationLogo(mode) {
  const iconEl = document.querySelector('.active-mode-icon');
  if (iconEl) {
    const normalizedMode = normalizeRecommendationMode(mode) || "all";
    const meta = RECOMMENDATION_MODES[normalizedMode];
    if (meta) iconEl.textContent = meta.icon;
  }
}

function renderRecommendationProductCard(product, mode = activeRecommendationMode) {
  const item = window.app && typeof window.app.normalizeProduct === "function"
    ? window.app.normalizeProduct(product)
    : { ...(product || {}) };
  const id = getProductReviewId(item);
  const imageUrl = getProductImageUrl(item);
  const title = item.title || "Produk Tokopedia";
  const normalizedMode = normalizeRecommendationMode(mode) || "all";

  // Format rating + sold
  const ratingMeta = formatRatingMeta(item);

  // Format harga
  const priceStr = formatProductPrice(item);

  // Format keyakinan AI
  const aiStr = formatDecisionLabel(item);
  const bestReason = normalizedMode === "terbaik" ? getBestReason(item) : "";

  // Overbudget badge
  const isOverbudget = isProductOverbudget(item);
  const overbudgetBadge = isOverbudget
    ? `<span class="rec-card-badge is-overbudget">Overbudget</span>`
    : '';
  
  // SUDAH DICEK badge HANYA untuk produk yang user sudah review (klik Benar)
  const checkedPill = isProductReviewed(item)
    ? '<span class="rec-checked-pill">Sudah dicek</span>'
    : '';

  const imageHtml = renderProductImage(item, { className: "recommendation-product-image" });

  // TIDAK ADA tombol Benar/Salah/Buka di card — card seluruhnya clickable buka modal
  return `
    <article class="recommendation-product-card" data-product-card data-product-id="${escapeHtml(id)}" data-id="${escapeHtml(id)}" role="button" tabindex="0" aria-label="${escapeHtml(title)}">
      ${checkedPill}
      <div class="recommendation-product-image-wrap${imageUrl ? "" : " is-image-missing"}">
        ${imageHtml}
      </div>
      <div class="recommendation-product-card-details">
        ${overbudgetBadge}
        <h4 class="recommendation-product-title">${escapeHtml(title)}</h4>
        <div class="recommendation-product-price">${escapeHtml(priceStr)}</div>
        ${ratingMeta ? `<div class="recommendation-product-rating-row"><span class="rec-rating">${escapeHtml(ratingMeta)}</span></div>` : ''}
        ${aiStr ? `<div class="rec-ai-confidence">${escapeHtml(aiStr)}</div>` : ''}
        ${bestReason ? `<p class="category-reason">${escapeHtml(bestReason)}</p>` : ''}
      </div>
    </article>
  `;
}

function setupProductImageErrorHandlers(scope = document) {
  scope.querySelectorAll(".recommendation-product-image, .product-image").forEach(img => {
    if (img.dataset.errorHandlerBound === "true") return;
    img.dataset.errorHandlerBound = "true";

    img.onerror = () => {
      const originalSrc = img.dataset.originalSrc || img.src;
      if (canProxyImageUrl(originalSrc) && window.app && typeof window.app.proxyImageUrl === "function" && !img.dataset.proxyTried) {
        img.dataset.proxyTried = "1";
        img.src = window.app.proxyImageUrl(originalSrc);
        return;
      }

      const wrapper = img.closest(".recommendation-product-image-wrap, .product-image-wrap");
      const placeholder = wrapper?.querySelector(".product-image-placeholder");
      if (placeholder) {
        const strong = placeholder.querySelector("strong");
        const span = placeholder.querySelector("span");
        if (strong) strong.textContent = "Gambar gagal dimuat";
        if (span) span.textContent = "Produk tetap bisa dibuka lewat detail.";
        placeholder.classList.remove("is-hidden");
      }
      handleImageError(img);
    };
  });
}

function renderRecommendationContent(mode) {
  const grid = document.querySelector(".recommendation-product-grid");
  if (!grid) return;

  const normalizedMode = normalizeRecommendationMode(mode) || "all";

  // Tampilkan/sembunyikan category limit bar — hanya untuk non-all
  const limitBar = document.getElementById('category-limit-bar');
  if (limitBar) {
    limitBar.classList.toggle('hidden', normalizedMode === 'all');
  }

  // Ambil category_limit dari inline input atau hidden input
  const inlineInput = document.getElementById('category_limit_inline');
  const hiddenInput = document.getElementById('category_limit');
  const rawLimit = inlineInput?.value || hiddenInput?.value || '12';
  const categoryLimit = Math.max(1, Math.min(parseInt(rawLimit, 10) || 12, 50));

  const categoryProducts = getCategoryProducts(normalizedMode);
  const isAllMode = normalizedMode === 'all';

  let displayProducts;
  let shortageMsg = '';

  if (isAllMode) {
    // Semua Barang: tampilkan semua, tidak dibatasi category_limit
    displayProducts = categoryProducts;
  } else {
    // Kategori lain: tampilkan maksimal categoryLimit, tapi tidak dipaksa penuh
    const actualCount = categoryProducts.length;
    displayProducts = categoryProducts.slice(0, categoryLimit);

    if (actualCount === 0) {
      // Tidak ada produk sama sekali
      shortageMsg = '';
    } else if (actualCount < categoryLimit) {
      // Data valid kurang dari yang diminta
      shortageMsg = `Kategori ini hanya punya ${actualCount} produk valid dari ${categoryLimit} yang diminta.`;
    }
    // Kalau actualCount >= categoryLimit: tidak perlu pesan, tampilkan categoryLimit item
  }

  let html = '';
  if (displayProducts.length === 0) {
    html = '<div class="recommendation-empty">Belum ada produk valid untuk kategori ini.</div>';
  } else {
    html = displayProducts.map(product => renderRecommendationProductCard(product, normalizedMode)).join('');
    if (shortageMsg) {
      html += `<div class="recommendation-shortage-notice">${escapeHtml(shortageMsg)}</div>`;
    }
  }

  grid.innerHTML = html;
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
      exit: 0,
      title: 0,
      enter: 0,
      stagger: 0
    };
  }

  if (isMobile) {
    return {
      exit: 120,
      title: 120,
      enter: 260,
      stagger: 16
    };
  }

  return {
    exit: 140,
    title: 140,
    enter: 300,
    stagger: 18
  };
}

function hardRenderRecommendationMode(mode) {
  const normalized = normalizeRecommendationMode(mode) || "all";
  activeRecommendationMode = normalized;
  reviewState.activeMode = normalized;

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
    stage.classList.remove("is-switching");
  }

  const panel = document.querySelector(".recommendation-active-panel");
  if (panel) panel.style.height = "";
}

async function selectRecommendationMode(nextMode, triggerButton) {
  nextMode = normalizeRecommendationMode(nextMode);
  if (!nextMode) return;
  if (nextMode === activeRecommendationMode) return;

  const stage = document.querySelector(".recommendation-stage");
  const grid = document.querySelector(".recommendation-product-grid");
  const title = document.querySelector(".recommendation-active-title");

  if (!stage || !grid || !title) {
    hardRenderRecommendationMode(nextMode);
    return;
  }

  activeRecommendationMode = nextMode;
  reviewState.activeMode = nextMode;

  if (window.app) {
    window.app.state.recommendationMode = nextMode;
    window.app.state.hasUserSelectedRecommendation = true;
  }

  const profile = getCategoryMotionProfile();
  const oldCards = [...grid.querySelectorAll("[data-product-card], .recommendation-product-card")];
  stage.classList.add("is-switching");

  if (oldCards.length > 0) {
    AnimeBridge.run(oldCards, {
      opacity: [1, 0],
      translateY: [0, -16],
      scale: [1, 0.965],
      delay: AnimeBridge.stagger(8, { from: "center", reversed: true }),
      duration: profile.exit,
      easing: "easeInQuad"
    });
  }

  await sleep(profile.exit);

  updateRecommendationButtons(nextMode);
  stage.dataset.activeMode = nextMode;

  const meta = RECOMMENDATION_MODES[nextMode];
  if (title && meta) {
    AnimeBridge.run(title, {
      opacity: [1, 0],
      translateY: [0, -8],
      duration: Math.round(profile.title * 0.45),
      easing: "easeInQuad",
      complete: () => {
        title.textContent = meta.label;
        AnimeBridge.run(title, {
          opacity: [0, 1],
          translateY: [8, 0],
          duration: Math.round(profile.title * 0.55),
          easing: "easeOutCubic"
        });
      }
    }) || (title.textContent = meta.label);
  }

  renderRecommendationContent(nextMode);
  renderCheckedProductsBox(nextMode);

  const newCards = [...grid.querySelectorAll("[data-product-card], .recommendation-product-card")];

  if (newCards.length > 0) {
    AnimeBridge.run(newCards, {
      opacity: [0, 1],
      translateY: [18, 0],
      scale: [0.985, 1],
      delay: AnimeBridge.stagger(profile.stagger, { start: 20, from: "first" }),
      duration: profile.enter,
      easing: "easeOutCubic"
    });
  }

  window.setTimeout(() => stage.classList.remove("is-switching"), profile.enter + profile.stagger * Math.min(newCards.length, 8) + 40);
}



function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, Math.max(0, Number(ms) || 0)));
}

function nextFrameTwice() {
  return new Promise(resolve => {
    const raf = window.requestAnimationFrame || (callback => window.setTimeout(callback, 16));
    raf(() => raf(resolve));
  });
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

  // Badge di kiri atas
  const badge = document.createElement("span");
  badge.className = `checked-product-badge is-${record.result === "positive" ? "positive" : "negative"}`;
  badge.textContent = record.result === "positive" ? "Benar" : "Salah";

  // Layout: gambar + info
  const layout = document.createElement("div");
  layout.className = "checked-product-layout";

  // Gambar produk
  const imageUrl = resolveProductImage(product);
  const imgWrap = document.createElement("div");
  imgWrap.className = "checked-product-image-wrap";
  if (imageUrl) {
    const img = document.createElement("img");
    img.className = "checked-product-image";
    img.src = imageUrl;
    img.alt = product.title || "Gambar produk";
    img.loading = "lazy";
    img.referrerPolicy = "no-referrer";
    img.onerror = () => {
      if (canProxyImageUrl(imageUrl) && !img.dataset.proxyTried && window.app && typeof window.app.proxyImageUrl === "function") {
        img.dataset.proxyTried = "1";
        img.src = window.app.proxyImageUrl(imageUrl);
        return;
      }
      imgWrap.innerHTML = '<div class="checked-product-img-placeholder">Tidak ada gambar</div>';
    };
    imgWrap.appendChild(img);
  } else {
    imgWrap.innerHTML = '<div class="checked-product-img-placeholder">Tidak ada gambar</div>';
  }

  // Info produk
  const info = document.createElement("div");
  info.className = "checked-product-info";

  const title = document.createElement("h4");
  title.className = "checked-product-title";
  title.textContent = product.title || "Produk Tokopedia";

  const price = document.createElement("p");
  price.className = "checked-product-price";
  price.textContent = formatProductPrice(product);

  // Rating/review, fallback ke sold count jika review count tidak tersedia.
  const ratingStr = formatRatingMeta(product);

  const metaRow = document.createElement("div");
  metaRow.className = "checked-product-meta-row";
  if (ratingStr) {
    const ratingEl = document.createElement("span");
    ratingEl.className = "checked-meta-rating";
    ratingEl.textContent = ratingStr;
    metaRow.appendChild(ratingEl);
  }

  // Keyakinan AI
  const aiStr = formatAiConfidence(product);

  const sourceMeta = document.createElement("p");
  sourceMeta.className = "checked-product-meta";
  const modeLabel = RECOMMENDATION_MODES[record.sourceMode]?.label || "Semua Barang";
  sourceMeta.textContent = `${modeLabel} · ${new Date(record.reviewedAt).toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit"
  })}`;

  info.append(title, price, metaRow);
  if (aiStr) {
    const aiEl = document.createElement("p");
    aiEl.className = "checked-product-ai";
    aiEl.textContent = aiStr;
    info.appendChild(aiEl);
  }
  info.appendChild(sourceMeta);

  // Tombol aksi
  const actions = document.createElement("div");
  actions.className = "checked-product-actions";

  const openBtn = document.createElement("a");
  openBtn.className = "checked-action-btn is-open";
  openBtn.href = product.url || product.product_url || "#";
  openBtn.target = "_blank";
  openBtn.rel = "noopener noreferrer";
  openBtn.textContent = "Buka Produk";
  actions.appendChild(openBtn);

  layout.append(imgWrap, info);
  card.append(badge, layout, actions);
  return card;
}

function renderCheckedProductsBox(mode) {
  setupCheckedProductsLayout();

  const box = document.querySelector(".checked-products-box");
  const grid = document.querySelector(".checked-products-grid");
  const count = document.querySelector(".checked-products-count");
  if (!box || !grid) return;
  const normalizedMode = normalizeRecommendationMode(mode) || "all";

  const records = getCheckedProductsForMode("all");

  if (normalizedMode !== "all" || records.length === 0) {
    box.classList.add("hidden");
    grid.innerHTML = "";
    if (count) count.textContent = "0 produk";
    return;
  }

  box.classList.remove("hidden");

  if (count) count.textContent = `${records.length} produk`;

  grid.innerHTML = "";

  records.forEach(record => grid.appendChild(createCheckedProductCard(record)));

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
  return getProductImageUrl(product);
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
  const imageUrl = getProductImageUrl(product);

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
          referrerpolicy="no-referrer"
        />
      `;

      const newImg = imgWrap.querySelector("img");
      newImg.addEventListener("error", () => {
        if (canProxyImageUrl(imageUrl) && !newImg.dataset.proxyTried && window.app && typeof window.app.proxyImageUrl === "function") {
          newImg.dataset.proxyTried = "1";
          newImg.src = window.app.proxyImageUrl(imageUrl);
          return;
        }
        imgWrap.innerHTML = `
          <div class="image-placeholder">
            <strong>Gambar gagal dimuat</strong>
            <span>Produk tetap bisa dibuka lewat detail.</span>
          </div>
        `;
      }, { once: true });
    } else {
      imgWrap.innerHTML = `
        <div class="image-placeholder">
          <strong>Gambar tidak tersedia</strong>
          <span>Produk tetap bisa dibuka lewat detail.</span>
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
  setText(".recommendation-modal-confidence", formatDecisionLabel(product));

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
    if (!isProductFeedbackHandled(candidate)) {
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
  const type = normalizeFeedbackResult(data.feedback_type || data.user_action);
  const reasons = data.reasons || [];
  const note = data.note || "";
  const userAction = type === "positive" ? "benar" : "salah";

  const product = (window.__MARKETSPY_PRODUCTS__ || []).find(p => getProductReviewId(p) === productId)
    || (activeModalProduct && getProductReviewId(activeModalProduct) === productId ? activeModalProduct : {})
    || {};
  const searchId = window.app?.state?.searchId || "unknown";
  
  const payload = {
    search_id: searchId,
    product_id: productId,
    product_title: product.title || "",
    user_action: userAction,
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

    // Cari product object dari state
    const product = (window.__MARKETSPY_PRODUCTS__ || []).find(p => getProductReviewId(p) === String(productId));
    if (product) {
      markProductAsReviewed(product, type, extra);
    }

    // Re-render recommendation content dan checked box
    renderRecommendationContent(activeRecommendationMode);
    renderCheckedProductsBox(activeRecommendationMode);

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

  let initialCheckDone = false;

  adaptiveScrollObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      const el = entry.target;

      // First callback: check if already visible during initial observe
      if (!initialCheckDone && entry.isIntersecting) {
        initialCheckDone = true;
        if (el.dataset.scrollAnimated !== "true") {
          el.dataset.scrollAnimated = "true";
          // Langsung reset ke state final tanpa initial transform delay
          el.style.opacity = "1";
          el.style.transform = "none";
          observer.unobserve(el);
          return;
        }
      }

      if (!entry.isIntersecting) return;

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
    // PERBAIKI: Jangan set initial transform jika element belum pernah diperiksa visibilitynya
    // Observer callback pertama akan handle visibility check dan decide apakah perlu initial transform
    // Untuk sekarang, set ke state final (no transform) untuk menghindari gap
    el.style.opacity = "1";
    el.style.transform = "none";
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
  if (card.closest(".recommendation-stage.is-switching")) return;

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
  if (card.closest(".recommendation-stage.is-switching")) return;

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

// Delegated listener untuk klik card kategori (buka modal) dan tombol di checked tray
if (!window.__MARKETSPY_REC_FEEDBACK_BOUND__) {
  window.__MARKETSPY_REC_FEEDBACK_BOUND__ = true;

  document.addEventListener("click", async event => {
    // Klik card kategori → buka modal detail
    const productCard = event.target.closest("[data-product-card]");
    if (productCard) {
      // Jangan buka modal kalau klik di link/button di dalam card (misal checked tray open btn)
      const clickedInteractive = event.target.closest("a, button");
      if (clickedInteractive) return;

      const productId = productCard.dataset.productId;
      if (!productId) return;

      const product = findProductById(productId);
      if (!product) return;

      // Buka modal detail dengan queue dari mode aktif
      const queue = getActiveRecommendationProducts(activeRecommendationMode);
      openProductDetailModal(product, queue);
      return;
    }

    // Klik card Hasil Review → buka modal detail
    const checkedCard = event.target.closest(".checked-product-card");
    if (checkedCard) {
      const openBtn = event.target.closest(".checked-action-btn.is-open");
      if (openBtn) return; // biarkan link buka produk jalan normal
      return;
    }
  });

  // Keyboard accessibility untuk card (Enter/Space)
  document.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const productCard = event.target.closest("[data-product-card]");
    if (!productCard) return;
    event.preventDefault();
    productCard.click();
  });
}

// Event listener untuk tombol Terapkan di category limit bar
if (!window.__MARKETSPY_CATEGORY_LIMIT_BOUND__) {
  window.__MARKETSPY_CATEGORY_LIMIT_BOUND__ = true;

  document.addEventListener("click", event => {
    const applyBtn = event.target.closest("#category-limit-apply");
    if (!applyBtn) return;
    event.preventDefault();
    renderRecommendationContent(activeRecommendationMode);
  });

  // Trigger saat user tekan Enter di input
  document.addEventListener("keydown", event => {
    if (event.key === "Enter" && event.target.id === "category_limit_inline") {
      event.preventDefault();
      renderRecommendationContent(activeRecommendationMode);
    }
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
  error: "Terjadi kesalahan — cek koneksi"
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

function setAppStatus(stateOrLabel) {
  const badge = document.querySelector("[data-app-status-badge]");
  if (!badge) return;

  const normalized = String(stateOrLabel || "idle").toLowerCase().trim();
  const stateMap = {
    idle: { label: "Siap", className: "is-idle" },
    siap: { label: "Siap", className: "is-idle" },
    running: { label: "Berjalan", className: "is-running" },
    berjalan: { label: "Berjalan", className: "is-running" },
    done: { label: "Selesai", className: "is-done" },
    selesai: { label: "Selesai", className: "is-done" },
    error: { label: "Error", className: "is-error" },
    gagal: { label: "Error", className: "is-error" },
    diblokir: { label: "Error", className: "is-error" }
  };
  const next = stateMap[normalized] || stateMap.idle;
  const textSpan = badge.querySelector(".status-badge-text");

  if (textSpan) {
    textSpan.textContent = next.label;
  } else {
    badge.textContent = next.label;
  }

  badge.classList.remove("is-idle", "is-running", "is-done", "is-error");
  badge.classList.add(next.className);
}

function syncTopStatusFromProgress(progress) {
  if (!progress) return;

  let status = "idle";

  if (progress.done) {
    status = progress.error ? "error" : "done";
  } else {
    const stage = getProgressStage(progress);
    if (["error", "failed", "blocked"].includes(stage)) {
      status = "error";
    } else if (stage !== "idle" && stage !== "done") {
      status = "running";
    }
  }

  setAppStatus(status);
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

  // Langsung set teks tanpa scramble — hindari karakter garbage
  if (reduceMotion) {
    el.textContent = targetText;
    return;
  }

  // Scramble hanya pakai karakter yang aman dan mudah dibaca
  const chars = "0123456789abcdef.";
  const duration = stage === "done" || stage === "error" ? 500 : 700;
  const start = performance.now();

  function frame(now) {
    const progress = Math.min((now - start) / duration, 1);
    const reveal = Math.floor(targetText.length * progress);

    let output = "";
    for (let i = 0; i < targetText.length; i++) {
      if (i < reveal) {
        output += targetText[i];
      } else if (targetText[i] === " ") {
        output += " ";
      } else {
        output += chars[Math.floor(Math.random() * chars.length)];
      }
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
      reviewedProducts: [],
      rejectedProducts: [],
      query: null,
      searchId: null,
      pollTimer: null,
      comparison: [],
      selectedEngine: null,
      recommendations: {},
      recommendationSourceProducts: [],
      recommendationsOpen: false,
      metadata: {},
      budgetInfo: null,
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

    setAppStatus(classMap[cls] || textMap[text] || "idle");
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
    const toleranceRaw = this.$('tolerance')?.value;
    const tol = Math.max(0, Math.min(Number.parseFloat(toleranceRaw || '0'), 100));
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
    // Update badge AI Scraper di header (selalu ada)
    const headerBadge = this.$('ai-scraper-header-badge');
    if (headerBadge) {
      const headerText = headerBadge.querySelector('.ai-scraper-header-text');
      if (status?.ok) {
        headerBadge.className = 'ai-scraper-header-badge is-active';
        if (headerText) headerText.textContent = 'AI Scraper Aktif';
      } else {
        headerBadge.className = 'ai-scraper-header-badge is-inactive';
        if (headerText) headerText.textContent = 'AI Scraper Tidak Aktif';
      }
    }

    // Update use_ai hidden input
    const useAi = this.$('use_ai');
    if (useAi) {
      // Selalu aktif — AI otomatis pakai rules kalau Ollama tidak tersedia
      useAi.value = 'true';
    }

    // Elemen-elemen berikut mungkin tidak ada di HTML baru — guard dengan optional chaining
    const badge = this.$('ai-status-badge');
    const message = this.$('ai-status-message');
    const classifier = this.$('ai-status-classifier');
    const semantic = this.$('ai-status-semantic');
    const json = this.$('ai-status-json');
    const install = this.$('ai-install-command');
    const scraperBadge = this.$('ai-scraper-badge');
    const scraperMessage = this.$('ai-scraper-message');

    if (scraperBadge) {
      scraperBadge.textContent = status?.ok ? 'AI Aktif' : 'Rules saja';
      scraperBadge.className = `ai-scraper-badge ${status?.ok ? 'is-ready' : 'is-fallback'}`;
    }
    if (scraperMessage) {
      scraperMessage.textContent = status?.ok
        ? (status.message || 'AI Orchestrator siap digunakan')
        : 'Model AI belum terinstall. Jalankan: ollama pull gemma3:4b';
    }

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
    } else {
      install.textContent = commands.join('\n');
      install.classList.remove('hidden');
    }
  }

  async startSearch() {
    const query = this.$('query')?.value.trim();
    const targetRaw = this.$('target_count')?.value ?? '';
    const parsedTarget = Number.parseInt(targetRaw, 10);
    const target = Number.isFinite(parsedTarget) && parsedTarget > 0 ? parsedTarget : 50;
    const toleranceRaw = this.$('tolerance')?.value;
    const tolerance = toleranceRaw ? Number.parseFloat(toleranceRaw) : 0;
    // AI selalu aktif — otomatis pakai rules kalau Ollama tidak tersedia
    const ai = true;
    const engineMode = 'auto';
    const targetFirstMode = true; // selalu aktif agar target terpenuhi
    const budget = this.getBudgetText();

    console.log('[FORM] submit triggered');
    console.log('[FORM] payload', { query, target, budget, tolerance, ai, engineMode });

    if (!query) {
      this.setStatus('Error', 'status-error');
      this.$('query')?.focus();
      return;
    }

    this.state.query = query;
    this.state.comparison = [];
    this.state.selectedEngine = null;
    this.state.recommendations = {};
    this.state.budgetInfo = null;
    this.state.recommendationsOpen = false;
    this.state.sortMode = this.activeSortMode();
    this.show('progress-panel');
    this.resetProgress();
    this.setStatus('Berjalan', 'status-running');

    try {
      console.log('[SCRAPE] request started');
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
      console.log('[SCRAPE] response', data);
      if (!data.success) {
        this.showError(data.error || 'Gagal memulai scraping');
        return;
      }
      this.state.searchId = data.search_id;
      this.state.progressStartedAtMs = data.started_at_epoch_ms || null;
      if (this.state.progressStartedAtMs) this.startElapsedTimer();
      setAppStatus("running");
      this.startPolling();
    } catch (err) {
      console.error('[SCRAPE] error', err);
      setAppStatus("error");
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
    setAppStatus("idle");
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
    this.state.budgetInfo = data.budget_info || null;
    this.state.engineMode = data.engine_mode || 'auto';
    this.state.metadata.engine_mode = this.state.engineMode;
    this.state.sortMode = data.sort_mode || this.state.metadata.sort_mode || this.state.sortMode || 'terbaik';
    this.state.recommendationsOpen = true;
    this.state.recommendationMode = 'all';
    this.state.hasUserSelectedRecommendation = false;
    // Tandai sudah auto-expanded agar observer tidak trigger expand lagi
    this.state.autoExpandedOnce = true;
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

    // Langsung expand stage tanpa animasi height agar tidak ada gap
    const stage = this.$('recommendation-stage');
    if (stage) {
      stage.classList.add('is-auto-expanded');
      // Hapus inline height kalau ada sisa dari animasi sebelumnya
      stage.style.height = '';
      stage.style.overflow = '';
    }

    console.log('[LAYOUT] scraping finished');
    console.log('[LAYOUT] render recommendations initial');
    console.log('[LAYOUT] active category', activeRecommendationMode);
    const stageHeight = stage?.offsetHeight || 0;
    const panelHeight = this.$('recommendations-panel')?.offsetHeight || 0;
    console.log('[LAYOUT] recommendation container height', { stageHeight, panelHeight });

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
    this.state.budgetInfo = budgetInfo || null;
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
    this.state.budgetInfo = item.budget_info || null;
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

    // Update header count
    this.setText('r-count', displayed || this.state.products.length || 0);
    this.setText('r-target', requested || '-');

    // Update hidden stat IDs (masih dipakai internal)
    const raw = Number(meta.raw_scraped_count ?? meta.raw_scraped ?? data.raw_count ?? 0);
    const deduped = Number(meta.deduped_count ?? data.deduped_count ?? 0);
    const budget = Number(meta.budget_valid_count ?? data.budget_valid_count ?? data.budget_count ?? 0);
    const semanticChecked = Number(meta.semantic_checked ?? meta.semantic_checked_count ?? 0);
    const aiChecked = Number(meta.classifier_checked ?? meta.ai_checked ?? data.ai_checked ?? 0);
    const aiAccepted = Number(meta.ai_accepted ?? meta.ai_accepted_count ?? data.ai_accepted_count ?? 0);
    const aiCallsAttempted = Number(meta.ai_calls_attempted ?? 0);
    const aiCallsSucceeded = Number(meta.ai_calls_succeeded ?? 0);

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
      status.textContent = displayed >= requested ? 'Selesai' : 'Sebagian';
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
    const list = [...(this.state.products || [])];

    return {
      all: [...list],
      terbaik: getBestProducts(list),
      termurah: getCheapestProducts(list),
      trusted: getTrustedProducts(list),
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
      img.referrerPolicy = 'no-referrer';
      img.onerror = () => {
        if (canProxyImageUrl(imageUrl) && !img.dataset.proxyTried) {
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
    const ratingNum = Number(item.rating) || 0;
    const reviewCount = Number(item.review_count || item.reviewCount || 0);
    const ratingStr = ratingNum > 0 ? formatRating(ratingNum, reviewCount) : '';
    const soldRaw = item.sold || item.sold_text || item.soldCount || item.sold_count || '';
    const soldStr = soldRaw ? formatSoldCount(soldRaw) : '';
    span.textContent = [ratingStr, soldStr].filter(Boolean).join(' · ');

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
    // Animasi hanya pada cards, bukan pada container panel
    // translateY pada active-panel menyebabkan gap visual sementara
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

    // Langsung tambah class tanpa animasi height — height animasi adalah penyebab gap
    stage.classList.add('is-auto-expanded');
    // Pastikan tidak ada inline height yang tersisa
    stage.style.height = '';
    stage.style.overflow = '';

    // Animasi cards saja, bukan height container
    if (this.canAnimate()) {
      this.animateRecommendationStage();
    }
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
    // Produk ditampilkan di dalam recommendation-product-grid (mode "all")
    // #products-grid tidak dipakai lagi — semua ada di dalam recommendation-stage
    // Pastikan grid lama kosong agar tidak ada card liar di luar container
    const grid = this.$('products-grid');
    if (grid) grid.innerHTML = '';
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
    invalidateRecommendationCache();
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
    return getProductImageUrl(product) || null;
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
    const icon = document.createElement('strong');
    icon.textContent = text || 'Gambar tidak tersedia';
    const label = document.createElement('span');
    label.textContent = 'Produk tetap bisa dibuka lewat detail.';
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
    img.referrerPolicy = 'no-referrer';
    img.onerror = () => {
      if (canProxyImageUrl(imageUrl) && !img.dataset.proxyTried) {
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
    if (product.rating) {
      const reviewCount = Number(product.review_count || product.reviewCount || 0);
      this.appendText(meta, 'product-rating', formatRating(Number(product.rating), reviewCount), 'span');
    }
    if (soldText) {
      const soldFormatted = formatSoldCount(soldText);
      this.appendText(meta, 'product-sold', soldFormatted, 'span');
    }
    if (shopName) this.appendText(meta, 'product-shop', shopName, 'span');
    if (shopLocation) this.appendText(meta, 'product-location', shopLocation, 'span');
    body.appendChild(meta);

    const badges = document.createElement('div');
    badges.className = 'product-badges';
    // Overbudget badge otomatis
    if (product.outside_budget || product.target_first_fallback) {
      const overBadge = this.createBadge('Overbudget');
      overBadge.className = 'product-badge is-overbudget';
      badges.appendChild(overBadge);
    }
    badges.appendChild(this.createBadge(formatDecisionLabel(product)));
    const learnedAdjustment = Number(product.learned_adjustment ?? 0);
    if (Number.isFinite(learnedAdjustment) && Math.abs(learnedAdjustment) > 0) {
      const sign = learnedAdjustment > 0 ? '+' : '';
      badges.appendChild(this.createBadge(`Learned ${sign}${learnedAdjustment.toFixed(2)}`));
    }
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
      delete img.dataset.proxyTried;
      img.src = imageUrl || '';
      img.referrerPolicy = 'no-referrer';
      img.onerror = () => {
        if (canProxyImageUrl(imageUrl) && !img.dataset.proxyTried) {
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
      const ratingNum = Number(product.rating) || 0;
      const reviewCount = Number(product.review_count || product.reviewCount || 0);
      let ratingStr = '';
      if (ratingNum > 0) {
        let countStr = '';
        if (reviewCount >= 1000) countStr = `${(reviewCount / 1000).toFixed(1).replace('.', ',')}rb`;
        else if (reviewCount > 0) countStr = `${reviewCount}+`;
        ratingStr = countStr ? `⭐ ${ratingNum} (${countStr})` : `⭐ ${ratingNum}`;
      }
      ratingEl.textContent = ratingStr;
      ratingEl.style.display = ratingStr ? 'inline' : 'none';
    }

    const soldEl = dialog.querySelector(".product-modal-sold");
    if (soldEl) {
      const soldRaw = product.sold || product.sold_text || product.soldCount || product.sold_count || '';
      const soldStr = soldRaw ? formatSoldCount(soldRaw) : '';
      soldEl.textContent = soldStr ? `🛍️ ${soldStr}` : '';
      soldEl.style.display = soldStr ? 'inline' : 'none';
    }

    const confEl = dialog.querySelector(".product-modal-confidence");
    if (confEl) {
      const confStr = formatDecisionLabel(product);
      confEl.textContent = confStr;
      confEl.style.display = confStr ? 'inline' : 'none';
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
let isReviewTransitioning = false;

const DETAIL_FEEDBACK_REASONS = [
  "Produk tidak relevan",
  "Cuma aksesoris",
  "Spesifikasi tidak sesuai query",
  "Harga tidak sesuai",
  "Nama produk salah",
  "Gambar tidak sesuai",
  "Toko tidak terpercaya",
  "Duplikat",
  "Bukan sesuai intent pencarian",
  "Data tidak lengkap",
  "Lainnya"
];

function getProductId(product) {
  return String(product?.id || product?.url || product?.product_url || product?.title || "");
}

function openProductDetailModal(product, queue = []) {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal || !product) return;

  activeDetailProduct = product;
  activeReviewQueue = Array.isArray(queue) && queue.length ? queue : [product];
  activeReviewIndex = activeReviewQueue.findIndex(item => getProductId(item) === getProductId(product));

  renderProductDetail(product);
  resetProductDetailPanelsState();

  modal.hidden = false;
  document.documentElement.classList.add("modal-open");
  document.body.classList.add("modal-open");

  animateProductDetailModalOpen();

  const closeButton = modal.querySelector("[data-close-product-modal]");
  if (closeButton) closeButton.focus({ preventScroll: true });
}

function unlockProductDetailModalScroll() {
  document.documentElement.classList.remove("modal-open");
  document.body.classList.remove("modal-open");
}

function closeProductDetailModal() {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal) {
    unlockProductDetailModalScroll();
    return;
  }

  animateProductDetailModalClose(() => {
    modal.hidden = true;
    unlockProductDetailModalScroll();
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
    const ratingStr = formatRatingMeta(product);
    const aiStr = formatAiConfidence(product);
    const parts = [ratingStr, aiStr].filter(Boolean);
    meta.innerHTML = parts.map(p => `<span>${escapeHtml(p)}</span>`).join('');
  }

  const imageUrl = resolveProductImage(product);

  if (img && placeholder) {
    if (imageUrl) {
      delete img.dataset.proxyTried;
      img.src = imageUrl;
      img.alt = product.title || "Gambar produk";
      img.referrerPolicy = "no-referrer";
      img.classList.remove("is-hidden");
      placeholder.classList.add("is-hidden");
      
      img.onerror = () => {
        if (canProxyImageUrl(imageUrl) && !img.dataset.proxyTried && window.app && typeof window.app.proxyImageUrl === "function") {
          img.dataset.proxyTried = "1";
          img.src = window.app.proxyImageUrl(imageUrl);
          return;
        }
        placeholder.innerHTML = "<strong>Gambar gagal dimuat</strong><span>Produk tetap bisa dibuka lewat detail.</span>";
        img.classList.add("is-hidden");
        placeholder.classList.remove("is-hidden");
      };
    } else {
      placeholder.innerHTML = "<strong>Gambar tidak tersedia</strong><span>Produk tetap bisa dibuka lewat detail.</span>";
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

  ensureDetailReasonPanel();
  resetDetailFeedbackPanel();
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

function getProductDetailContent() {
  return document.querySelector("#productDetailContent");
}

function getProductDetailTransitionTargets() {
  return [
    document.querySelector("#productDetailImagePanel"),
    document.querySelector("#productDetailInfoPanel")
  ].filter(Boolean);
}

function resetProductDetailPanelsState() {
  getProductDetailTransitionTargets().forEach(panel => {
    panel.style.opacity = "";
    panel.style.transform = "";
    panel.style.filter = "";
  });
}

function setReviewButtonsDisabled(disabled) {
  const modal = document.querySelector("[data-product-modal]");
  if (!modal) return;

  modal
    .querySelectorAll("[data-feedback-answer], [data-detail-feedback-save], [data-detail-feedback-cancel], .feedback-open")
    .forEach(control => {
      if (control.tagName === "A") {
        control.setAttribute("aria-disabled", disabled ? "true" : "false");
        control.tabIndex = disabled ? -1 : 0;
        control.style.pointerEvents = disabled ? "none" : "";
      } else {
        control.disabled = disabled;
      }
    });
}

function ensureDetailReasonPanel() {
  const grid = document.querySelector("[data-detail-feedback-reason-grid]");
  if (!grid || grid.children.length) return;

  DETAIL_FEEDBACK_REASONS.forEach(reason => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "feedback-reason-chip";
    chip.dataset.detailFeedbackReason = reason;
    chip.dataset.reason = reason;
    chip.textContent = reason;
    chip.addEventListener("click", event => {
      event.preventDefault();
      if (isReviewTransitioning) return;
      chip.classList.toggle("is-selected");
    });
    grid.appendChild(chip);
  });
}

function resetDetailFeedbackPanel() {
  const panel = document.querySelector("[data-detail-feedback-reason-panel]");
  if (panel) panel.hidden = true;

  document
    .querySelectorAll("[data-detail-feedback-reason-grid] .feedback-reason-chip")
    .forEach(chip => chip.classList.remove("is-selected"));

  const note = document.querySelector("[data-detail-feedback-note]");
  if (note) note.value = "";
}

function revealDetailReasonPanel() {
  const panel = document.querySelector("[data-detail-feedback-reason-panel]");
  if (!panel || !panel.hidden) return;

  panel.hidden = false;

  AnimeBridge.run(panel, {
    opacity: [0, 1],
    translateY: [12, 0],
    duration: 220,
    easing: "easeOutCubic"
  });
}

function collectDetailFeedbackReasons() {
  const chips = document.querySelectorAll("[data-detail-feedback-reason-grid] .feedback-reason-chip.is-selected");
  return Array.from(chips).map(chip => chip.dataset.reason || chip.textContent.trim()).filter(Boolean);
}

function collectDetailFeedbackNote() {
  return document.querySelector("[data-detail-feedback-note]")?.value.trim() || "";
}

async function animateProductDetailOut() {
  const imagePanel = document.querySelector("#productDetailImagePanel");
  const infoPanel = document.querySelector("#productDetailInfoPanel");
  const targets = [imagePanel, infoPanel].filter(Boolean);

  if (!targets.length || !window.anime) return;

  await anime({
    targets,
    opacity: [1, 0],
    translateX: (el, i) => i === 0 ? [0, -24] : [0, -30],
    scale: [1, 0.99],
    duration: 240,
    delay: anime.stagger(25),
    easing: "easeInOutQuad"
  }).finished;
}

async function animateProductDetailIn() {
  const imagePanel = document.querySelector("#productDetailImagePanel");
  const infoPanel = document.querySelector("#productDetailInfoPanel");
  const targets = [imagePanel, infoPanel].filter(Boolean);

  if (!targets.length || !window.anime) return;

  if (typeof anime.set === "function") {
    anime.set(targets, {
      opacity: 0,
      translateX: 28,
      scale: 0.99
    });
  } else {
    targets.forEach(panel => {
      panel.style.opacity = "0";
      panel.style.transform = "translateX(28px) scale(0.99)";
    });
  }

  await anime({
    targets,
    opacity: [0, 1],
    translateX: [28, 0],
    scale: [0.99, 1],
    duration: 300,
    delay: anime.stagger(35),
    easing: "easeOutCubic"
  }).finished;
}

function waitForProductImageReady() {
  const img = document.querySelector("#productDetailImagePanel img");

  if (!img || img.classList.contains("is-hidden")) {
    return Promise.resolve();
  }

  if (img.complete) {
    return Promise.resolve();
  }

  return new Promise(resolve => {
    let settled = false;
    const done = () => {
      if (settled) return;
      settled = true;
      img.onload = null;
      img.onerror = null;
      resolve();
    };

    img.onload = done;
    img.onerror = done;
    window.setTimeout(done, 350);
  });
}

async function submitProductFeedback(feedbackPayload = {}) {
  if (!activeDetailProduct) throw new Error("Tidak ada produk aktif untuk direview.");

  const product = activeDetailProduct;
  const verdict = String(feedbackPayload.verdict || "").toLowerCase();
  const type = verdict === "correct" || verdict === "benar" || verdict === "positive"
    ? "positive"
    : "negative";
  const reasons = Array.isArray(feedbackPayload.reasons) ? feedbackPayload.reasons : [];
  const note = feedbackPayload.note || "";

  await sendFeedback({
    product_id: getProductId(product),
    feedback_type: type,
    reasons,
    note
  });

  return { product, type, reasons, note };
}

function moveToNextReviewProduct() {
  const queue = activeReviewQueue.length
    ? activeReviewQueue
    : getActiveRecommendationProducts(activeRecommendationMode);

  for (let index = activeReviewIndex + 1; index < queue.length; index += 1) {
    const candidate = queue[index];
    if (!isProductFeedbackHandled(candidate)) {
      activeReviewQueue = queue;
      activeReviewIndex = index;
      activeDetailProduct = candidate;
      return true;
    }
  }

  const refreshedQueue = getActiveRecommendationProducts(activeRecommendationMode);
  const nextProduct = refreshedQueue.find(product => !isProductFeedbackHandled(product));
  if (!nextProduct) {
    activeReviewQueue = refreshedQueue;
    activeReviewIndex = -1;
    activeDetailProduct = null;
    return false;
  }

  activeReviewQueue = refreshedQueue;
  activeReviewIndex = refreshedQueue.findIndex(product => getProductId(product) === getProductId(nextProduct));
  activeDetailProduct = nextProduct;
  return true;
}

function getCurrentReviewProduct() {
  return activeDetailProduct;
}

function renderProductDetailModal(product) {
  renderProductDetail(product);
}

async function goToNextReviewProduct(feedbackPayload) {
  if (isReviewTransitioning) return;
  isReviewTransitioning = true;

  try {
    setReviewButtonsDisabled(true);

    const submitted = await submitProductFeedback(feedbackPayload);

    // Tandai produk sebagai reviewed dan update tray
    const checkedTrayPromise = moveProductToCheckedTray(submitted.product, submitted.type, {
      reasons: submitted.reasons,
      note: submitted.note
    }).catch(error => console.error("[CHECKED_TRAY_TRANSITION_FAILED]", error));

    // Re-render recommendation grid agar card yang sudah direview hilang
    renderRecommendationContent(activeRecommendationMode);

    await animateProductDetailOut();

    const hasNext = moveToNextReviewProduct();

    if (!hasNext) {
      await checkedTrayPromise;
      closeProductDetailModal();
      showSmallToast("Semua produk sudah direview.");
      return;
    }

    renderProductDetailModal(getCurrentReviewProduct());
    await waitForProductImageReady();
    await animateProductDetailIn();
    await checkedTrayPromise;
  } catch (err) {
    console.error("[REVIEW_NEXT_TRANSITION_FAILED]", err);
    showSmallToast("Feedback gagal disimpan. Coba lagi.");
  } finally {
    setReviewButtonsDisabled(false);
    isReviewTransitioning = false;
  }
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

    const disabledLink = event.target.closest(".feedback-open[aria-disabled='true']");
    if (disabledLink) {
      event.preventDefault();
      return;
    }

    const feedbackButton = event.target.closest("[data-feedback-answer]");
    if (feedbackButton) {
      event.preventDefault();
      if (isReviewTransitioning) return;

      const answer = feedbackButton.dataset.feedbackAnswer;

      if (answer === "salah") {
        revealDetailReasonPanel();
        return;
      }

      goToNextReviewProduct({
        verdict: "correct"
      });
      return;
    }

    const saveWrongButton = event.target.closest("[data-detail-feedback-save]");
    if (saveWrongButton) {
      event.preventDefault();
      if (isReviewTransitioning) return;

      const reasons = collectDetailFeedbackReasons();
      const note = collectDetailFeedbackNote();

      goToNextReviewProduct({
        verdict: "wrong",
        reasons: reasons.length ? reasons : ["Ditandai salah oleh user"],
        note
      });
      return;
    }

    const cancelWrongButton = event.target.closest("[data-detail-feedback-cancel]");
    if (cancelWrongButton) {
      event.preventDefault();
      if (isReviewTransitioning) return;

      const panel = document.querySelector("[data-detail-feedback-reason-panel]");
      if (panel) panel.hidden = true;
      return;
    }

    // Klik card produk ditangani oleh __MARKETSPY_REC_FEEDBACK_BOUND__ listener
    // Tidak perlu handler di sini untuk menghindari double-open
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
  setAppStatus("idle");
});
