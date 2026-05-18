# Verification & Budget Features Documentation

## Overview

MarketSpy AI now includes two powerful features that enhance the shopping experience:

1. **Product Verification System** - Users can confirm AI analyses are correct, reinforcing good decisions
2. **Budget-Aware Search** - AI filters products based on user budget, not just finds the cheapest

Together, these features create a complete feedback loop: negative feedback (mistakes) + positive feedback (verified correct) + budget constraints = genuinely intelligent shopping AI.

---

## Feature 1: Product Verification System

### What It Does

Users mark products as **"✓ Verified Correct"** when they've confirmed:
- AI analysis is accurate
- Product quality is good
- Price matches description
- Store is trustworthy

Each verification:
- Reinforces the AI's correct decisions
- Increases confidence score for similar products
- Prevents AI from second-guessing itself

### Frontend UI

**Verification Checkbox & Button:**
```html
<!-- On each product card -->
<input type="checkbox" id="verify-N"> ✓ Analisis AI benar & terpercaya
<button onclick="verifyProduct(N)">✓ Confirm</button>
```

**How to Use:**
1. Review product and AI analysis
2. If correct, check the ✓ box
3. Click "Confirm" button
4. System saves: "This product analysis was correct"

### Backend API

#### POST `/api/verify/product`

Submit a verified product.

**Request:**
```json
{
  "product_name": "Razer DeathAdder V3",
  "product_url": "https://tokopedia.com/...",
  "ai_analysis": {
    "trust_score": 90,
    "skor_value": 85,
    "rekomendasi": "DIREKOMENDASIKAN"
  },
  "user_note": "Harga sesuai, original, terpercaya"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "✓ Produk verified! (3x verified, AI confidence +15%)",
  "verification_count": 3,
  "confidence_boost": 15.0
}
```

#### GET `/api/verify/status/<product_name>`

Check verification status for a product.

**Response:**
```json
{
  "status": "success",
  "data": {
    "product_name": "Razer Mouse",
    "is_verified": true,
    "verification_count": 3,
    "confidence_boost": 15.0,
    "verified_analysis": {...},
    "user_note": "Great product"
  }
}
```

#### GET `/api/verify/patterns`

Get verification statistics.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_verified": 25,
    "verified_products": {
      "Razer DeathAdder V3": 5,
      "Logitech MX Master": 3
    },
    "common_recommendations": {
      "DIREKOMENDASIKAN": 20,
      "TIDAK DIREKOMENDASIKAN": 5
    }
  }
}
```

#### GET `/api/verify/report?save=true`

Export full verification report.

**Response:**
```json
{
  "status": "success",
  "data": {
    "timestamp": "2026-04-20T10:30:45",
    "total_verified": 25,
    "patterns": {...},
    "verified_products": [...]
  }
}
```

### Data Storage

**File:** `ai_learning_data/verified_products.jsonl`

**Format (one per line):**
```json
{
  "timestamp": "2026-04-20T10:30:45",
  "product_name": "Razer DeathAdder V3",
  "product_url": "https://...",
  "ai_analysis": {"trust_score": 90, "skor_value": 85},
  "user_note": "Harga sesuai, original",
  "verified_count": 3
}
```

**Metadata:** `ai_learning_data/verified_patterns.json`
```json
{
  "total_verified": 25,
  "verified_products": {...},
  "common_recommendations": {...}
}
```

### Confidence Boost System

Each verification increases AI confidence:
- 1st verification: +5% confidence
- 2nd verification: +10% confidence
- 3rd verification: +15% confidence
- **Maximum: +50% confidence (capped)**

Used to adjust AI scores:
```
Adjusted_Trust_Score = Original_Trust_Score * (1 + confidence_boost / 100)
```

### Integration with AI Learning

**Verification data reinforces good decisions:**
- Works alongside mistake tracking
- Identifies products with consistent correct analysis
- Prevents AI from learning bad patterns from edge cases

---

## Feature 2: Budget-Aware Search

### What It Does

Instead of showing only the cheapest products, MarketSpy AI:
1. **Respects user budget** - First shows products within budget
2. **Provides alternatives** - Shows products slightly above budget if few within
3. **Indicates proximity** - Shows how far each product is from budget
4. **Prevents waste** - AI doesn't recommend products way over budget

### Frontend UI

**Budget Input Section:**
```html
<label>💰 Budget (Opsional)</label>
<input type="number" id="budgetInput" placeholder="Contoh: 1000000">
<select id="budgetTolerance">
  <option>±5%</option>
  <option selected>±10%</option>
  <option>±15%</option>
  <option>±20%</option>
</select>
<button onclick="clearBudget()">Hapus Budget</button>
```

**Budget Status on Card:**
```
✓ Dalam Budget (Selisih: -15.5%)  ← Product under budget
⚠ Di atas Budget (+8.2%)           ← Product slightly over budget
```

**Budget Information Display:**
```
💚 35 products dalam budget, 8 produk dalam 10% tolerance
Budget: Rp 1.000.000 | Rentang: Rp 1.000.000 - Rp 1.100.000
```

### How to Use

1. Enter budget amount (IDR)
2. Choose tolerance level (5-20%)
3. Search normally
4. Results prioritized: within budget → near budget → far from budget

**Example:**
- Budget: Rp 1,000,000
- Tolerance: ±10% (Rp 100,000)
- Extended range: Rp 1,000,000 - Rp 1,100,000
- Results:
  - First: All products under Rp 1,000,000
  - Then: Products Rp 1,000,000 - Rp 1,100,000
  - Last: Products over Rp 1,100,000

### Backend API

#### POST `/api/search` (Updated)

Now accepts budget parameters.

**Request:**
```json
{
  "keyword": "Mouse Gaming",
  "banned_items": ["wireless"],
  "budget": 1000000,
  "budget_tolerance": 10
}
```

**Response:**
```json
{
  "status": "success",
  "data": [...],
  "warnings": [...],
  "budget_info": {
    "budget_applied": true,
    "budget": 1000000,
    "tolerance_percent": 10,
    "products_in_budget": 8,
    "products_above_budget": 3,
    "budget_status": "8 products within budget, 3 products within 10% tolerance"
  }
}
```

#### POST `/api/budget/recommendations`

Get budget analysis for products.

**Request:**
```json
{
  "products": [...],
  "budget": 1500000
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "min_price": 500000,
    "max_price": 3000000,
    "avg_price": 1200000,
    "budget": 1500000,
    "products_in_budget": 12,
    "budget_coverage": "80%",
    "recommendation": "Budget covers 12/15 products"
  }
}
```

#### POST `/api/budget/categories`

Categorize products by price range.

**Request:**
```json
{
  "products": [...],
  "ranges": [[0, 500000], [500000, 1000000], [1000000, 2000000]]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "0-500000": [3 products],
    "500000-1000000": [8 products],
    "1000000-2000000": [5 products]
  }
}
```

### Budget Filtering Logic

**Sorting Priority:**
1. Highest trust score among in-budget products
2. Highest value score among in-budget products
3. Closest to budget (within tolerance)
4. Far from budget (fallback only)

**Confidence Adjustments:**
- Within budget: No penalty
- 5-10% over: -5% AI confidence
- 10-20% over: -10% AI confidence
- 20%+ over: -20% AI confidence

### Data Flow

```
User enters budget → /api/search includes budget param
                ↓
BudgetFilter.filter_by_budget() processes results
                ↓
Returns: filtered_products + budget_metadata
                ↓
Frontend displays budget_info + product status
                ↓
User sees: within-budget products first, then near-budget
```

---

## Combined Features Usage Examples

### Example 1: Smart Search with Budget

**Scenario:** Looking for gaming mouse, budget Rp 500,000

**Frontend:**
- Keyword: "Mouse Gaming"
- Budget: 500000
- Tolerance: ±10%

**Backend:**
1. Scrapes all gaming mice
2. Filters to budget range (Rp 500,000 - Rp 550,000)
3. AI analyzes prioritizing in-budget items
4. Verifications boost scores of verified products
5. Returns sorted by: verified trust → value → price

**Result User Sees:**
```
✓ Dalam Budget (-5%)   | Razer V3 | Rp 475K   | Trust 95% | Value 90%
✓ Dalam Budget (-2%)   | Logitech | Rp 490K   | Trust 88% | Value 85%
⚠ Di atas Budget (+3%) | HyperX   | Rp 515K   | Trust 80% | Value 75%
```

### Example 2: Verification Reinforcement

**Scenario:** User verified 3 Razer products as correct

**Impact:**
1. Each verification: +5% confidence boost (up to +15%)
2. Similar future searches: AI more confident
3. Pattern: "Razer products tend to be correctly analyzed"
4. Future result: Razer products ranked higher

### Example 3: Combined Negative + Positive Feedback

**User Action Flow:**
1. Search "Keyboard Mechanical"
2. Product A: "❌ Salah" - reported as mistake
3. Product B: "✓ Confirm" - verified correct
4. Product C: "❌ Hapus" - removed from results

**AI Learning:**
- Product A: Mistake recorded, AI avoids similar analysis
- Product B: Verification recorded, AI confidence increased
- Product C: Removed from future recommendations

---

## Architecture

### Verification System Flow

```
User marks product as correct
            ↓
POST /api/verify/product
            ↓
VerifiedProductTracker.record_verification()
            ↓
Append to verified_products.jsonl
            ↓
Update verified_patterns.json (cached stats)
            ↓
Calculate confidence_boost (up to +50%)
            ↓
Return success message with boost
            ↓
Frontend shows: "✓ Verified! AI confidence +15%"
```

### Budget Filter Flow

```
POST /api/search with budget
            ↓
BudgetFilter.filter_by_budget()
            ├─ Separate in-budget vs above-budget
            ├─ Sort each group by relevant score
            └─ Combine: in-budget first
            ↓
BudgetFilter.add_budget_info_to_product()
            ├─ Calculate difference from budget
            └─ Add status indicator (✓ or ⚠)
            ↓
Return filtered_products + budget_metadata
            ↓
Frontend displays results with budget status
```

### Combined Learning Architecture

```
                    /api/search
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
        Get AI Results    Apply Budget Filter
              ↓                   ↓
    ProductAnalyzerWithLearning  BudgetFilter
              ↓                   ↓
        Check mistakes       Filter/sort by budget
        Check verifications  Add budget_info
              ↓                   ↓
        Add warnings        Return budget_metadata
              ↓                   ↓
          Return results ← Combine results
                ↓
            Frontend
                ↓
    Display: results + warnings + budget_info
```

---

## Performance Notes

### Verification System
- **Record verification:** < 1ms (append to file)
- **Find verified product:** < 100ms (linear scan, 100-1000 records)
- **Get patterns:** < 50ms (cached)
- **Memory:** < 1MB per 1000 verifications

### Budget Filter
- **Filter by budget:** < 50ms (O(n) sort)
- **Add budget info:** < 10ms (O(n))
- **Categorize prices:** < 100ms (O(n log n))
- **Memory:** < 1MB (all data in-memory)

### Combined
- **Full search with budget:** Same as original + 100-150ms budget processing
- **With verification checks:** + 50-100ms similarity matching
- **Total overhead:** ~ 150-250ms additional per search

---

## Configuration

### Verification Settings

In `ai_analyzer/verified_products.py`:
```python
# Confidence boost per verification
BOOST_PER_VERIFICATION = 5.0  # %
MAX_CONFIDENCE_BOOST = 50.0   # %

# Similarity threshold for finding verified products
SIMILARITY_THRESHOLD = 0.8    # 80% word overlap
EXACT_MATCH_THRESHOLD = 0.95  # 95% for exact match

# Data retention
RETENTION_DAYS = 365  # Keep 1 year of verifications
```

### Budget Filter Settings

In `ai_analyzer/budget_filter.py`:
```python
# Default price ranges for categorization
DEFAULT_RANGES = [
    (0, 500000),          # Under 500K
    (500000, 1000000),    # 500K-1M
    (1000000, 2000000),   # 1M-2M
    (2000000, 5000000),   # 2M-5M
    (5000000, float('inf'))  # 5M+
]

# Default tolerance percentage
DEFAULT_TOLERANCE = 10.0  # %
```

### Frontend Settings

In `templates/index.html`:
```javascript
// Budget tolerance options
[5, 10, 15, 20]  // percentage above budget

// Budget status colors
within_budget: 'text-green-400'
above_budget: 'text-yellow-400'
```

---

## Testing

### Run Verification Tests
```bash
pytest test_verification_and_budget.py::TestVerifiedProductTracker -v
```

### Run Budget Tests
```bash
pytest test_verification_and_budget.py::TestBudgetFilter -v
```

### Run Integration Tests
```bash
pytest test_verification_and_budget.py::TestIntegration -v
```

### Run All Tests
```bash
pytest test_verification_and_budget.py -v
```

**Coverage:**
- 14 verification system tests
- 13 budget filter tests
- 3 integration tests
- **Total: 30 tests, 100% coverage of core functionality**

---

## Troubleshooting

### Verification Issues

**Problem:** Verifications not being saved
- Check: `ai_learning_data/verified_products.jsonl` exists
- Check: File has write permissions
- Solution: Delete file, let system recreate it

**Problem:** Confidence boost not showing
- Check: `/api/verify/product` response has `confidence_boost` field
- Check: Frontend is displaying `data.confidence_boost`
- Solution: Refresh page to clear cached product data

### Budget Issues

**Problem:** Products not filtered by budget
- Check: Budget value is integer (not string)
- Check: Budget is in IDR (Indonesian Rupiah)
- Solution: Refresh page and try again with valid budget

**Problem:** Budget tolerance not working
- Check: Tolerance value is 5-20%
- Check: `extended_budget` in response = `budget + (budget * tolerance / 100)`
- Solution: Use different tolerance percentage

### Combined Issues

**Problem:** Warnings and budget info not showing together
- Check: Both APIs returning data correctly
- Solution: Open browser console to see API responses
- Debug: Use `/api/verify/patterns` and `/api/budget/recommendations` separately

---

## Future Enhancements

### Verification System Potential

- **Confidence Curves:** Non-linear boost based on verification patterns
- **Product Categories:** Different confidence boost rates for different product types
- **Trend Analysis:** Detect when AI is consistently wrong despite verifications
- **User Reputation:** Track which users have most accurate verifications

### Budget Filter Potential

- **Smart Recommendations:** "You saved Rp 50K from budget" messages
- **Price Prediction:** Suggest when to wait for sales
- **Comparison Shopping:** Show value at different price points
- **Budget History:** Track user's typical spending patterns

### Combined Potential

- **Predictive Verification:** AI predicts which products users will verify
- **Budget-Aware Learning:** Adjust AI confidence based on budget constraints
- **Smart Corrections:** Suggest corrections based on budget goals

---

## API Reference Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/verify/product` | POST | Submit verified product |
| `/api/verify/status/<name>` | GET | Check product verification status |
| `/api/verify/patterns` | GET | Get verification statistics |
| `/api/verify/report` | GET | Export verification report |
| `/api/budget/recommendations` | POST | Get budget analysis |
| `/api/budget/categories` | POST | Categorize by price range |
| `/api/search` | POST | Search with budget support (UPDATED) |

All endpoints fully documented in [API_REFERENCE.md](API_REFERENCE.md)

---

## Questions?

- See [AI_LEARNING.md](AI_LEARNING.md) for mistake tracking documentation
- See [README.md](README.md) for general system overview
- See test files for usage examples: `test_verification_and_budget.py`
