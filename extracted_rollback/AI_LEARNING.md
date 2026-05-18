# AI Learning System - Complete Documentation

## Overview

The AI Learning System allows MarketSpy AI to **learn from its own mistakes** and continuously improve. When users identify incorrect AI analyses, the system records these mistakes and prevents them from happening again.

This is a **permanent solution** - not a workaround. The AI literally learns what it got wrong.

## Architecture

```
User Interaction
    ↓
AI Analysis (ProductAIAnalyzer)
    ↓
Results displayed on Dashboard
    ↓
User marks result as "WRONG"
    ↓
AIMistakeTracker.record_mistake()
    ├─→ Store in mistakes.jsonl
    ├─→ Analyze patterns
    └─→ Update knowledge base
    ↓
Future searches check mistakes database
    ├─→ "This product caused errors before"
    ├─→ "Here's what the correct analysis should be"
    └─→ Apply warnings/corrections
```

## Components

### 1. AIMistakeTracker (`ai_analyzer/mistake_tracker.py`)

**Core class for managing AI mistakes**

```python
tracker = AIMistakeTracker(storage_dir="ai_learning_data")
```

**Key Methods:**

#### `record_mistake()`
Records an AI mistake for learning.

```python
tracker.record_mistake(
    product_name="Razer DeathAdder V3",
    product_url="https://tokopedia.com/...",
    ai_analysis={
        "trust_score": 50,
        "skor_value": 40,
        "rekomendasi": "TIDAK DIREKOMENDASIKAN"
    },
    user_feedback="AI terlalu pesimis. Produk original dan banyak terjual",
    correction={
        "trust_score": 85,
        "skor_value": 80,
        "rekomendasi": "DIREKOMENDASIKAN"
    }
)
```

**Storage Format** (`mistakes.jsonl`):
```json
{
  "timestamp": "2026-04-20T10:30:45.123456",
  "product_name": "Razer DeathAdder V3",
  "product_url": "https://tokopedia.com/...",
  "ai_analysis": {...},
  "user_feedback": "AI terlalu pesimis...",
  "correction": {...}
}
```

#### `get_similar_mistakes(product_name, threshold=0.7)`
Finds similar past mistakes using word-based similarity.

```python
similar_mistakes = tracker.get_similar_mistakes("Razer Mouse", threshold=0.8)
# Returns: [
#   {"product_name": "Razer Mouse Gaming", ...},
#   {"product_name": "Razer Mouse Pro", ...}
# ]
```

#### `should_skip_analysis(product_name)`
Determines if a product is too problematic for AI analysis.
Returns `True` if same product caused 2+ mistakes.

```python
if tracker.should_skip_analysis("Problematic Product"):
    # Use manual analysis instead
    pass
```

#### `get_correction_for_mistake(product_name)`
Retrieves the known correct analysis for a product.

```python
correction = tracker.get_correction_for_mistake("Razer Mouse")
if correction:
    # Use this pre-verified analysis instead of re-analyzing
    use_correction(correction)
```

#### `get_patterns()`
Returns statistical analysis of AI mistakes.

```python
patterns = tracker.get_patterns()
# Returns:
# {
#   "total_mistakes": 15,
#   "problematic_products": {
#     "Razer Mouse": 3,
#     "Gaming Keyboard": 2
#   },
#   "common_feedbacks": {
#     "AI terlalu pesimis": 5,
#     "Harga salah dihitung": 3
#   }
# }
```

#### `export_mistakes_report(output_file=None)`
Generates comprehensive report of all mistakes and patterns.

```python
report = tracker.export_mistakes_report(output_file="report.json")
# Report includes: total mistakes, patterns, individual mistake details
```

### 2. ProductAnalyzerWithLearning

**Wrapper that integrates learning into analysis**

```python
learning_analyzer = ProductAnalyzerWithLearning(
    base_analyzer=ProductAIAnalyzer(),
    mistake_tracker=AIMistakeTracker()
)
```

**`analyze_with_learning()` Method:**
```python
results, warnings = await learning_analyzer.analyze_with_learning(
    products_dict=products,
    batch_size=10,
    limit=10,
    banned_items=[]
)

# warnings: ["⚠️ 'Razer Mouse' has caused AI mistakes before - results should be verified"]
```

## API Endpoints

### 1. Report AI Mistake
**POST** `/api/feedback/mistake`

Mark an AI analysis as incorrect and teach the system.

**Request:**
```json
{
  "product_name": "Razer DeathAdder V3",
  "product_url": "https://tokopedia.com/...",
  "ai_analysis": {
    "trust_score": 50,
    "skor_value": 40,
    "rekomendasi": "TIDAK DIREKOMENDASIKAN"
  },
  "feedback": "AI terlalu pesimis, produk original dan banyak terjual",
  "correction": {
    "trust_score": 85,
    "skor_value": 80,
    "rekomendasi": "DIREKOMENDASIKAN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Kesalahan tercatat! AI akan belajar dari ini untuk tidak mengulanginya lagi."
}
```

### 2. Get AI Mistake Patterns
**GET** `/api/ai-learning/patterns`

Get statistical analysis of AI mistakes.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_mistakes": 15,
    "problematic_products": {
      "Razer Mouse Gaming": 3,
      "Gaming Keyboard Mechanical": 2
    },
    "common_feedbacks": {
      "AI terlalu pesimis tentang produk original": 5
    }
  }
}
```

### 3. Export Mistakes Report
**GET** `/api/ai-learning/mistakes?save=true`

Get comprehensive report of all AI mistakes.

**Query Parameters:**
- `save`: `"true"` to save to file, `"false"` for JSON response

**Response:**
```json
{
  "status": "success",
  "data": {
    "timestamp": "2026-04-20T10:30:45",
    "total_mistakes": 15,
    "patterns": {...},
    "mistakes": [...]
  }
}
```

### 4. Check Product History
**GET** `/api/ai-learning/check/<product_name>`

Check if a product has history of causing AI mistakes.

**Response:**
```json
{
  "status": "success",
  "data": {
    "product_name": "Razer Mouse",
    "has_issues": true,
    "should_skip_ai_analysis": false,
    "similar_mistakes_count": 2,
    "known_correction": {
      "trust_score": 85,
      "skor_value": 80
    }
  }
}
```

## Data Storage

All learning data is stored locally in `ai_learning_data/` directory:

```
ai_learning_data/
├── mistakes.jsonl          # All recorded mistakes (one JSON per line)
├── corrections.jsonl       # Corrected analyses (for future reference)
└── patterns.json           # Statistical analysis of mistakes
```

**Why JSONL format for mistakes?**
- Efficient appending of new records
- Easy streaming/processing
- Each line is independent
- Can grow to millions of records without rewriting entire file

## How It Works

### Scenario: AI Gets Product Analysis Wrong

**Step 1: User searches "Razer Mouse"**
```
→ ProductAnalyzerWithLearning.analyze_with_learning()
→ Checks AIMistakeTracker for similar mistakes
→ "Razer Mouse" previously failed analysis 2 times
→ Returns warning to user
→ AI analysis results shown with ⚠️ indicator
```

**Step 2: User identifies AI was wrong**
```
User clicks "Mark as incorrect" button
Fills in:
  - What was wrong?
  - What should it have been?
```

**Step 3: Mistake recorded and learned**
```
POST /api/feedback/mistake
→ tracker.record_mistake()
→ Stored in mistakes.jsonl
→ Patterns updated
→ Next search for similar products will be aware of this mistake
```

**Step 4: Next search for same product**
```
→ Tracker finds known correction
→ Option: Apply correction or show warning
→ AI improvement over time
```

## Testing

Run the comprehensive test suite:

```bash
# All AI learning tests
pytest test_ai_learning.py -v

# Specific test class
pytest test_ai_learning.py::TestAIMistakeTracker -v

# With coverage
pytest test_ai_learning.py --cov=ai_analyzer.mistake_tracker
```

**Test Coverage:**
- ✅ Recording mistakes
- ✅ Finding similar mistakes
- ✅ String similarity algorithm
- ✅ Pattern analysis
- ✅ Report generation
- ✅ Integration with analyzer
- ✅ API endpoints

## Configuration

### Storage Directory
Default: `ai_learning_data/`

Change in code:
```python
tracker = AIMistakeTracker(storage_dir="/custom/path")
```

Or environment variable (if implemented):
```bash
export AI_LEARNING_DIR="/custom/path"
```

### Retention Policy
Clear old mistakes (older than 30 days):

```python
tracker.clear_old_mistakes(keep_days=30)
```

## Usage Examples

### Example 1: Full Feedback Workflow

```python
import requests

# 1. Get AI analysis results
response = requests.post("http://localhost:5000/api/search", json={
    "keyword": "Razer Mouse"
})
results = response.json()["data"]

# 2. User identifies mistake
wrong_result = results[0]

# 3. Report the mistake
feedback = requests.post(
    "http://localhost:5000/api/feedback/mistake",
    json={
        "product_name": wrong_result["nama_produk"],
        "product_url": wrong_result["url_produk"],
        "ai_analysis": {
            "trust_score": wrong_result["trust_score"],
            "skor_value": wrong_result["skor_value"]
        },
        "feedback": "AI terlalu pesimis, produk original banyak terjual",
        "correction": {
            "trust_score": 85,
            "skor_value": 80,
            "rekomendasi": "DIREKOMENDASIKAN"
        }
    }
)

print(feedback.json()["message"])
# "Kesalahan tercatat! AI akan belajar dari ini untuk tidak mengulanginya lagi."

# 4. Get learning patterns
patterns = requests.get("http://localhost:5000/api/ai-learning/patterns")
print(patterns.json()["data"]["total_mistakes"])
# 15
```

### Example 2: Check Product History

```python
# Before analyzing a product, check if it's problematic
history = requests.get(
    "http://localhost:5000/api/ai-learning/check/Razer%20Mouse"
).json()

if history["data"]["has_issues"]:
    print(f"⚠️ This product caused {history['data']['similar_mistakes_count']} past mistakes")
    if history["data"]["known_correction"]:
        print(f"Known correct analysis: {history['data']['known_correction']}")
```

### Example 3: Generate Report

```python
# Export all mistakes and patterns
report = requests.get(
    "http://localhost:5000/api/ai-learning/mistakes?save=true"
).json()

print(f"Total AI mistakes recorded: {report['data']['total_mistakes']}")
print(f"Most problematic products: {list(report['data']['patterns']['problematic_products'].keys())[:5]}")

# Report also saved to ai_mistakes_report.json
```

## Benefits

### For Users
- ✅ Gradual improvement in AI accuracy
- ✅ Warnings for products with history of mistakes
- ✅ Ability to help AI learn
- ✅ More trustworthy recommendations over time

### For Developers
- ✅ Clear insight into AI failure patterns
- ✅ Data-driven model/prompt improvements
- ✅ Track which product categories need work
- ✅ Historical audit trail of mistakes

### For Business
- ✅ AI gets smarter without retraining
- ✅ Continuous improvement loop
- ✅ User engagement (users help train AI)
- ✅ Competitive advantage (learning system)

## Performance Considerations

- **Storage:** JSONL format is efficient; scales to millions of records
- **Query Speed:** String similarity is O(n words); caches patterns
- **Pattern Updates:** Lightweight JSON operations; runs synchronously
- **Memory:** No large data structures; streaming operations where possible

## Future Enhancements

### Phase 2
- [ ] Machine learning to detect mistake patterns automatically
- [ ] Prompt optimization based on historical mistakes
- [ ] Automated model fine-tuning with mistake data
- [ ] Collaborative learning across users (anonymized)

### Phase 3
- [ ] A/B testing different AI models against mistake database
- [ ] Predictive analysis: "This product likely has similar issues"
- [ ] Automated feedback loop: "These types of products need different analysis"

## Troubleshooting

### Issue: Mistakes file grows too large
**Solution:** Clear old mistakes periodically
```python
tracker.clear_old_mistakes(keep_days=30)
```

### Issue: Similar mistake detection not working
**Solution:** Adjust threshold
```python
# Lower threshold = find more similar mistakes
similar = tracker.get_similar_mistakes("Product", threshold=0.5)
```

### Issue: Want to reset all learning data
**Solution:** Delete the directory
```bash
rm -rf ai_learning_data/
```

## Security Notes

- ✅ Learning data stored locally (no external API calls)
- ✅ No sensitive data in mistake records
- ✅ No authentication required for recording (can add if needed)
- ✅ No data sharing (fully local)

## Conclusion

This AI Learning System transforms MarketSpy AI from a **static model** to a **continuously improving** system. Every mistake is an opportunity to learn, and the system captures and leverages that learning automatically.

**The AI gets better with every user correction.**

That's the permanent solve - not a band-aid, but a learning feedback loop built into the system.
