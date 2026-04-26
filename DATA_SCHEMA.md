# Cloud Kitchen Review Analytics — Complete Data Schema
## For Conversational Bot / LLM Context

---

## 1. RAW INPUT SCHEMA (Zomato / Swiggy CSV)

Every incoming review file has exactly 7 columns:

| Field | Type | Nulls | Description |
|---|---|---|---|
| `Order_Id` | int64 | 0% | Unique order identifier. 10-digit integer. e.g. `7844735518` |
| `Res_id` | int64 | 0% | Restaurant/outlet ID. Same brand can have many Res_ids (one per location). e.g. `21548608` |
| `Res_name` | string | 0% | Brand name as received from platform. Has 39 raw spellings across 23 canonical brands. |
| `Date` | string | 0% | Order date. Format: `DD/MM/YYYY`. e.g. `01/03/2026`. Range in dataset: 01–19 Mar 2026. |
| `Delivery_Rating` | float64 | 100% | Delivery rating (1–5). **Entirely null in current dataset** — not used in analytics. |
| `Food_Rating` | float64 | 0% | Food rating. Values: `1.0, 2.0, 3.0, 4.0, 5.0`. No decimals other than .0. |
| `Comments` | string | 85.3% | Free-text review. 14.7% of orders have a comment. When null, treated as empty string. |

**Key numbers:**
- Total rows: 164,104
- Rows with comments: 24,147 (14.7%)
- Unique Order_Ids: 164,031 (73 duplicates exist — same order re-rated)
- Unique Res_ids: 6,836 (outlets/locations)
- Unique Res_names (raw): 39 → normalised to 23 canonical brand names

---

## 2. FOOD_RATING DISTRIBUTION

| Rating | Count | % of total | Comment rate |
|---|---|---|---|
| 1.0 | 33,559 | 20.5% | 39.1% leave a comment |
| 2.0 | 8,779 | 5.4% | 25.7% leave a comment |
| 3.0 | 12,378 | 7.5% | 15.4% leave a comment |
| 4.0 | 21,119 | 12.9% | 6.1% leave a comment |
| 5.0 | 88,269 | 53.8% | 6.3% leave a comment |

**Insight:** 1-star orders are 6x more likely to have a comment than 4–5 star orders.
The comment corpus is heavily negative-skewed.

---

## 3. BRAND NORMALISATION MAP

Raw spellings from the platform → canonical name used in analytics:

| Canonical Brand Name | Raw Variants Absorbed |
|---|---|
| Behrouz Biryani | `Behrouz biryani` |
| Dabba & Co | `Dabba & Co.` |
| Faasos - Wraps, Rolls & Shawarma | `Faasos - Wraps & Rolls`, `Faasos Signature Wraps & Rolls`, `Faasos Signature Wraps And Rolls` |
| Firangi Bake | `Firangi bake` |
| Honest bowl | `Honest Bowl` |
| Lunchbox - Meals & Thalis | `Lunch Box - Meals And Thalis` |
| Sweet Truth - Cake and Desserts | `Sweet Truth - Cake And Desserts` |
| The Biryani Life | `The biryani life` |
| The Good Bowl | `The good bowl` |
| The Pizza Project by Oven Story | `The Pizza Project By Oven Story`, `The Pizza Project By Oven story` |
| Veg Darbar by Behrouz Biryani | `Veg Darbar By Behrouz Biryani` |
| Veg Meals by Lunchbox | `Veg Meals By LunchBox`, `Veg Meals By Lunchbox` |

Brands with no variants (already canonical):
`Wendy's Burgers`, `Oven Story Pizza`, `Thalaiva Biryani`, `Makhani Darbar`,
`Shawarmajaan`, `99 Square Pizza`, `Rowdy Reddy Biryani`, `Fricken Chicken`,
`Thinsane Pizza by Oven Story`, `Dumdaar Kilo Biryani Handi`, `Dum Biryani By Punjabi Angithi`

---

## 4. COMMENT TEXT CHARACTERISTICS

### 4a. Language composition (of 24,147 comments)

| Type | Count | % | Description |
|---|---|---|---|
| English only | 22,388 | 92.7% | ASCII text, English words |
| Mixed Unicode+English | 1,668 | 6.9% | English with emoji, symbols, ❤ $% etc. |
| Hindi/Devanagari | 37 | 0.2% | Contains Unicode 0900–097F block characters |
| Pure non-English | ~54 | 0.2% | Other scripts |

### 4b. Length statistics

| Metric | Value |
|---|---|
| Minimum | 1 character |
| Maximum | 2,018 characters |
| Average | 60.7 characters |
| Median | 40 characters |
| Very short (≤ 5 chars) | 1,008 reviews |
| Long (> 200 chars) | 972 reviews |

### 4c. Unicode and special characters

**Emoji (1,505 reviews — 6.2%):**
Common patterns: `❤`, `❤️`, `😋`, `🔥`, `🤮`, `👎🏼`, `😭`, `😊`, `🙏`
Emoji are stripped/ignored during classification — patterns match on surrounding text.

**Special platform tokens:**
- `$%` appears in reviews — this is a Zomato platform rendering artefact (likely replaces emoji or special characters that failed to encode). Treated as noise, ignored in classification.

**Hindi examples:**
```
"इतना गंदा केक बता नहीं सकता हूं।"  (very bad cake)
"बकवास बेस्वाद"  (nonsense tasteless)
"मैंने अब तक का सबसे खराब आलू पराठा खाया।"  (worst aloo paratha I ever ate)
```
Note: Hindi reviews are currently classified by their English portions only. Pure Hindi reviews with no English keywords fall through to rating-based fallback.

### 4d. Common typos and phonetic spellings handled

The classifier pattern-matches these misspellings:

| Written as | Means |
|---|---|
| `tast` | taste |
| `bd test` / `very bd test` | bad taste |
| `teast` | taste |
| `packging` | packaging |
| `qulaity` | quality |
| `quantiy` | quantity |
| `burgger` | burger |
| `waist` / `wast` | waste |
| `osm` | awesome |
| `litt` | lit (slang for great) |

### 4e. Price mentions in text (212 reviews)

Pattern: `\d+ rs`, `\d+ rupees`, `rs \d+`
Examples:
- `"Very less quantity for 250 rs"`
- `"not worth for the price of 200 rupees"`
- `"charging 29 rs for that packing"`

These are captured under **Value for Money → Overpriced / Not Worth** when combined with negative sentiment.

### 4f. In-text rating mentions (136 reviews)

Some customers write their rating in the comment text:
- `"5 stars from me!"`
- `"0 rating worst quality"`
- `"2 stars only for the fries"`

These are noted but the `Food_Rating` column is authoritative — text mentions are not used to override it.

---

## 5. TOPIC & SUBTOPIC (PLUG & SUB-PLUG) TAXONOMY

Classification is first-match: the comment is tested against topics in order 1–10.
The first matching subtopic wins. If nothing matches, fallback rules apply.

### Classification priority order:

```
1. Food Quality      →  8 subtopics
2. Quantity          →  4 subtopics
3. Wrong Order       →  3 subtopics
4. Packaging         →  2 subtopics
5. Delivery          →  3 subtopics
6. Value for Money   →  2 subtopics
7. Hygiene           →  1 subtopic
8. Positive Overall  →  2 subtopics
9. App/Platform      →  2 subtopics
10. Other Feedback   →  1 subtopic (catch-all)
── No Comment        →  N/A (no text at all)
```

---

### TOPIC 1: Food Quality (12,803 reviews — 53.0%)

Most frequent topic. Covers everything about the food itself.

| Subtopic | Count | % within topic | Key trigger phrases |
|---|---|---|---|
| Taste - Bad | 8,831 | 69.1% | `bad taste`, `not tasty`, `tasteless`, `bland`, `horrible`, `bad test`, `bd test`, `waste food`, `too salty`, `too spicy`, `too sweet` |
| Taste - Good | 1,932 | 15.1% | `delicious`, `yummy`, `tasty`, `great taste`, `amazing`, `fantastic`, `loved it`, `superb` |
| Freshness - Stale/Bad Smell | 643 | 5.0% | `stale`, `bad smell`, `smell bad`, `foul smell`, `rotten`, `not fresh`, `old food`, `smelly` |
| Cooking - Undercooked | 450 | 3.5% | `undercooked`, `not cooked`, `half cooked`, `raw`, `unboiled`, `patty not cooked`, `less cooked` |
| Temperature - Cold Food | 400 | 3.1% | `cold food`, `food was cold`, `food is cold`, `cold burger`, `cold pizza`, `lukewarm`, `not hot` |
| Cooking - Overcooked/Hard | 215 | 1.7% | `overcooked`, `burnt`, `hard food`, `too hard`, `hard cake`, `not soft` |
| Texture - Soggy | 183 | 1.4% | `soggy`, `soft fries`, `not crispy`, `watery` |
| Foreign Object | 121 | 0.9% | `hair`, `stone`, `insect`, `fly`, `cockroach`, `worm`, `plastic in` |

**Real examples:**
```
1★  "the food is not good in tast"                     → Taste - Bad
5★  "Chocolate tast are very delicious."               → Taste - Good
1★  "Its cold, stale, tasteless, spilled, bad smell."  → Taste - Bad (first match)
1★  "patty not cooked properly"                        → Cooking - Undercooked
1★  "cake is not good, so hard that it was not cutting"→ Cooking - Overcooked/Hard
1★  "French fries were literally cold."                → Temperature - Cold Food
1★  "Why is there hair in the food?"                   → Foreign Object
3★  "Soggy fries, burger was okay"                     → Texture - Soggy
```

---

### TOPIC 2: Quantity (2,333 reviews — 9.7%)

Covers amount, portion size, missing items, and gravy/sauce levels.

| Subtopic | Count | % within topic | Key trigger phrases |
|---|---|---|---|
| Portion Too Small | 1,432 | 61.4% | `less quantity`, `very less`, `small portion`, `too small`, `less food`, `barely anything`, `mini portion` |
| Missing Items | 617 | 26.5% | `missing`, `not received`, `did not get`, `item missing`, `no sauce`, `no ketchup`, `no fries`, `no spoon`, `add on not` |
| Fewer Pieces | 147 | 6.3% | `fewer pieces`, `less pieces`, `less chicken`, `no chicken pieces`, `single piece` |
| Less Gravy/Sauce | 85 | 3.6% | `less gravy`, `no gravy`, `gravy less`, `less curry`, `dal less`, `rajma less` |

**Real examples:**
```
1★  "Very less quantity for 250 rs"       → Portion Too Small
1★  "did not get lemon soda"              → Missing Items
1★  "No chicken served"                   → Fewer Pieces
3★  "curry was quite less."               → Less Gravy/Sauce
```

---

### TOPIC 3: Wrong Order (604 reviews — 2.5%)

Covers items that were not what was ordered — highest safety/dietary risk topic.

| Subtopic | Count | % within topic | Key trigger phrases |
|---|---|---|---|
| Wrong Item Sent | 524 | 86.8% | `wrong item`, `wrong order`, `instead of`, `in place of`, `received instead`, `different food`, `not what i ordered` |
| Veg/Non-Veg Mix-up | 71 | 11.8% | `ordered veg` + `chicken`, `ordered chicken` + `veg`, `veg non-veg`, `vegetarian chicken`, `chicken vegetarian` |
| Wrong Variant/Size | 9 | 1.5% | `wrong variant`, `wrong size`, `wrong flavour`, `peri peri` + `regular` |

**Real examples:**
```
1★  "I ordered burger but in place of burger I get roll"          → Wrong Item Sent
1★  "ordered chicken burger, but received veg"                    → Wrong Item Sent
1★  "ordered veg received chicken biryani"                        → Veg/Non-Veg Mix-up
3★  "instead of peri peri fries, regular ones were sent."         → Wrong Item Sent
```

**⚠ High priority:** Veg/Non-Veg Mix-up has religious and medical implications (vegetarians, allergies). Flag these immediately.

---

### TOPIC 4: Packaging (264 reviews — 1.1%)

| Subtopic | Count | % within topic | Key trigger phrases |
|---|---|---|---|
| Packaging Damaged | 231 | 87.5% | `packaging bad`, `pack torn`, `spill`, `spilt`, `leaked`, `broken pack`, `not sealed`, `box broken` |
| Beverage Issue | 47 | 17.8% | `coke spill`, `bottle open`, `coke flat`, `flat coke`, `no gas`, `cold drink bad`, `coke diluted` |

Note: A review can only hit one subtopic (first match). Beverage Issue pattern is checked second.

**Real examples:**
```
4★  "Packaging not good. Food is spilt outside"          → Packaging Damaged
2★  "The bottle of coke wont open at all"                → Beverage Issue
1★  "Bad packaging, no ketchup provided."                → Packaging Damaged
```

---

### TOPIC 5: Delivery (507 reviews — 2.1%)

Note: This covers Zomato/Swiggy delivery, not kitchen fulfilment.

| Subtopic | Count | % within topic | Key trigger phrases |
|---|---|---|---|
| Late Delivery | 361 | 71.2% | `late delivery`, `delivery late`, `delayed`, `very late`, `slow delivery`, `long time` |
| Not Delivered | 120 | 23.7% | `not delivered`, `order not deliver`, `never received`, `no delivery` |
| Delivery Person | 26 | 5.1% | `delivery rude`, `rude delivery`, `delivery guy bad`, `delivery boy bad` |

---

### TOPIC 6: Value for Money (587 reviews — 2.4%)

| Subtopic | Count | % within topic | Key trigger phrases |
|---|---|---|---|
| Overpriced / Not Worth | 515 | 87.7% | `not worth`, `overpriced`, `too expensive`, `costly`, `waste of money`, `money waste`, `high price` |
| Good Value | 54 | 9.2% | `worth it`, `value for money`, `affordable`, `good price`, `great value` |

---

### TOPIC 7: Hygiene (19 reviews — 0.1%)

| Subtopic | Key trigger phrases |
|---|---|
| Unhygienic | `unhygienic`, `dirty`, `unclean`, `hair in`, `insect`, `cockroach`, `contaminated`, `filthy` |

Note: "hair in food" hits Foreign Object (Food Quality) before Hygiene due to priority order.

---

### TOPIC 8: Positive Overall (3,800 reviews — 15.7%)

| Subtopic | Count | Key trigger phrases |
|---|---|---|
| Overall Positive | 3,724 | `so good`, `very good`, `loved`, `fantastic`, `enjoyed`, `superb`, `great food`, `amazing food`, `osm` |
| Specific Praise | 76 | `best burger`, `best cake`, `best biryani`, `best pizza`, `best wrap` |

Also triggered by **rating fallback**: if rating ≥ 4.5 and no other pattern matches → Overall Positive.

---

### TOPIC 9: App/Platform (92 reviews — 0.4%)

| Subtopic | Key trigger phrases |
|---|---|
| Platform Issue | `nisha`, `rating story`, `college student`, `selena` (Zomato's fake review prompt names) |
| Offer/Promo Issue | `1get1`, `buy 1 get 1`, `offer not`, `coupon`, `discount not` |

---

### TOPIC 10: Other Feedback (2,950 reviews — 12.2%)

Catch-all. Comment exists but no pattern matched and rating is 2–4.
Examples: `"rice was not that flavourful"`, `"average"`, `"okay"`, `"Not chicken keema. It was chicken curry."`

---

### No Comment (140,145 orders — 85.3% of all orders)

No text review was left. Only `Food_Rating` is available for these orders.
These are still used in rating averages, trend lines, and KPI calculations.

---

## 6. DERIVED / ENRICHED FIELDS

These fields are added by the pipeline and stored in `reviews.pkl`:

| Field | Type | Values | How derived |
|---|---|---|---|
| `Source` | string | `"zomato"`, `"swiggy"` | Inferred from CSV filename |
| `Week` | string | `"W1"`, `"W2"`, `"W3"` | Date → day number: ≤7=W1, ≤14=W2, else=W3 |
| `Topic` | string | 10 topics + "No Comment" | Pattern matching on `Comments` |
| `Subtopic` | string | 28 subtopics + "N/A" | Pattern matching within matched topic |

---

## 7. INSIGHT GENERATION RULES

How raw data becomes dashboard insights:

### Issue rate per brand
```
issue_rate = count(topic != "Positive Overall" AND topic != "Other Feedback" AND topic != "No Comment")
             ÷ count(comments != "")
```

### Declining brand detection
```
declining = weekly_avg[W3] < weekly_avg[W1] - 0.05
drop_score = weekly_avg[W1] - weekly_avg[W3]
```

### Heatmap cell value
```
cell = count(brand X, topic Y comments) ÷ count(brand X comments) × 100
Colour: ≥15% = red(h1), ≥10% = orange(h2), ≥6% = amber(h3), ≥3% = light green(h4), <3% = green(h5)
```

### Comment rate
```
comment_rate = count(orders with non-empty comment) ÷ total_orders × 100
```

### Weekly averages
```
weekly_avg[W] = mean(Food_Rating) for all orders in that week, for that brand
```

---

## 8. NUMBERS CONVERTED TO INSIGHTS — EXAMPLES

| Raw signal | Insight generated |
|---|---|
| 71 reviews matching `veg.*non.?veg` pattern | "71 veg/non-veg mix-ups — dietary error with religious/medical implications. Immediate kitchen labelling audit required." |
| Behrouz Biryani W1=3.74, W2=3.68, W3=3.63 | "Declining 0.11 pts over 3 weeks with 20,877 orders — highest impact declining brand." |
| Food Quality = 53% of all text reviews | "Taste issues dominate — 8,831 bad taste reviews are the #1 driver of 1-star ratings." |
| 39.1% comment rate at 1-star vs 6.3% at 5-star | "Unhappy customers are 6× more likely to leave a review — the comment corpus overrepresents negatives." |
| Oven Story Pizza Delivery = 5.2% complaint rate | "Highest delivery complaint rate of all brands — check late-delivery slot patterns." |

---

## 9. BOT QUERY EXAMPLES AND EXPECTED DATA PATH

| User query | Data fields used | Computation |
|---|---|---|
| "Which brand has most taste complaints?" | `Res_name`, `Topic`, `Subtopic` | Filter Topic=Food Quality AND Subtopic=Taste-Bad, group by Res_name, count |
| "Is Behrouz improving or declining?" | `Res_name`, `Week`, `Food_Rating` | Group by Week, mean Food_Rating, compare W1 vs W3 |
| "How many wrong orders this week?" | `Topic`, `Date` | Filter Topic=Wrong Order, filter by date |
| "Top complaint for Lunchbox?" | `Res_name`, `Topic`, `Subtopic` | Filter brand, group by Topic+Subtopic, sort by count |
| "What % of reviews mention cold food?" | `Subtopic`, total `Comments` count | count(Subtopic=Temperature-Cold Food) ÷ total_comments |
| "Show me all 1-star reviews for Wendy's with packaging issues" | `Res_name`, `Food_Rating`, `Topic`, `Comments` | Filter brand + rating + topic, return raw comments |
| "Which outlet (Res_id) of Behrouz has most complaints?" | `Res_id`, `Res_name`, `Topic` | Filter brand, group by Res_id, count issue topics |
