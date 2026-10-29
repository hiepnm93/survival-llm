"""Short official safety guidance for the hazards where a wrong answer can kill, matched to the question by regex.

core.chat_events puts matching cards in front of the model before it answers and checks its answer against them, so
a library search that misses (a flood toolkit for a downed power line) can't leave it improvising a rescue. Written
from the agencies' published guidance; each card names the agency.
"""
import re


def _card(key, title, source, trigger, text):
    return {"key": key, "title": title, "source": source, "trigger": re.compile(trigger, re.I), "text": text}


CARDS = [
    _card("carbon-monoxide", "Generators, engines and carbon monoxide", "CDC",
          r"carbon monoxide|\bCO (?:alarm|detector|poisoning)s?\b"
          r"|\bgenerators?\b.{0,80}\b(?:garage|indoors?|inside|basement|house|home|shed|porch|windows?|tent|room|vents?)\b"
          r"|\b(?:garage|indoors?|inside|basement|shed|tent)\b.{0,80}\bgenerators?\b"
          r"|\b(?:where|how far|distance)\b.{0,60}\bgenerators?\b"
          r"|\b(?:grill|charcoal|camp ?stove|propane heater|gas oven|gas stove|car|engine|truck)\b.{0,80}"
          r"\b(?:indoors?|inside|garage|basement|tent|heat(?:ing)? (?:the|my|our) (?:house|home|room|apartment))\b",
          "Never use a generator, grill, camp stove or other gasoline-, propane-, gas- or charcoal-burning device inside "
          "a home, garage, basement, crawlspace or tent, even with doors and windows open. Run a generator outdoors only, "
          "at least 20 feet (6 m) from doors, windows and vents. Never run a car or truck inside a garage, even with the "
          "garage door open, and never heat a home with a gas oven or stove. If anyone has a headache, dizziness, "
          "weakness, nausea, vomiting, chest pain or confusion, get everyone into fresh air right away and call 911."),
    _card("power-line", "Downed power lines", "Ready.gov",
          r"\b(?:power|electric(?:al)?|utility|overhead|service|hydro)[ -]?(?:lines?|wires?|cables?|poles?)\b"
          r"|\blive wires?\b|\bdowned (?:lines?|wires?)\b|\blines? (?:is |are )?down\b",
          "Treat every downed or sagging power line as live and deadly, even if it isn't sparking or the power is out. "
          "Stay at least 35 feet (10 m) away, since the ground around it can be energized, and keep everyone and pets "
          "back. Call 911 and the power company. Never touch the line, or anything or anyone touching it, and never try "
          "to move it, even with a stick or broom. If a line falls on your car, stay inside and call 911; get out only "
          "if it catches fire, by jumping clear with your feet together and shuffling away."),
    _card("electric-shock", "Electric shock", "Red Cross",
          r"electrocut|electric(?:al)? (?:shock|injur)|\b(?:got|been|being|was|is) shocked\b|touch(?:ed|ing) a (?:live )?wire",
          "Don't touch a person who may still be in contact with electricity. If you can do it safely, turn off the "
          "power at the main breaker or fuse box; if the source is a power line or you can't cut the power, stay well "
          "away and call 911. Once the power is off, check breathing and start CPR if they aren't breathing. Everyone "
          "with an electric shock needs medical care, even if the burns look small."),
    _card("gas-leak", "Gas leaks", "Ready.gov",
          r"gas leak|leak(?:ing)? (?:gas|propane)|propane leak|smell(?:s|ing)? (?:of |like )?(?:natural |propane )?gas"
          r"|\bgas smell|rotten eggs?",
          "If you smell gas or hear hissing or blowing, leave the building right away and get everyone out. Don't use "
          "light switches, phones, lighters or anything that could make a spark on the way out, and don't look for the "
          "leak. From a safe distance outside, call 911 or the gas company. Don't go back in until they say it is safe."),
    _card("house-fire", "Home fires and smoke", "NFPA",
          r"\b(?:house|home|kitchen|grease|apartment|building|room|car) (?:is )?(?:on )?fire\b|\bon fire\b"
          r"|\bfire in (?:the|my|our|a)\b|\bsmoke (?:alarm|detector)s?\b|\bsmoke (?:in|filling|coming)\b|\bescape (?:a|the) fire",
          "Get out, stay out, and call 911 from outside. Crawl low under smoke, feel doors with the back of your hand and "
          "use another way out if one is hot, and close doors behind you. Never go back inside a burning building for "
          "people, pets or belongings: tell firefighters who is missing. If your clothes catch fire, stop, drop and "
          "roll. Smother a small grease fire with a lid and turn off the heat; never put water on it."),
    _card("floodwater", "Floodwater", "NWS",
          r"\bflood(?:ed|ing|water|waters|s)?\b.{0,80}\b(?:walk|wade|wading|drive|driving|cross|swim|car|road|street)"
          r"|\b(?:walk|wade|wading|drive|driving|cross|swim)\w*\b.{0,80}\bflood|\bwater over the road",
          "Turn around, don't drown: never walk, swim or drive through floodwater. Six inches of moving water can knock "
          "you down and a foot of it can carry away a car; the road underneath may be washed out. Floodwater can hide "
          "downed power lines, sewage, chemicals and debris. If your car stalls in rising water, get out and move to "
          "higher ground if you can do it safely. If you are trapped, go to the highest level and call 911."),
    _card("water-bleach", "Disinfecting drinking water with bleach", "EPA",
          r"\bbleach\b.{0,80}\bwater\b|\bwater\b.{0,80}\bbleach\b|disinfect\w* (?:the |my |drinking )?water"
          r"|purif\w* (?:the |my |drinking )?water|water purif|\bwater\b.{0,60}\b(?:contaminat\w*|unsafe|safe to drink)"
          r"|(?:contaminated|unsafe|cloudy|murky|untreated) water|water (?:from|out of) (?:a |the )?(?:river|stream|lake|creek|pond)",
          "Boiling is best when you can. To disinfect clear water with plain unscented household bleach (6% or 8.25% "
          "sodium hypochlorite), add 8 drops of 6% or 6 drops of 8.25% bleach per gallon (about 2 drops per liter), "
          "and double that for cloudy or very cold water after filtering it through a clean cloth. Stir and let it "
          "stand 30 minutes: it should smell slightly of chlorine; if not, repeat the dose and wait 15 more minutes. "
          "Don't use scented, color-safe or splash-less bleach."),
    _card("boil-water", "Boiling water to make it safe", "CDC",
          r"\bboil\w*\b.{0,40}\bwater\b|\bwater\b.{0,40}\bboil",
          "Bring clear water to a full rolling boil for 1 minute (3 minutes above 6,500 feet / 2,000 m). If it is "
          "cloudy, let it settle and filter it through a clean cloth, paper towel or coffee filter first. Let it cool on "
          "its own and keep it in clean, covered containers."),
    _card("food-outage", "Food safety after a power outage or flood", "USDA",
          r"\b(?:fridge|refrigerat\w*|freezer|frozen food|perishable)"
          r"|\b(?:power|outage|blackout|electricity)\b.{0,80}\b(?:food|meat|milk|groceries)\b"
          r"|\b(?:food|meat|milk|groceries)\b.{0,80}\b(?:power|outage|blackout|electricity)\b"
          r"|\bfood\b.{0,60}\bflood|\bflood\w*\b.{0,60}\bfood",
          "Keep the fridge and freezer doors closed. A closed fridge keeps food safe for about 4 hours; a full freezer "
          "holds its temperature about 48 hours (24 hours if half full). Throw out meat, poultry, fish, eggs, milk, "
          "leftovers and other perishable food that has been above 40 °F (4 °C) for 2 hours or more. Never taste food "
          "to check it: when in doubt, throw it out. Throw out food that touched floodwater, except undamaged "
          "commercial cans, which can be cleaned and sanitized; home-canned food must be discarded."),
    _card("bleeding", "Severe bleeding", "Red Cross",
          r"\bbleed\w*|tourniquet|hemorrhag|haemorrhag|\bdeep (?:cut|wound|gash)|spurting|gushing",
          "Call 911 for heavy bleeding. Press firmly and directly on the wound with a clean cloth or gauze and keep "
          "pressing; put more cloth on top instead of lifting soaked layers. For life-threatening bleeding from an arm "
          "or leg that pressure doesn't stop, put a tourniquet 2-3 inches above the wound (not on a joint) and tighten "
          "it until the bleeding stops; note the time and don't loosen it. Keep the person lying down and warm."),
    _card("burns", "Burns", "NHS",
          r"\b(?:burn(?:ed|t|s)?|scald(?:ed|s)?)\b.{0,40}\b(?:hand|arm|skin|finger|leg|face|foot|child|baby|myself|"
          r"himself|herself|blister)|\b(?:hand|arm|skin|finger|leg|face)\b.{0,30}\bburn|\bburns?\b (?:first aid|treatment)"
          r"|treat\w* (?:a |the |my )?burn",
          "Cool the burn under cool or lukewarm running water for 20 minutes as soon as possible; don't use ice, butter "
          "or creams. Take off rings and clothing near it unless they are stuck to the skin. Cover it loosely with "
          "cling film or a clean plastic bag. Call 911 for large or deep burns, burns to the face, hands, feet or "
          "genitals, electrical or chemical burns, or burns on a baby or young child."),
    _card("hypothermia", "Hypothermia", "CDC",
          r"hypotherm|\bshiver\w*|frostbite|(?:out|been|stuck) in the cold",
          "Hypothermia is an emergency: call 911. Get the person into a warm room or shelter and take off any wet "
          "clothing. Warm the center of the body first (chest, neck, head and groin) with dry blankets, layers or "
          "skin-to-skin contact; warm sweet drinks help if they are awake and can swallow, but no alcohol. If they "
          "aren't breathing or have no pulse, start CPR."),
    _card("heat-stroke", "Heat stroke", "CDC",
          r"heat ?stroke|heat exhaustion|stopped sweating|overheat(?:ed|ing)\b.{0,40}\b(?:person|man|woman|child|kid|he|she)"
          r"|\b(?:very|too) hot\b.{0,60}\b(?:confus\w*|dizz\w*|faint\w*)|\bworking in the heat",
          "Heat stroke is a medical emergency: call 911. Move the person somewhere cool and shaded, take off extra "
          "clothing, and cool them quickly with cold water or ice: a cool bath or shower, soaked cloths and fanning, or "
          "ice packs on the neck, armpits and groin. Don't give them anything to drink if they are confused or can't "
          "swallow safely."),
    _card("choking", "Choking", "Red Cross",
          r"\bchok(?:e|es|ed|ing)\b|heimlich|stuck in (?:his|her|their|my|the) throat",
          "If someone can't cough, speak or breathe, call 911 and act now. For an adult or a child over 1: give 5 back "
          "blows between the shoulder blades with the heel of your hand, then 5 abdominal thrusts, and repeat until the "
          "object comes out or they become unresponsive. For a baby under 1, give 5 back blows and 5 chest thrusts with "
          "two fingers, never abdominal thrusts. If they become unresponsive, start CPR."),
    _card("drowning", "Drowning and water rescue", "Red Cross",
          r"drown\w*|water rescue|swept away|rip current|caught in (?:a |the )?current"
          r"|\b(?:fell|fallen|is|are|someone|struggling) (?:in|into) (?:the )?(?:water|river|lake|pool|sea|ocean|creek|pond)\b",
          "Call 911, or have someone call. Don't go into the water after someone unless you are trained: from land, "
          "reach out with a pole, branch or rope, or throw them something that floats. Never enter fast-moving or "
          "flood water. Once they are out, check breathing and start CPR if they aren't breathing normally."),
    _card("lightning", "Lightning", "NWS",
          r"lightning|thunder\w*",
          "When thunder roars, go indoors: no place outside is safe. Get into a building with wiring and plumbing, or a "
          "hard-topped car with the windows up, and wait 30 minutes after the last thunder. Indoors, stay off corded "
          "phones and away from water, windows and doors. If you are caught outside, get off hilltops and away from "
          "water and lone trees. A person struck by lightning carries no charge: call 911 and start CPR if needed."),
    _card("chainsaw", "Chainsaws and storm debris", "OSHA",
          r"chain ?saws?|fallen trees?|trees? (?:fell|fallen|down)|tree limbs?|cut(?:ting)? (?:up )?(?:a |the )?"
          r"(?:tree|trees|limb|limbs|branch|branches)\b|storm debris|debris clean",
          "Check for power lines first: never cut a tree or limb that touches or is near a line; call the power company. "
          "Wear a helmet, eye and ear protection, gloves, chaps and sturdy boots. Hold the saw with both hands, keep the "
          "tip clear to avoid kickback, and never cut above shoulder height or from a ladder. Watch for bent or trapped "
          "limbs that can spring back, and run the saw and other engines outdoors only."),
    _card("chemicals", "Household chemicals and fumes", "CDC",
          r"\bbleach\b.{0,60}\b(?:ammonia|vinegar|acid|mix\w*|combin\w*)|\b(?:ammonia|vinegar)\b.{0,60}\bbleach"
          r"|chemical (?:spill|burn|splash|exposure|fumes|smell|in (?:my|his|her|their|the) eyes?)|toxic fumes"
          r"|\bfumes\b|swallowed (?:bleach|cleaner|detergent|chemicals?|antifreeze|gasoline)",
          "Never mix bleach with ammonia, vinegar or other acids, or with other cleaners: it releases toxic gas. If "
          "someone breathed fumes, get them into fresh air. For chemicals on the skin or in the eyes, rinse with plenty "
          "of running water for 15-20 minutes and take off contaminated clothing. Don't make anyone vomit. Call Poison "
          "Control (in the US, 1-800-222-1222), or 911 if they have trouble breathing, collapse or have a seizure."),
    _card("insulin", "Insulin without a fridge", "FDA",
          r"insulin",
          "Insulin, opened or unopened, can usually be kept at room temperature (59-86 °F / 15-30 °C) for up to 28 "
          "days; some pens and brands differ, so check the leaflet. Keep it out of direct heat, sunlight and freezing, "
          "and don't use insulin that has frozen or looks cloudy or clumped when it should be clear. If insulin kept "
          "warmer is all you have, use it rather than go without, and check blood sugar more often."),
    _card("child-medicine", "Medicine doses and poisoning", "NHS",
          r"\b(?:dose|doses|dosage|dosing)\b|how (?:much|many) (?:ibuprofen|tylenol|acetaminophen|paracetamol|"
          r"motrin|advil|benadryl|aspirin|medicine|pills?|tablets?)|overdose|took too (?:much|many)|swallowed (?:pills|"
          r"medicine|tablets)|\bpoison(?:ed|ing)?\b",
          "Give children only medicine made for children, at the dose on the label for their age or weight, measured "
          "with the syringe or spoon that comes with it; never guess a child's dose from an adult tablet. Don't give "
          "aspirin to anyone under 16. Write down each dose and the time so no one doubles up. If someone may have taken "
          "too much or swallowed something poisonous, call Poison Control (in the US, 1-800-222-1222) or 911, even if "
          "they seem fine."),
    _card("shelter-in-place", "Sheltering from radiation or a chemical release", "Ready.gov",
          r"nuclear|radiation|radioactive|fallout|dirty bomb|shelter[- ]in[- ]place|chemical (?:release|attack|leak|"
          r"plume|cloud)|toxic (?:cloud|plume|gas)|\bhazmat\b",
          "Get inside the nearest sturdy building and stay inside: go to the basement or the middle of the building, "
          "away from windows and doors. Close windows, doors and vents, and turn off fans, heating and air conditioning "
          "that bring in outside air. If you were outside, take off your outer clothes and wash with soap and water. "
          "Stay inside for at least 24 hours unless officials say otherwise, and listen to local radio for instructions."),
    _card("candles", "Candles and light in an outage", "NFPA",
          r"\bcandles?\b|oil lamps?|kerosene lamps?|light(?:ing)? (?:during|in) (?:a |the )?(?:blackout|outage)",
          "Use flashlights or battery lanterns rather than candles during an outage. If you do use candles, put them in "
          "sturdy holders at least 12 inches (30 cm) from anything that can burn, out of reach of children and pets, "
          "and blow them out when you leave the room or go to sleep; never leave one burning unattended. Never use a "
          "candle where medical oxygen is used."),
]

# Hazards worth the answer's safety check even when no card matched.
HAZARD = re.compile(r"electri|power ?lines?|live wires?|\bfire\b|flames?|smoke|\bgas\b|propane|carbon monoxide|"
                    r"chemical|ammonia|\bflood|drown|\brescue\b|explo(?:de|sion|sive)|unconscious|not breathing|poison",
                    re.I)


def match(question, limit=3):
    """The cards whose trigger the question matches, at most limit, in CARDS order."""
    return [c for c in CARDS if c["trigger"].search(question or "")][:limit]


def is_hazard(question):
    """Whether the question is about a hazard: a card matches, or it names one."""
    return bool(match(question) or HAZARD.search(question or ""))
