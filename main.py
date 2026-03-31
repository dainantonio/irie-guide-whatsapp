import os
import json
from collections import defaultdict
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import PlainTextResponse
import google.generativeai as genai
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

# ── Gemini setup ──────────────────────────────────────────────────────────────
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are IrieGuide, a warm, knowledgeable, and enthusiastic Caribbean tourism concierge for Jamaica.
You speak with a friendly island vibe — occasionally sprinkling in Jamaican phrases like "Irie!", "No worries, mon",
"Big up!", and "Walk good!" — but you keep it professional and easy to understand for all visitors.

Your mission is to help tourists discover the best of Jamaica: attractions, food, culture, history, beaches,
adventure, and hidden gems across all 14 parishes. When recommending places, always be specific and enthusiastic.
If a user asks about a parish or region, use the get_jamaica_recommendation tool to fetch curated attraction data.

Keep responses concise and WhatsApp-friendly (no markdown headers, use plain text with emojis).
Aim for 3–5 sentences max unless the user asks for more detail."""

# ── Function / tool definition ────────────────────────────────────────────────
JAMAICA_DATA = {
    "Kingston": {
        "description": "Jamaica's vibrant capital and cultural heartbeat",
        "attractions": [
            "Bob Marley Museum – the reggae legend's former home on Hope Road",
            "Devon House – colonial mansion with the island's best ice cream",
            "National Gallery of Jamaica – finest Caribbean art collection",
            "Port Royal – sunken 'Wickedest City' with pirate history",
            "Emancipation Park – sculptures and peaceful green space",
            "Blue Mountains Coffee Tour – world-famous coffee at its source",
        ],
        "food": "Try jerk chicken at Scotchies, patties at Tastee, and ackee & saltfish at any local cook shop.",
        "tip": "Visit the Coronation Market on a Saturday morning for an authentic Kingston experience.",
    },
    "Saint Andrew": {
        "description": "Home to the Blue Mountains and uptown Kingston suburbs",
        "attractions": [
            "Blue Mountains National Park – UNESCO World Heritage hiking",
            "Holywell Recreation Area – cool mountain camping and trails",
            "Strawberry Hill – luxury eco-resort with panoramic views",
            "Irish Town – charming mountain village",
            "University of the West Indies Mona Campus – beautiful historic grounds",
        ],
        "food": "Mountain lodges serve hearty Jamaican breakfasts with Blue Mountain coffee.",
        "tip": "Hike to Blue Mountain Peak (7,402 ft) to watch sunrise above the clouds — start at 2 AM.",
    },
    "Saint Thomas": {
        "description": "Rugged east-end parish with mineral springs and rich history",
        "attractions": [
            "Bath Fountain – natural hot mineral spring baths since 1699",
            "Morant Point Lighthouse – Jamaica's easternmost tip",
            "Stony Gut Village – birthplace of National Hero Paul Bogle",
            "Yallahs Salt Ponds – flamingo habitat and scenic ponds",
            "Reggae Falls – hidden waterfall in the jungle",
        ],
        "food": "Famous for roasted breadfruit and ackee prepared in traditional ways.",
        "tip": "Saint Thomas is off the tourist trail — perfect for authentic local culture.",
    },
    "Portland": {
        "description": "Jamaica's lush garden parish, birthplace of the Blue Lagoon",
        "attractions": [
            "Blue Lagoon – mystical 180-ft deep mineral spring meets the sea",
            "Reach Falls – stunning multi-tiered jungle waterfall",
            "Boston Bay Beach – birthplace of Jamaican jerk cooking",
            "Frenchman's Cove – pristine private beach with freshwater river",
            "Rio Grande Rafting – romantic bamboo raft journey",
            "Nonsuch Caves – underground stalactite caverns",
        ],
        "food": "Boston Bay is ground zero for authentic jerk pork and chicken — don't leave without trying it.",
        "tip": "Port Antonio town has beautiful Georgian architecture and a colorful marina.",
    },
    "Saint Mary": {
        "description": "North coast parish with waterfalls, James Bond history, and eco-adventures",
        "attractions": [
            "GoldenEye Resort – Ian Fleming's home where James Bond was born",
            "Firefly – Noël Coward's hilltop estate with stunning views",
            "Kwame Nkrumah Garden – historic Pan-African landmark",
            "Tacky Falls – scenic waterfall named after National Hero Tacky",
            "Annotto Bay – historic harbor town",
            "Robin's Bay – eco-tourism and bioluminescent bay nearby",
        ],
        "food": "Fresh seafood at the Oracabessa Fish Fry every Friday night.",
        "tip": "Take the coastal road from Ocho Rios to Port Antonio for breathtaking scenery.",
    },
    "Saint Ann": {
        "description": "The Garden Parish — birthplace of Marcus Garvey and home to Ocho Rios",
        "attractions": [
            "Dunn's River Falls – Jamaica's most iconic waterfall, climb it!",
            "Nine Mile – Bob Marley's birthplace and mausoleum in Rhoden Hall",
            "Dolphin Cove – swim with dolphins, sharks, and stingrays",
            "Green Grotto Caves – limestone caverns with underground lake",
            "Chukka Caribbean Adventures – zip-lining, ATVs, horseback riding",
            "Marcus Garvey Birthplace – historic site in Saint Ann's Bay",
        ],
        "food": "Ocho Rios has great options — try Scotchies for jerk and The Ruins for fine dining.",
        "tip": "Visit Dunn's River Falls early morning to beat the cruise ship crowds.",
    },
    "Saint James": {
        "description": "Home to Montego Bay, Jamaica's tourism capital and Hip Strip",
        "attractions": [
            "Doctor's Cave Beach – the most famous beach in MoBay",
            "Rose Hall Great House – haunted plantation of the White Witch Annie Palmer",
            "Montego Bay Marine Park – snorkeling and glass-bottom boat tours",
            "Hip Strip (Gloucester Avenue) – bars, restaurants, and nightlife",
            "Rocklands Bird Sanctuary – hand-feed wild hummingbirds",
            "Greenwood Great House – preserved Georgian plantation house",
        ],
        "food": "Day-O Plantation Restaurant for jerk in a great house setting; The Pelican for local favorites.",
        "tip": "Montego Bay's Donald Sangster Airport is Jamaica's main international gateway.",
    },
    "Hanover": {
        "description": "Quiet western parish with unspoiled beaches and Lucea's charm",
        "attractions": [
            "Half Moon Bay Beach – pristine crescent beach, locals' secret",
            "Lucea Fort – 18th-century British fort with harbor views",
            "Tryall Club – world-class golf course and villa resort",
            "Sandy Bay Beach – calm, clear waters perfect for families",
            "Hanover Museum – local history in Lucea courthouse",
        ],
        "food": "Fresh fish and lobster at beachside shacks in Sandy Bay and Half Moon Bay.",
        "tip": "Hanover is less developed than Negril — great for travelers seeking tranquility.",
    },
    "Westmoreland": {
        "description": "Home to Negril's Seven Mile Beach and stunning sunsets",
        "attractions": [
            "Seven Mile Beach – one of the Caribbean's most beautiful beaches",
            "Rick's Café – legendary cliff-jumping and sunset spot",
            "Negril Cliffs – dramatic limestone cliffs for diving and snorkeling",
            "Royal Palm Reserve – wetland nature sanctuary",
            "Booby Cay Island – small island day trip with snorkeling",
            "YS Falls (nearby) – natural waterfall with rope swings",
        ],
        "food": "Norma's on the Beach for upscale Jamaican; Cosmo's Seafood for casual fresh catch.",
        "tip": "Negril sunsets are world-famous — be at the cliffs at Rick's Café 30 min before sunset.",
    },
    "Saint Elizabeth": {
        "description": "Jamaica's breadbasket with Black River Safari and mineral springs",
        "attractions": [
            "YS Falls – most beautiful waterfall in Jamaica with natural pools",
            "Black River Safari – crocodile boat tour on Jamaica's longest river",
            "Pelican Bar – wooden bar built on a sandbar 1 mile offshore",
            "Appleton Estate – Jamaica's famous rum distillery tour",
            "Bamboo Avenue – 4km canopy of giant bamboo over the road",
            "Lover's Leap – dramatic 1,700-ft cliff with legend of star-crossed lovers",
        ],
        "food": "The best jerk in this area is found in Middle Quarters — try the peppered shrimp roadside stalls.",
        "tip": "Book the Pelican Bar boat trip — it's one of the most unique bars in the world.",
    },
    "Manchester": {
        "description": "Cool highland parish with Mandeville's colonial charm",
        "attractions": [
            "Marshall's Pen Great House – birding paradise, 100+ species",
            "Mandeville Town Square – colonial Georgian architecture",
            "Pickapeppa Factory – tour of Jamaica's famous hot sauce maker",
            "Shooter's Hill – scenic highlands with great views",
            "Alligator Pond – authentic fishing village with fried fish shacks",
            "High Mountain Coffee – estate tour and tasting",
        ],
        "food": "Alligator Pond's Little Ochie seafood restaurant is a must — legendary fresh fish and lobster.",
        "tip": "Manchester's cooler climate (2,000 ft elevation) makes it a refreshing break from beach heat.",
    },
    "Clarendon": {
        "description": "Central parish with spa retreats, caves, and industrial heritage",
        "attractions": [
            "Milk River Mineral Bath – world's most radioactive (therapeutic) spa",
            "Halse Hall Great House – one of Jamaica's oldest sugar estates",
            "Vere Plains – vast agricultural heartland of Jamaica",
            "Portland Cottage – coastal fishing village",
            "Four Paths – historic crossroads town",
        ],
        "food": "Local cook shops in May Pen serve authentic Jamaican cuisine at very affordable prices.",
        "tip": "Milk River Spa is a therapeutic gem — the mineral water is said to cure arthritis and skin conditions.",
    },
    "Saint Catherine": {
        "description": "Historic parish with Spanish Town, Jamaica's former capital",
        "attractions": [
            "Spanish Town Square – oldest surviving Georgian square in the Americas",
            "Rodney's Memorial – monument to British Admiral George Rodney",
            "White Marl Taino Museum – pre-Columbian indigenous heritage",
            "Hellshire Beach – favorite local beach with fresh fried fish",
            "Caymanas Park – Jamaica's premier horse racing track",
            "Ferry River – mangrove boat tours",
        ],
        "food": "Hellshire Beach is famous for its fried fish and festival (sweet fried dumplings) — a national institution.",
        "tip": "Spanish Town was Jamaica's capital for 300 years — the historic square is a UNESCO candidate site.",
    },
    "Trelawny": {
        "description": "Birthplace of Usain Bolt, home to Cockpit Country and Falmouth",
        "attractions": [
            "Cockpit Country – impenetrable limestone karst wilderness, Maroon homeland",
            "Falmouth Heritage Tours – best-preserved Georgian town in the Caribbean",
            "Good Hope Great House – 18th-century estate with river tubing",
            "Martha Brae River Rafting – relaxing bamboo raft journey",
            "Luminous Lagoon – world's brightest bioluminescent bay",
            "Usain Bolt statue in Sherwood Content – honor the fastest man ever",
        ],
        "food": "Falmouth's waterfront has great seafood; try roasted yam and saltfish at local roadside stalls.",
        "tip": "The Luminous Lagoon night tour is magical — the water glows bright blue-green when disturbed.",
    },
}


def get_jamaica_recommendation(parish: str) -> dict:
    """Get tourism recommendations for a specific Jamaican parish.

    Args:
        parish: The name of the Jamaican parish (e.g., 'Kingston', 'Portland', 'Westmoreland')

    Returns:
        A dictionary with attractions, food tips, and travel advice for the parish.
    """
    # Normalize input
    normalized = parish.strip().title()
    # Handle common aliases
    aliases = {
        "St Ann": "Saint Ann",
        "St. Ann": "Saint Ann",
        "St Andrew": "Saint Andrew",
        "St. Andrew": "Saint Andrew",
        "St Thomas": "Saint Thomas",
        "St. Thomas": "Saint Thomas",
        "St Mary": "Saint Mary",
        "St. Mary": "Saint Mary",
        "St James": "Saint James",
        "St. James": "Saint James",
        "St Elizabeth": "Saint Elizabeth",
        "St. Elizabeth": "Saint Elizabeth",
        "St Catherine": "Saint Catherine",
        "St. Catherine": "Saint Catherine",
        "Mobay": "Saint James",
        "Mo Bay": "Saint James",
        "Montego Bay": "Saint James",
        "Ocho Rios": "Saint Ann",
        "Ochos Rios": "Saint Ann",
        "Negril": "Westmoreland",
        "Port Antonio": "Portland",
        "Ocho Rios": "Saint Ann",
    }
    parish_key = aliases.get(normalized, normalized)

    if parish_key in JAMAICA_DATA:
        data = JAMAICA_DATA[parish_key]
        return {
            "parish": parish_key,
            "description": data["description"],
            "top_attractions": data["attractions"],
            "food_tip": data["food"],
            "local_tip": data["tip"],
            "status": "found",
        }
    else:
        available = list(JAMAICA_DATA.keys())
        return {
            "status": "not_found",
            "message": f"Parish '{parish}' not found. Available parishes: {', '.join(available)}",
        }


# Gemini tool schema
TOOLS = [
    {
        "function_declarations": [
            {
                "name": "get_jamaica_recommendation",
                "description": "Get curated tourism recommendations, top attractions, food tips, and local advice for a specific Jamaican parish or major tourist destination.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parish": {
                            "type": "string",
                            "description": "The Jamaican parish name or major destination (e.g., 'Kingston', 'Portland', 'Westmoreland', 'Montego Bay', 'Negril')",
                        }
                    },
                    "required": ["parish"],
                },
            }
        ]
    }
]

# ── Session storage ───────────────────────────────────────────────────────────
MAX_TURNS = 10
sessions: dict[str, list] = defaultdict(list)


def get_session_history(phone: str) -> list:
    return sessions[phone]


def add_to_session(phone: str, role: str, content) -> None:
    sessions[phone].append({"role": role, "parts": [content] if isinstance(content, str) else content})
    # Keep only last MAX_TURNS pairs (each pair = user + model = 2 entries)
    if len(sessions[phone]) > MAX_TURNS * 2:
        sessions[phone] = sessions[phone][-(MAX_TURNS * 2):]


# ── Gemini chat with function calling ─────────────────────────────────────────
def chat_with_gemini(phone: str, user_message: str) -> str:
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-lite",
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
    )

    history = get_session_history(phone)
    chat = model.start_chat(history=history)

    response = chat.send_message(user_message)

    # Handle function calling loop
    while response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]

        if hasattr(part, "function_call") and part.function_call.name:
            fn_call = part.function_call
            fn_name = fn_call.name
            fn_args = dict(fn_call.args)

            # Execute the function
            if fn_name == "get_jamaica_recommendation":
                result = get_jamaica_recommendation(**fn_args)
            else:
                result = {"error": f"Unknown function: {fn_name}"}

            # Send function result back to model
            response = chat.send_message(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=fn_name,
                        response={"result": json.dumps(result)},
                    )
                )
            )
        else:
            break

    # Extract text response
    text = response.text.strip()

    # Update session with final user message and model response
    add_to_session(phone, "user", user_message)
    add_to_session(phone, "model", text)

    return text


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="IrieGuide – Jamaica WhatsApp Concierge")


@app.get("/")
async def root():
    return {"status": "IrieGuide is live!", "message": "No worries, mon — the bot is running. ☀️🌴"}


@app.post("/webhook")
async def webhook(
    Body: str = Form(...),
    From: str = Form(...),
):
    user_message = Body.strip()
    phone = From.strip()

    try:
        reply = chat_with_gemini(phone, user_message)
    except Exception as e:
        reply = f"Irie! We hit a small bump, mon. Please try again in a moment. 🌴 (Error: {str(e)[:100]})"

    twiml = MessagingResponse()
    twiml.message(reply)
    return PlainTextResponse(str(twiml), media_type="application/xml")
