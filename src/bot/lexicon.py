LEXICON = {
    "hy": {
        "welcome": "👋 Բարև ձեզ! Բարի գալուստ Ավտոաճուրդների և Մաքսազերծման Բոտ:\n\nԱյստեղ կարող եք փնտրել Copart/IAAI աճուրդներից մեքենաներ, հաշվարկել Հայաստան տեղափոխման և մաքսազերծման ծախսերը, ինչպես նաև սահմանել ավտոմատ ծանուցումներ:",
        "choose_lang": "Խնդրում ենք ընտրել լեզուն / Please select language:",
        "lang_set": "✅ Լեզուն փոխվեց հայերենի:",
        "main_menu": "📌 Գլխավոր Մենյու:",
        "btn_search": "🔍 Որոնել Մեքենաներ",
        "btn_calc": "🧮 Մաքսազերծման Հաշվիչ",
        "btn_alerts": "🔔 Իմ Ծանուցումները",
        "btn_lang": "🌐 Փոխել Լեզուն",
        "btn_broker_panel": "⚙️ Դիլեր / Ադմին Պանել",
        "search_prompt_make": "🏎 Մուտքագրեք մեքենայի Մարկան (օր․՝ Hyundai, Toyota, Tesla):",
        "search_prompt_model": "🚘 Մուտքագրեք Մոդելը (կամ սեղմեք /skip` բոլորը տեսնելու համար):",
        "search_prompt_budget": "💰 Մուտքագրեք աճուրդի առավելագույն բյուջեն ($ USD-ով) (օր․՝ 7000):",
        "search_prompt_year": "📅 Մուտքագրեք սկսած որ տարեթվից (օր․՝ 2018, կամ /skip):",
        "search_prompt_title": "📜 Ընտրեք Title-ի տեսակը:",
        "title_all": "Բոլորը",
        "title_salvage": "Salvage Certificate",
        "title_clean": "Clean Title",
        "searching": "⏳ Որոնում ենք աճուրդներում, խնդրում ենք սպասել...",
        "no_results": "❌ Ձեր որոնմանը համապատասխան մեքենաներ չգտնվեցին:",
        "car_card": (
            "🚘 **{title}**\n"
            "🆔 Lot ID: `{id}` ({auction_source})\n"
            "📅 Տարեթիվ: {year} | 🛣 Վազք: {mileage} miles\n"
            "⛽️ Վառելիք: {fuel_type} | ⚙️ Շարժիչ: {engine_cc} cc\n"
            "💥 Վնասվածք: {primary_damage} | 📜 Title: {title_type}\n"
            "📍 Գտնվելու վայրը: {location}\n"
            "🏷 Ընթացիկ բիդ: **${current_bid}** | Buy It Now: {buy_now_str}\n\n"
            "💵 **Ծախսերի Մանրամասն Հաշվարկ (USD)**:\n"
            "• 🎯 **Գնահատված հաղթող գին (Est. Winning Bid)**: **${auction_price}**\n"
            "• Աճուրդի միջնորդավճար: ${auction_fee}\n"
            "• Տեղափոխում (ԱՄՆ -> Փոթի -> Երևան): ${total_logistics}\n"
            "• ՀՀ Մաքսազերծում + Բնապահպ․: **${customs_clearance_total}**\n"
            "• Բրոքերի/Դիլերի ծառայություն: ${broker_fee}\n"
            "------------------------------------\n"
            "💰 **ՎԵՐՋՆԱԿԱՆ ԸՆԴՀԱՆՈՒՐ ԱՐԺԵՔԸ ԵՐԵՎԱՆՈՒՄ: ${total_cost}**\n\n"
            "🔗 [👉 Դիտել ԿՈՆԿՐԵՏ ԼՕՏԸ ԱՃՈՒՐԴՈՒՄ]({auction_url})"
        ),
        "calc_prompt_price": "💵 Մուտքագրեք մեքենայի աճուրդային գինը ($ USD):",
        "calc_prompt_year": "📅 Մուտքագրեք արտադրման տարեթիվը (օր․՝ 2020):",
        "calc_prompt_cc": "⚙️ Մուտքագրեք շարժիչի ծավալը cc-ով (օր․՝ 2000, կամ 0 էլեկտրականի համար):",
        "calc_prompt_fuel": "⛽️ Ընտրեք վառելիքի տեսակը:",
        "fuel_gasoline": "Բենզին / Դիզել",
        "fuel_hybrid": "Հիբրիդ (Hybrid)",
        "fuel_electric": "Էլեկտրական (EV)",
        "save_search_success": "🔔 Որոնումը պահպանվել է! Նոր մեքենաներ հայտնվելիս կստանաք ծանուցում:",
        "no_saved_searches": "📭 Դուք չունեք պահպանված ծանուցումներ:",
        "btn_delete": "🗑 Ջնջել",
        "btn_add_alert": "➕ Ավելացնել Նոր Ծանուցում",
        "broker_panel_text": "⚙️ **Բրոքերի և Ադմինի Պանել**\n\nԸնթացիկ կարգավորումներ:\n• Լոգիստիկայի բազային արժեք: ${logistics_base}\n• Բրոքերի միջնորդավճար: ${broker_fee}",
        "btn_set_logistics": "✏️ Փոխել Լոգիստիկայի Գինը",
        "btn_set_broker_fee": "✏️ Փոխել Բրոքերի Միջնորդավճարը",
        "prompt_new_logistics": "Մուտքագրեք լոգիստիկայի նոր բազային արժեքը ($ USD):",
        "prompt_new_broker_fee": "Մուտքագրեք բրոքերի նոր միջնորդավճարը ($ USD):",
        "success_update": "✅ Կարգավորումները հաջողությամբ թարմացվեցին:"
    },
    "en": {
        "welcome": "👋 Hello! Welcome to the Car Auction & Customs Clearance Bot:\n\nYou can search cars on Copart/IAAI auctions, calculate total shipping and Armenia customs clearance costs, and setup auto-alerts!",
        "choose_lang": "Please select language:",
        "lang_set": "✅ Language changed to English.",
        "main_menu": "📌 Main Menu:",
        "btn_search": "🔍 Search Cars",
        "btn_calc": "🧮 Customs Calculator",
        "btn_alerts": "🔔 My Alerts",
        "btn_lang": "🌐 Change Language",
        "btn_broker_panel": "⚙️ Dealer / Admin Panel",
        "search_prompt_make": "🏎 Enter car Make (e.g., Hyundai, Toyota, Tesla):",
        "search_prompt_model": "🚘 Enter Model (or send /skip to search all):",
        "search_prompt_budget": "💰 Enter max auction budget in $ USD (e.g., 7000):",
        "search_prompt_year": "📅 Enter minimum year (e.g., 2018, or /skip):",
        "search_prompt_title": "📜 Select Title Type:",
        "title_all": "All",
        "title_salvage": "Salvage Certificate",
        "title_clean": "Clean Title",
        "searching": "⏳ Searching auctions, please wait...",
        "no_results": "❌ No cars found matching your criteria.",
        "car_card": (
            "🚘 **{title}**\n"
            "🆔 Lot ID: `{id}` ({auction_source})\n"
            "📅 Year: {year} | 🛣 Mileage: {mileage} miles\n"
            "⛽️ Fuel: {fuel_type} | ⚙️ Engine: {engine_cc} cc\n"
            "💥 Primary Damage: {primary_damage} | 📜 Title: {title_type}\n"
            "📍 Location: {location}\n"
            "🏷 Current Bid: **${current_bid}** | Buy It Now: {buy_now_str}\n\n"
            "💵 **Detailed Cost Breakdown (USD)**:\n"
            "• 🎯 **Predicted Winning Bid**: **${auction_price}**\n"
            "• Auction Fee: ${auction_fee}\n"
            "• Shipping (US -> Poti -> Yerevan): ${total_logistics}\n"
            "• Armenia Customs Clearance: **${customs_clearance_total}**\n"
            "• Broker Service Fee: ${broker_fee}\n"
            "------------------------------------\n"
            "💰 **TOTAL ESTIMATED COST IN YEREVAN: ${total_cost}**\n\n"
            "🔗 [👉 VIEW EXACT LOT ON COPART]({auction_url})"
        ),
        "calc_prompt_price": "💵 Enter auction price ($ USD):",
        "calc_prompt_year": "📅 Enter production year (e.g. 2020):",
        "calc_prompt_cc": "⚙️ Enter engine volume in cc (e.g. 2000, or 0 for EV):",
        "calc_prompt_fuel": "⛽️ Select fuel type:",
        "fuel_gasoline": "Gasoline / Diesel",
        "fuel_hybrid": "Hybrid",
        "fuel_electric": "Electric (EV)",
        "save_search_success": "🔔 Search alert saved! You will be notified when matching cars appear.",
        "no_saved_searches": "📭 You have no saved search alerts.",
        "btn_delete": "🗑 Delete",
        "btn_add_alert": "➕ Add New Alert",
        "broker_panel_text": "⚙️ **Broker / Admin Panel**\n\nCurrent Settings:\n• Base Logistics Cost: ${logistics_base}\n• Broker Fee: ${broker_fee}",
        "btn_set_logistics": "✏️ Update Logistics Cost",
        "btn_set_broker_fee": "✏️ Update Broker Fee",
        "prompt_new_logistics": "Enter new base logistics cost ($ USD):",
        "prompt_new_broker_fee": "Enter new broker fee ($ USD):",
        "success_update": "✅ Settings updated successfully!"
    }
}


def get_text(lang: str, key: str, **kwargs) -> str:
    lang_lex = LEXICON.get(lang, LEXICON["hy"])
    text = lang_lex.get(key, LEXICON["hy"].get(key, f"[{key}]"))
    if kwargs:
        return text.format(**kwargs)
    return text
