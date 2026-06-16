import re, json
from collections import defaultdict
import pandas as pd

# ── Load Excel taxonomy once ─────────────────────────────────────────────────
def _load_taxonomy():
    f = "/mnt/user-data/uploads/All_Brand_Plug_-_Sub_Plug_Mapping.xlsx"
    df = pd.read_excel(f, sheet_name="Sheet1", header=None)
    os_plugs = [str(v).strip() for v in df.iloc[2:, 0].dropna().tolist()]
    lb_rows  = [(str(df.iloc[i,2]).strip(), str(df.iloc[i,3]).strip())
                for i in range(2, len(df)) if pd.notna(df.iloc[i,2]) and pd.notna(df.iloc[i,3])]
    fa_rows  = [(str(df.iloc[i,5]).strip(), str(df.iloc[i,6]).strip())
                for i in range(2, len(df)) if pd.notna(df.iloc[i,5]) and pd.notna(df.iloc[i,6])]
    wd_plugs = [str(v).strip() for v in df.iloc[2:, 11].dropna().tolist()]
    lb_map = defaultdict(list)
    for sub, plug in lb_rows: lb_map[plug].append(sub)
    fa_map = defaultdict(list)
    for sub, plug in fa_rows: fa_map[plug].append(sub)
    return os_plugs, lb_rows, fa_rows, wd_plugs, lb_map, fa_map

OS_PLUGS, LB_ROWS, FA_ROWS, WD_PLUGS, LB_MAP, FA_MAP = _load_taxonomy()

LB_BRANDS = {
    "Behrouz Biryani","Thalaiva Biryani","The Biryani Life",
    "Veg Darbar by Behrouz Biryani","Lunchbox - Meals & Thalis",
    "Veg Meals by Lunchbox","The Good Bowl","Honest bowl",
    "Dabba & Co","Makhani Darbar","Rowdy Reddy Biryani",
    "Dumdaar Kilo Biryani Handi","Dum Biryani By Punjabi Angithi",
}
OS_BRANDS = {
    "Oven Story Pizza","The Pizza Project by Oven Story",
    "Thinsane Pizza by Oven Story","99 Square Pizza",
}
WD_BRANDS = {"Wendy's Burgers"}
# All others → Faasos

# ── Comprehensive patterns ────────────────────────────────────────────────────
P = {
    "good taste":    r"\bgood\b|\bnice\b|\bgreat\b|\bsuper\b|\btasty\b|\byummy\b|\byum\b|\bawesome\b|\bperfect\b|\bexcellent\b|\bamazing\b|\bfantastic\b|\bwonderful\b|\blovely\b|\bsuperb\b|\bfabulous\b|\bdelicious\b|\bbrilliant\b|\boutstanding\b|\btesty\b|\bosm\b|\bwow\b|\bgodd\b|\bgoog\b|\blovy\b|\bosam\b|\byummu\b|\bgr8\b|\bgud\b|\bgd\b|\bnyc\b|\bwooow\b|\bsoo good\b|\btoo good\b|\bfinger.?lick|\bmouth.?water|\bheavenly\b|\bdivine\b|\bscrumptious\b|\bdelightful\b|\bwill order again\b|\bworth it\b|\bmust try\b|\bfinally found\b|\bbest ever\b",
    "bad taste":     r"bad taste|not tasty|tasteless|bland|horrible taste|worst taste|no taste|no flavor|no flavou|bad test|bd test|no test|not testy|not tasted|not test|nor good|nt good|not nice|bad food|poor taste|awful|disgusting|not good taste|taste.*bad|bad.*taste|poor.*food|below average|not recommended|bakwas|bekar|ghatiya|faltu|third.?class|shitty|pathetic|vry bad|vary bad|baad|worse|wrost|worest",
    "taste":         r"\btaste\b|\bflavor\b|\bflavou|\btest\b(?!icular)|too spicy|very spicy|over spicy|extremely spicy|super spicy|much spicy|not spicy|less spicy|no spice|masala.*jyada|jyada.*masala|bahut.*masala|too sweet|too sour|too bitter|too tangy|sweet.*instead.*spicy|spicy.*instead|no masala.*biryani|biryani.*no masala",
    "quality":       r"\bquality\b|\bstandard\b|\bexpected better\b|\bdisappoint\b|\bnot up to\b|\bnot upto\b|\bnot as good as\b|\bbelow standard\b|\bpoor quality\b|\bbad quality\b|\blow quality\b|\bsubstandard\b|\bworst quality\b|\bnot meeting\b|\bnot maintai\b|\bquality degraded\b|\bquality went down\b|\bquality down\b",
    "cold":          r"\bcold\b|\bthanda\b|\bthandi\b|\bnot hot\b|\bnot warm\b|\blukewarm\b|\bstone cold\b|\bice cold\b|\bfreezing\b|\bfreezer\b|\bfreeze\b|\bfrozen\b|\bcame cold\b|\barrived cold\b|\breached cold\b|\bdelivered cold\b|cold food|food cold|cold pizza|pizza cold|cold burger|burger cold|cold biryani|biryani cold|cold rice|rice cold|cold wrap|cold roti|cold dal|cold sabzi|cold gravy|cold chicken|cold curry|cold paratha|thanda tha|thanda aa|thanda khana|khana thanda|cold as water|cold as hell|like fridge|like freezer|removed from fridge|from fridge|straight from fridge",
    "warm":          r"\bwarm\b(?!.*cold)|needs to be warm|not.*warm|\blukewarm\b",
    "quantity":      r"\bquantity\b|\bquantiti\b|\bportion\b|\bless food\b|\bvery less\b|\btoo less\b|\bso less\b|\bquite less\b|\bsmall portion\b|\btiny portion\b|\bnot enough\b|\bless amount\b|\bhalf empty\b|\bhalf filled\b|\bvery small\b|\btoo small\b|\bminiscule\b|\bbarely anything\b|\blow quantity\b|\bpoor quantity\b|\bnot sufficient\b|\binsufficient\b|\bkam\b(?! sahi)|\bhalf bowl\b|\bquantity.*low\b|\bless.*quantity\b|\bquantum issue\b|\bportion size\b|\bnot filling\b|\bvery little\b|\btoo little\b|\bonly one\b(?! more)|\bonly 1\b|\bonly 2\b|\bonly two\b|\bonly three\b|\bonly.*piece\b|\bsingle piece\b|\bsmall size\b|\bsize.*small\b|\bless paneer\b|\bless chicken\b|\bless pieces\b|\bless mutton\b|\bchicken.*less\b|\bpaneer.*less\b|\bpieces.*less\b|\bpieces.*very less\b|\bonly.*pcs\b|only.*piece|very few|hardly any|very limited|limited.*pieces|miniature",
    "missing":       r"\bmissing\b|\bnot received\b|\bnot given\b|\bnot provided\b|\bnot sent\b|\bnot packed\b|\bnot included\b|\bforgot\b|\bdid not get\b|\bdidn.t get\b|\bwhere is\b|\bnot there\b|\bnot add\b|\bnot added\b|\babsent\b|\bmissed\b|\bitem.*missing\b|\bnot in order\b|\bdid not receive\b|\bdidn.t receive\b|\bnever received\b|\bnot come\b|\bwasn.t there\b|\bweren.t there\b|\bwasn.t given\b|\bweren.t given\b",
    "late delivery": r"\blate\b(?!.*taste|.*flavor|.*test)|\bdelay\b|\bdelayed\b|\bslow delivery\b|\bvery late\b|\btoo late\b|\blong time\b|\btoo long\b|\btook.*long\b|\btaking.*long\b|\blong.*deliver\b|\bnot on time\b|\bextremely late\b|\bmuch time\b|\btoo much time\b|\bwaited\b|\bwait.*long\b|\bpreparation.*late\b|\blate.*preparation\b|\bdelivery.*late\b|\blate.*delivery\b|\bvery slow\b|\bslow service\b|\bslow.*prepar\b|\bunreasonable delay\b|\binordinate delay\b|wrry.*late|wrry.*order|Too latte|Too late|order.*late|late.*order|1.5.*hr|1.5.*hour|2.*hour.*wait|waited.*hour|45 min.*wait|preparation.*slow|slow.*preparation",
    "delivery":      r"\bdelivery\b|\bdeliver\b|\bdelivered\b",
    "good delivery": r"good delivery|great delivery|fast delivery|quick delivery|on time|delivered on time|delivery fast|delivery quick|fast delivery|quick delivery|on.*time.*delivery|super.*fast|speedy delivery",
    "goof up":       r"wrong item|wrong order|different item|instead of|in place of|received instead|got instead|sent wrong|wrong food|not what i ordered|ordered.*but.*got|ordered.*but.*received|mismatch|incorrect.*item|incorrect.*order|wrong product|different product|different food|got wrong|they gave wrong|wrong delivered|delivered wrong|wrong sent|sent different|ordered.*wheat.*maida|blueberry.*chocolate|wrong pizza|wrong burger|wrong biryani|wrong roll|wrong wrap|wrong cake|wrong roti|wrong chapati|ordered.*paneer.*got.*veg|wrong.*chicken.*veg|veg.*non.?veg|non.?veg.*veg|chicken.*vegetarian|vegetarian.*chicken|wrong drink|pepsi.*instead.*coke|thumbsup.*instead|different.*drink|sent.*wrong.*drink|wrong.*cold.*drink|wrong.*beverage|wrong.*fries|normal.*fries.*instead.*peri|peri.*fries.*got.*normal|regular.*fries.*instead|salted.*fries.*instead.*peri|wrong masala lemon|masala lemon instead|instead.*pepsi|instead.*coke|wrong.*soda|rating mismatch|got different|different received|received wrong|wrong received|order mismatch|wrong sauce|wrong base|wrong flavou|wrong lemon|wrong ice tea|wrong masala|got paneer.*instead|instead.*paneer|wrong veg|wrong non veg|wrong.*cake|cake.*wrong|ordered.*blueberry.*biscoff|ordered.*hazelnut.*biscoff",
    "wrong order":   r"wrong item|wrong order|mismatch|incorrect order|different item|instead of|goof",
    "spillage":      r"spill|spilt|leaked|spillage|leaking|overflow|coke.*spill|drink.*spill|bottle.*leaking|container.*leaking|everything.*wet|got.*wet|liquid.*spill",
    "spillage - food": r"coke.*spill|drink.*spill|coke.*flat|flat.*coke|no gas|no fizz|flat.*drink|cold.*drink.*bad|soda.*flat|cola.*flat|bottle.*tight|cap.*tight|cap.*not.*open|can.t.*open.*bottle|open.*bottle.*can.t|bottle.*cap.*tight|couldn.t.*open|wont.*open|won.t.*open|not.*opening|not able.*open|difficult.*open|hard to open|fizz|gas.*not|bottle.*issue|coke.*water|cola.*water|drink.*water|coke.*open|bottle.*open|open.*coke|open.*bottle|cap.*soo tight|cap.*so tight|tight.*cap",
    "pkg/handling issue": r"packaging|packing|packed|pack.*torn|torn.*pack|box.*broken|container.*broken|box.*open|open.*box|not sealed|crushed|squished|dented|box.*damage|damage.*box|box.*wet|wet.*box|poor.*pack|bad.*pack|worst.*pack|package.*bad|bad.*package|pack.*not.*good|packing.*issue|packaging.*issue|packaging.*bad|bad.*packaging|box.*dented|pizza.*stuck.*box|stuck.*box|stuck.*top",
    "packaging issue":  r"packaging.*bad|bad.*packaging|pack.*torn|torn.*pack|damaged.*pack|box.*damage|spillage",
    "food stale":    r"stale|not fresh|old food|expired|gone bad|wasn.t fresh|food.*old|old.*food|stale.*food|food.*stale|bread.*not.*fresh|bun.*not.*fresh|stale.*bun|stale.*bread|rotten|rotten.*food|spoiled|bad.*smell|smell.*bad|foul.*smell|smell.*foul|smelly|odour|bad.*odour|kept.*long|made.*long.*ago|pre.*made|premade|reheated|previously.*cooked",
    "fp":            r"food poison|food.*poisoning|stomach ache|stomach.*pain|vomiting|vomit|sick after|fell sick|feeling sick|ill after|not well after|bad burps|burping|infection|got sick|stomach.*bad|stomach.*hurt|unwell after|health.*issue.*food|body.*ache.*after|stomach.*issue.*after|food.*infection",
    "foreign particle": r"hair|stone|insect|fly|cockroach|worm|foreign.*object|found.*in food|plastic.*in|glass.*in.*food|nail.*in|bug.*in|pin.*feather|feather.*in|strand.*in|found.*something",
    "uncooked":      r"uncooked|not cooked|undercooked|raw|half cooked|half.?baked|not properly cooked|not fully cooked|not done|patty not cooked|doughy|gummy.*rice|sticky.*rice|rice.*sticky|rice.*clump|clumped.*rice|rice.*raw|raw.*rice|half.*boiled|rice.*not.*boiled|not boiled|kachha|kachi|kacha|sabudana.*raw|sabudana.*not.*cooked|vada.*not.*fried|not fried.*properly|sabudana.*uncooked|not baked|half baked|underbaked|needs more cooking|not done properly|less cooked",
    "burnt":         r"\bburnt\b|\bburned\b|\bcharred\b|overcooked|over.?cooked|over fried|too fried|extra fried|black.*spots|dark.*spots|burnt.*food|food.*burnt|burnt.*roti|burnt.*paratha|burnt.*pizza|burnt.*chicken|burnt.*wrap|burnt.*popcorn|popcorn.*burnt|burnt.*bread|bread.*burnt|slightly burnt|a bit burnt|bit.*burnt",
    "overcooked":    r"overcooked|over.?cooked|over fried|slightly burnt|burnt|chicken.*overcooked|mutton.*overcooked",
    "dry":           r"\bdry\b|\bdried out\b|\bno moisture\b|\btoo dry\b|\bvery dry\b|dry.*food|food.*dry|dry.*biryani|dry.*roti|dry.*paratha|dry.*chicken|dry.*bread|dry.*burger|dry.*wrap|dry.*rice|rice.*dry",
    "soggy":         r"\bsoggy\b|not crispy|soft fries|soggy.*pizza|pizza.*soggy|soggy.*base|base.*soggy|soggy.*crust|crust.*soggy|wet.*pizza|limp",
    "hard":          r"\bhard\b(?!.*work|.*ly|.*ship|.*ly|.*core)|\bchewy\b|\btough\b|hard.*bread|hard.*roti|hard.*chapati|hard.*paratha|hard.*cake|like.*papad|papad.*like|rubbery|elastic.*paratha|elastic.*roti|hard.*bun|bun.*hard|chapati.*hard|roti.*hard|paratha.*hard|like papad|turned papad|became papad|hard.*biscuit|not soft|too hard|very hard|extremely hard|like stone|like rock|rock like|stone like",
    "oily":          r"\boily\b|\bgreasy\b|too.*oily|very.*oily|oil.*coming|too.*much.*oil|oil.*excess|excess.*oil|oil.*dripping|dripping.*oil|full of oil|swimming.*oil|oil.*floating",
    "salty":         r"\bsalty\b|too.*salty|very.*salty|excess.*salt|too.*much.*salt|high.*salt|salt.*high|over.*salted|salt.*more|more.*salt|salt.*bahut|namak.*jyada|jyada.*namak|no.*salt|salt.*less|less.*salt|no.*solt|solt.*nahi|salt.*nahi|namak.*nahi|no salt.*at all|salt.*absent|salt.*missing",
    "experience":    r"good experience|great experience|nice experience|amazing experience|wonderful experience|excellent experience|positive experience|\benjoyed\b|will order again|ordering again|would recommend|highly recommend|definitely order|must try|\bworth it\b|\bloved it\b|\blove it\b|first choice|best experience|overall.*good|overall.*great|\bsatisfied\b|\bsatisfactory\b|\bhappy with\b|very happy|totally happy|completely happy|really happy|thoroughly enjoyed|absolutely loved",
    "bad experience":r"bad experience|terrible experience|horrible experience|worst experience|very bad experience|negative experience|never again|dont recommend|do not recommend|not recommend",
    "dissatisfaction": r"dissatisfied|disappointed|dissatisfaction|very unhappy|extremely.*disappointed|totally.*disappointed|very.*disappointed|upset.*with|not happy|unhappy.*with|sad.*experience|\bdisappoint\b|not happy with|deeply dissatisfied",
    "vfm":           r"not worth|overpriced|too expensive|costly|waste of money|money waste|very costly|price.*high|high price|not worth.*price|not worth.*money|expensive|waste money|worthless|worth less|not worthy|west of money|over.?priced|wasted money|wasting money|not value|no value|poor value|bad value|overcharge|charged more|price.*not.*justified|too costly for|not justify.*price|price.*not.*right",
    "value for money": r"not worth|overpriced|too expensive|costly|waste.*money|very costly|price.*high|not worth.*price|expensive|waste money|worthless|over.?priced",
    "image issue":   r"image.*different|photo.*different|not like.*photo|different.*picture|picture.*different|misleading.*image|misleading.*photo|photo.*misleading|doesn.t look like|not look like|picture.*deceptive|deceptive.*picture|image.*not.*match|not.*match.*image|looks different|not as shown|not as.*menu|not as.*image|not as.*picture|shown.*in.*image|image.*shown|as per image|as per photo",
    "size issue":    r"too small.*size|size.*too small|smaller.*than.*expect|very small.*size|size.*very small|mini.*size|tiny.*size|wrong.*size|size.*wrong",
    "service issue": r"rude|bad service|service.*bad|staff.*bad|bad.*staff|customer.*service.*bad|service.*issue|customer.*care.*not|not.*responding|number.*not.*working|contact.*not|unreachable|not reachable|marked.*delivered.*without|without.*delivering|forced.*rating|made.*to.*rate|compelled.*rate|threatening|rating.*force",
    "instructions": r"instruction.*not|not.*instruction|special.*request.*not|not.*special.*request|note.*not|not.*note|customiz.*not|personaliz.*not|added.*note|mentioned.*not.*followed|not.*followed.*mention|specifically.*said|said.*not.*follow|without.*onion.*got.*onion|no.*onion.*gave.*onion|no garlic.*garlic|instruction.*not follow|note not taken",
    "refund":        r"refund|money back|return.*money|want.*refund|need.*refund|give.*refund|full.*refund",
    "bogo":          r"bogo|buy.*one.*get|1get1|offer.*not|not.*offer|coupon.*not|offer.*issue|deal.*not|discount.*not|free.*item.*not|not.*free.*item",
    "dip missing":   r"dip.*missing|no.*dip|dip.*not|chutney.*not.*given|sauce.*not.*given|no.*sauce|ketchup.*not.*given|no.*ketchup|tomato.*sauce.*not|no.*mayo|mayo.*not.*given|mayo.*missing|sauce.*missing|no.*chutney|chutney.*missing|no.*mint",
    "ketch up required": r"ketchup|ketch.*up|tomato.*sauce.*missing|no.*ketchup|ketchup.*not",
    "topping missing": r"topping.*missing|no.*topping|toppings.*not.*there|toppings.*absent|less.*topping|topping.*less|no.*toppings",
    "accompaniments missing": r"raita.*not|no.*raita|raita.*missing|pickle.*missing|salan.*missing|no.*salan|mint.*chutney.*not|no.*mint.*chutney|gulab.*jamun.*missing|gulab.*jamun.*not|sweet.*missing|jamun.*missing|no.*sweet.*in.*order|complimentary.*missing|no.*side|side.*missing|no.*salad|salad.*missing|shorba.*not|no.*shorba|no.*raitha|raitha.*not|raitha.*missing|no.*curd|curd.*missing|no.*pickle|pickle.*not",
    "coke missing":  r"coke.*missing|cold.*drink.*missing|drink.*missing|soda.*missing|lemon.*soda.*not|masala.*lemonade.*not|cola.*not.*given|pepsi.*not.*given|falooda.*not.*given|chaas.*not.*given|didn.t.*receive.*coke|not.*receive.*coke|no.*coke|no.*cola|coke.*not.*sent|beverage.*missing|drink.*not.*given|drink.*not.*sent|masala.*not.*given.*fries|peri.*masala.*not|masala.*peri.*not|no.*masala.*with|masala.*not.*with",
    "not specific":  r"average|okay|okish|ok ok|just ok|decent|mediocre|so so|meh|normal|theek|thik|abhi tak|sahi|thoda|could be better|needs improvement|scope for improvement",
}

def _match(cl, *keys):
    """Try matching comment against patterns for given keys (in order)."""
    for key in keys:
        if key in P:
            try:
                if re.search(P[key], cl, re.IGNORECASE):
                    return True
            except: pass
    return False

def classify_plug_subplug(comment, brand, rating=None):
    if not comment or not str(comment).strip():
        return "Comment Blank", "Comment Blank"
    
    c  = str(comment).strip()
    cl = c.lower()
    
    # ── OvenStory ──────────────────────────────────────────────────────────
    if brand in OS_BRANDS:
        for plug in OS_PLUGS:
            if plug in ("Instructions", "BOGO", "Refund", "Good Delivery", "OND"):
                if _match(cl, plug.lower()): return plug, plug
                continue
            if _match(cl, plug.lower()): return plug, plug
        if rating:
            r = float(rating)
            if r >= 4.5: return "Good Taste", "Good Taste"
            if r <= 1.5: return "Bad Taste", "Bad Taste"
        return "Bad Quality", "Bad Quality"

    # ── Wendy's ────────────────────────────────────────────────────────────
    elif brand in WD_BRANDS:
        for plug in WD_PLUGS:
            if plug == "Comment not clear": continue
            if _match(cl, plug.lower()): return plug, plug
        if rating:
            r = float(rating)
            if r >= 4.5: return "Good taste", "Good taste"
            if r <= 1.5: return "Quality", "Quality"
        return "Comment not clear", "Comment not clear"

    # ── LB+TGB ─────────────────────────────────────────────────────────────
    elif brand in LB_BRANDS:
        # Match sub-plug first (more specific → gives both plug and subplug)
        for sub, plug in LB_ROWS:
            if _match(cl, sub.lower()): return plug, sub
        # Then plug level
        for plug in LB_MAP:
            if plug in ("Not Specific",): continue
            if _match(cl, plug.lower()): return plug, plug
        if rating:
            r = float(rating)
            if r >= 4.5: return "Experience", "Good Experience- Food"
            if r <= 1.5: return "Taste", "Bad Taste"
        return "Not Specific", "Not Specific"

    # ── Faasos + all remaining ──────────────────────────────────────────────
    else:
        for sub, plug in FA_ROWS:
            if sub == "Comment Blank": continue
            if _match(cl, sub.lower()): return plug, sub
        for plug in FA_MAP:
            if plug in ("Comment Blank", "Comments Not Clear"): continue
            if _match(cl, plug.lower()): return plug, plug
        if rating:
            r = float(rating)
            if r >= 4.5: return "Experience", "Good Experience- Food"
            if r <= 1.5: return "Taste", "Bad Taste"
        return "Comments Not Clear", "Comments Not Clear"
