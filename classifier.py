import re

# ── Primary taxonomy (phrase-level patterns, checked first) ─────────────────
TAXONOMY = {
    "Food Quality": {
        "Taste - Bad":
            r"bad taste|not tasty|tasteless|no taste|bland|blant|bad test|bd test"
            r"|not good taste|waste food|horrible taste|worst taste|bad flavor|no flavor"
            r"|too salty|too spicy|too sweet|too sour|over spiced|under spiced"
            r"|not delicious|disgusting|awful|substandard|very bad|horrible|pathetic.*food"
            r"|bakwas|bakwaas|bekar|faltu|ghatiya|shitty|shit food|trash food"
            r"|third.?class|ek dum bekar|bilkul bakwas|bahut bekar|बकवास"
            r"|not good at all|not at all good|no good|not satisfied|not happy|disappointed"
            r"|fraud|not authentic|not up to mark|not upto mark|below average|poor quality"
            r"|not recommended|too cold|very cold|food.*(is|was) cold|cold.*(food|pizza|biryani|burger|rice)"
            r"|delivered cold|pizza not hot|not at all hot"
            r"|bad in taste|taste very bad|taste is bad|test not good|no test|very bad test",
        "Taste - Good":
            r"delicious|yummy|yum|tasty|great taste|good taste|loved the taste|amazing taste"
            r"|fantastic|wonderful taste|nice taste|excellent taste|loved it|awesome taste"
            r"|perfect taste|best taste|superb taste|osm|soo tasty|so tasty|testy|testy food"
            r"|super tasty|taste is super|ultimate taste|authentic taste|soo good"
            r"|it.?s (too )?good|too good|must.?try|goog food|supper food|woow|wooow",
        "Temperature - Cold Food":
            r"cold food|food was cold|food is cold|cold burger|cold pizza|cold rice"
            r"|cold curry|cold chicken|lukewarm|not hot|not warm|food cold",
        "Freshness - Stale/Bad Smell":
            r"stale|bad smell|smell bad|foul smell|rotten|not fresh|old food|smelly"
            r"|expired|gone bad|odour|odor|spoiled food|rotten food|food was stale",
        "Cooking - Undercooked":
            r"undercooked|not cooked|half cooked|raw|unboiled|not properly cooked"
            r"|not fully cooked|poorly cooked|patty not cooked|less cooked|not done"
            r"|uncooked food|uncooked rice|rice not boiled|not well cooked",
        "Cooking - Overcooked/Hard":
            r"overcooked|burnt|hard food|too hard|very hard cake|hard cake|not soft"
            r"|its burned|burnt food|burnt pizza|over.?cooked",
        "Foreign Object":
            r"hair|stone|insect|fly|cockroach|worm|foreign object|found.*in food|plastic in",
        "Texture - Soggy":
            r"soggy|soft fries|limp|not crispy|fries.*cold|watery",
    },
    "Quantity": {
        "Portion Too Small":
            r"less quantity|very less|quantity.*less|portion.*small|small portion"
            r"|quantity is less|very small|too small|less food|very less food|less amount"
            r"|amount.*less|small serving|serving.*less|less serving|miniature|barely anything"
            r"|not enough food|low quantity|poor quantity|quantity low|quantity is low"
            r"|worst quantity|less quality|very small",
        "Missing Items":
            r"missing|not received|didn.t get|did not get|not get|item.*missing|where is my"
            r"|incomplete order|absent|not included|no sauce|no ketchup|no fries|no drink"
            r"|no spoon|no cutlery|no tissue|add on.*not|addon.*not|no masala|no rajma"
            r"|no salad|coke is missing|egg was missing|items missing|order missing",
        "Less Gravy/Sauce":
            r"less gravy|no gravy|gravy.*less|less curry|curry.*less|dry.*curry"
            r"|sauce.*less|less sauce|dal.*less|less dal|rajma.*less",
        "Fewer Pieces":
            r"fewer pieces|less pieces|chicken.*less|pieces.*less|less chicken|no chicken"
            r"|chicken pieces.*less|not enough pieces|one piece only|single piece|less pieces",
    },
    "Wrong Order": {
        "Wrong Item Sent":
            r"wrong item|wrong order|different item|instead of|in place of|got.*instead"
            r"|received.*instead|sent.*wrong|wrong food|not what i ordered"
            r"|ordered.*but.*got|ordered.*but.*received|different food|wrong item sent",
        "Veg/Non-Veg Mix-up":
            r"ordered veg.*chicken|ordered chicken.*veg|veg.*non.?veg|non.?veg.*veg"
            r"|chicken.*instead.*veg|veg.*instead.*chicken|vegetarian.*chicken|chicken.*vegetarian",
        "Wrong Variant/Size":
            r"wrong variant|wrong size|wrong flavour|wrong flavor|different flavour"
            r"|peri peri.*regular|regular.*peri peri",
    },
    "Packaging": {
        "Packaging Damaged":
            r"packaging.*bad|bad packaging|pack.*torn|torn.*pack|spill|spilt|leaked|leaking"
            r"|broken.*pack|damaged.*pack|not sealed|open.*pack|pack.*open|box.*broken"
            r"|container.*broken|worst pack(aging|ing|age)?|poor pack(aging|ing)?|bad pack(aging|ing)?",
        "Beverage Issue":
            r"coke.*spill|drink.*spill|coke.*tight|bottle.*open|coke.*flat|flat coke"
            r"|no gas|cold drink.*bad|soda.*missing|lemon soda|coke.*diluted",
    },
    "Delivery": {
        "Late Delivery":
            r"late delivery|delivery late|delayed|very late|too late|long time"
            r"|waited.*long|taking.*long|slow delivery|delay|order delayed|order delay"
            r"|very delayed|delivery.*late|slow delivery|worst delivery|bad delivery",
        "Not Delivered":
            r"not delivered|order not deliver|delivery not done|no delivery"
            r"|didn.t deliver|never received|not yet delivered",
        "Delivery Person":
            r"delivery.*rude|rude delivery|delivery guy.*bad|delivery boy.*bad|delivery person.*bad",
    },
    "Value for Money": {
        "Overpriced / Not Worth":
            r"not worth|overpriced|too expensive|costly|waste of money|money waste"
            r"|very costly|price.*high|high price|not worth the price|not worth the money"
            r"|expensive|waste money|worthless|worth less|not worthy|west of money"
            r"|over.?priced|shit food",
        "Good Value":
            r"worth it|value for money|affordable|reasonable price|good price|great value"
            r"|cheap and good|best value|money worth",
    },
    "Hygiene": {
        "Unhygienic":
            r"unhygienic|not hygienic|dirty|unclean|hair in|found.*hair|insect"
            r"|cockroach|fly in food|contaminated|filthy",
    },
    "Positive Overall": {
        "Overall Positive":
            r"so good|very good|really good|loved|fantastic|wonderful|enjoyed|superb"
            r"|best order|will order again|keep it up|great food|good food|amazing food"
            r"|nice food|excellent food|osm|awesome food|fabulous|perfect food|lovely"
            r"|good service|fast delivery|on time|good delivery|nice service|good experience"
            r"|satisfied|satisfactory|worth it|must try|always best|good job|great job"
            r"|thank you|thanks|keep it up|good one|good person|good boy|loved it",
        "Specific Praise":
            r"best burger|best cake|best biryani|best pizza|best wrap|loved the burger"
            r"|pizza.*amazing|biryani.*great|cake.*delicious|cheesecake.*delicious"
            r"|best biryani|best shawarma|yummy biryani|good biryani",
    },
    "App/Platform": {
        "Platform Issue":    r"nisha|rating.*story|story.*rating|college student|selena|zomato.*issue|app.*issue",
        "Offer/Promo Issue": r"1get1|buy.*1.*get.*1|offer.*not|not.*offer|coupon|discount.*not|promo",
    },
}

# ── Short/slang exact-match patterns (checked BEFORE main taxonomy for 1-3 word reviews) ──
# Each entry: (topic, subtopic, compiled_regex)
SLANG_PATTERNS = [
    # Neutral/ambiguous FIRST so avarage/average don't hit Taste-Bad
    ("Other Feedback", "General Comment", re.compile(
        r"^(ok+|okay+|okish|ok\s+ok|okay\s+okay|just\s+ok|average|avg|avarage"
        r"|not\s+so\s+good|not\s+that\s+good|better|na|hi|let|very|a|\.+|…+"
        r"|thank\w*|thanks)\s*[!.]*\s*$",
        re.IGNORECASE
    )),
    # ── POSITIVE ──────────────────────────────────────────────────────────────
    ("Positive Overall", "Overall Positive", re.compile(
        r"^(good|goo+d|gu+d|gd|v\s*good|nice|nyc|wow|osm|awesome|super|superb"
        r"|fabulous|fab|amazing|fantastic|perfect|must.?try|yum+|testy|testi"
        r"|so+o?\s+tasty|it.?s\s+(too\s+)?good|too\s+good|super\s+tasty"
        r"|ultimate\s+taste|authentic\s+taste|goog|supper|wooow?|brilliant"
        r"|lovely|satisfied|satisfactory|worth\s+it|keep\s+it\s+up|good\s+job"
        r"|great\s+job|good\s+service|nice\s+service|fast\s+delivery|on\s+time"
        r"|good\s+delivery|good\s+experience|nice\s+delivery|good\s+person"
        r"|good\s+boy|thank\s*you|thanks|thankyou|thank|loved\s+it|love\s+it"
        r"|i\s+love\s+it|must\s+try|always\s+best)\s*[!.😊👍🙂🤌🥰]*\s*$",
        re.IGNORECASE
    )),
    ("Positive Overall", "Overall Positive", re.compile(
        r"^\s*[👍👌🤌🥰😋😁☺😊🙂🫶🤩]+\s*$"  # positive emoji only
    )),
    ("Food Quality", "Taste - Good", re.compile(
        r"^(good\s+taste|nice\s+taste|great\s+taste|taste\s+is\s+(good|super|great)"
        r"|taste\s+good|taste\s+was\s+good|it.?s\s+good|food\s+is\s+(good|awesome)"
        r"|good\s+food|nice\s+food|excellent\s+food|amazing\s+food|delicious\s+food"
        r"|tasty\s+food|yummy\s+food|super\s+food|awesome\s+food|best\s+food"
        r"|good\s+pizza|nice\s+pizza|very\s+nice|very\s+good|very\s+tasty"
        r"|very\s+delicious|so\s+tasty|soo\s+tasty|food\s+was\s+(good|tasty|awesome)"
        r"|really\s+awesome|just\s+amazing|super\s+👍|good\s+👍|nice\s+👍|good\s+😊"
        r"|loved\s+the\s+taste|loved\s+the\s+food|food\s+is\s+awesome"
        r"|taste\s+so\s+good|it.?s\s+too\s+good)\s*[!.😋👍]*\s*$",
        re.IGNORECASE
    )),

    # ── NEGATIVE — Taste ──────────────────────────────────────────────────────
    ("Food Quality", "Taste - Bad", re.compile(
        r"^(bad|very\s+bad|so\s+bad|too\s+bad|no\s+good|not\s+good|not\s+nice"
        r"|not\s+good\s+at\s+all|not\s+at\s+all\s+good|it.?s\s+not\s+good"
        r"|poor|poor\s+taste|poor\s+food|bad\s+food|bad\s+quality"
        r"|bakwas|bak+w[ao]+s|bakwaas|bekar|faltu|ghatiya|fraud"
        r"|shitty|shitty\s+food|shit\s+food|shit\s+taste|trash|trash\s+food"
        r"|terrible|disgusting|worse|worest|wrost|very\s+worst|worst\s+ever"
        r"|horrible|pathetic|pathetic\s+food|pathetic\s+taste|third.?class"
        r"|ek\s+dum\s+bekar|bilkul\s+bakwas|बकवास|बहुत\s+बेकार"
        r"|not\s+satisfied|not\s+happy|disappointed|i\s+don.?t\s+like"
        r"|below\s+average|very\s+average|average\s+taste|average\s+food"
        r"|not\s+recommended|not\s+authentic|improve\s+taste|bad\s+experience"
        r"|not\s+up\s+to\s+mark|not\s+upto\s+mark|less\s+quality|no\s+test"
        r"|test\s+not\s+good|not\s+(good\s+)?te[a]?st|very\s+bad\s+food"
        r"|not\s+worth\s+it|waste|waste\s+food|shame|bad\s+in\s+taste"
        r"|taste\s+very\s+bad|taste\s+is\s+bad|very\s+bad\s+test"
        r"|not\s+testy|taste\s+less|tasteless\s+food|taste\s+less\s+food"
        r"|ghatiya|bakwas\s+taste|so\s+sweet|too\s+sweet|avarage|avarage\s+food"
        r"|baad|not\s+so\s+(tasty|good)|not\s+nice|it\s+was\s+not\s+good)\s*[!.😡👎😣🤮💩]*\s*$",
        re.IGNORECASE
    )),
    ("Food Quality", "Taste - Bad", re.compile(
        r"^\s*[👎😡😣🤮💩😔]+\s*$"  # negative emoji only
    )),

    # ── NEGATIVE — Temperature ────────────────────────────────────────────────
    ("Food Quality", "Temperature - Cold Food", re.compile(
        r"^(cold|(it.?s|was|food\s+(is|was))\s+cold|(too|very)\s+cold"
        r"|(pizza|biryani|burger|rice|food)\s+(is|was)\s+cold"
        r"|delivered\s+cold|cold\s+(pizza|biryani|food|burger|order)"
        r"|(not\s+(hot|at\s+all\s+hot)|pizza\s+not\s+hot)"
        r"|it\s+was\s+not\s+hot|order\s+was\s+cold|very\s+cold\s+food"
        r"|pizza\s+was\s+cold|it.?s\s+cold)\s*[!.]*\s*$",
        re.IGNORECASE
    )),

    # ── NEGATIVE — specific single-word quality issues ─────────────────────
    ("Food Quality", "Texture - Soggy", re.compile(
        r"^(dry|very\s+dry|too\s+dry|oily|too\s+(much\s+)?oily|(very\s+)?salty"
        r"|too\s+much\s+salt|too\s+much\s+masala|(too|very)\s+spicy|very\s+hard"
        r"|spicy|hard|very\s+spicy)\s*[!.]*\s*$",
        re.IGNORECASE
    )),
    ("Food Quality", "Cooking - Undercooked", re.compile(
        r"^(uncooked|uncooked\s+(food|rice)|undercooked|rice\s+not\s+boiled"
        r"|not\s+well\s+cooked)\s*[!.]*\s*$",
        re.IGNORECASE
    )),
    ("Food Quality", "Cooking - Overcooked/Hard", re.compile(
        r"^(overcooked|over\s+cooked|burnt\s+(food|pizza)?|its?\s+burned?)\s*[!.]*\s*$",
        re.IGNORECASE
    )),
    ("Food Quality", "Freshness - Stale/Bad Smell", re.compile(
        r"^(stale|stale\s+food|food\s+was\s+stale|rotten|rotten\s+food"
        r"|spoiled\s+food|bad\s+smell)\s*[!.]*\s*$",
        re.IGNORECASE
    )),

    # ── QUANTITY ──────────────────────────────────────────────────────────────
    ("Quantity", "Portion Too Small", re.compile(
        r"^((low|poor|very\s+less|less|worst|very\s+small|very\s+poor)\s+quantity"
        r"|quantity\s+(is\s+)?(low|less|very\s+less)|quantity\s+low|not\s+enough"
        r"|less\s+pieces|poor\s+quantity|low\s+quantity|very\s+small"
        r"|quantity)\s*[!.]*\s*$",
        re.IGNORECASE
    )),
    ("Quantity", "Missing Items", re.compile(
        r"^((item|items|order|egg|coke)\s+missing|missing\s+item(s)?"
        r"|not\s+received|no\s+(sauce|cutlery)|coke\s+is\s+missing"
        r"|no\s+masala|no\s+rajma|no\s+salad|items\s+missing|order\s+missing)\s*[!.]*\s*$",
        re.IGNORECASE
    )),

    # ── DELIVERY ──────────────────────────────────────────────────────────────
    ("Delivery", "Late Delivery", re.compile(
        r"^((very\s+)?late|(too\s+)?late|(slow|worst|bad)\s+delivery"
        r"|delivery\s+late|(order\s+)?delayed?|very\s+delayed?|(order\s+)?delay"
        r"|very\s+delay|slow\s+delivery|delivery\s+is\s+late|too\s+late)\s*[!.]*\s*$",
        re.IGNORECASE
    )),

    # ── PACKAGING ─────────────────────────────────────────────────────────────
    ("Packaging", "Packaging Damaged", re.compile(
        r"^(worst|poor|bad)\s+pack(aging|ing|age)?\s*[!.]*\s*$",
        re.IGNORECASE
    )),

    # ── VALUE FOR MONEY ───────────────────────────────────────────────────────
    ("Value for Money", "Overpriced / Not Worth", re.compile(
        r"^(waste\s+of\s+money|west\s+of\s+money|waste\s+money|not\s+worth\s+it"
        r"|not\s+worthy|worthless|worth\s+less|expensive|over.?priced"
        r"|not\s+worth[!.]*|waste[!.]*)\s*[!.]*\s*$",
        re.IGNORECASE
    )),

    # ── NEUTRAL / AMBIGUOUS → Other Feedback ─────────────────────────────────
    ("Other Feedback", "General Comment", re.compile(
        r"^(ok+|okay+|okish|ok\s+ok|okay\s+okay|just\s+ok|average|avg|avarage"
        r"|av[ge]+|not\s+so\s+good|not\s+that\s+good|better|satisf\w+"
        r"|below\s+average|na|hi|let|very|a|\.+|…+|thank\w*|thanks)\s*[!.]*\s*$",
        re.IGNORECASE
    )),
]


TOPIC_ORDER = [
    "Food Quality", "Quantity", "Wrong Order", "Packaging",
    "Delivery", "Value for Money", "Hygiene",
    "Positive Overall", "App/Platform", "Other Feedback",
]

TOPIC_COLORS = {
    "Food Quality":     "#E24B4A",
    "Positive Overall": "#3B6D11",
    "Other Feedback":   "#888780",
    "Quantity":         "#BA7517",
    "Wrong Order":      "#534AB7",
    "Value for Money":  "#185FA5",
    "Delivery":         "#0F6E56",
    "Packaging":        "#D4537E",
    "App/Platform":     "#378ADD",
    "Hygiene":          "#F09595",
}


def classify(comment, rating=None):
    """
    Return (topic, subtopic) for a review comment.
    Strategy:
    1. Short/slang exact patterns first (handles single-word and emoji reviews)
    2. Full phrase patterns (TAXONOMY)
    3. Rating-based fallback
    """
    if not comment or len(str(comment).strip()) < 1:
        return "No Comment", "N/A"

    c = str(comment).strip()

    # Step 1: short/slang exact patterns (best for 1-3 word reviews)
    if len(c) <= 40:
        for topic, subtopic, regex in SLANG_PATTERNS:
            if regex.search(c):
                return topic, subtopic

    # Step 2: main phrase taxonomy
    cl = c.lower()
    for topic, subtopics in TAXONOMY.items():
        for subtopic, pattern in subtopics.items():
            if re.search(pattern, cl):
                return topic, subtopic

    # Step 3: rating fallback
    if rating is not None:
        try:
            r = float(rating)
            if r >= 4.5:
                return "Positive Overall", "Overall Positive"
            elif r <= 1.5:
                return "Food Quality", "Taste - Bad"
        except (ValueError, TypeError):
            pass

    return "Other Feedback", "General Comment"
