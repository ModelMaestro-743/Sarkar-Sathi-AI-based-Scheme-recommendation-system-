QUESTION_FLOW = [
    "preferred_language",
    "name",
    "state",
    "area_type",
    "employment",
    "income",
    "education",
    "interest_sector",
    "user_query",
]

LANGUAGE_TO_TRANSLATOR = {"en": "english", "hi": "hindi", "mr": "marathi"}

COMMAND_ALIASES = {
    "more": {"more", "aur", "और", "ajun", "aankhi", "आणखी"},
    "stop": {"stop", "rok", "रोक", "थांब", "thamb"},
    "resume": {"resume", "continue", "जारी", "chalu", "suru", "सुरू"},
    "yes": {"yes", "haan", "ha", "हाँ", "haanji", "हो", "होय"},
    "update": {"update", "upd", "अपडेट", "badlo", "बदलो", "badla", "बदला"},
}

QUESTION_TEXT = {
    "preferred_language": {
        "en": "Please choose your preferred language / कृपया अपनी पसंदीदा भाषा चुनें / कृपया तुमची पसंतीची भाषा निवडा: English, Hindi, Marathi.",
        "hi": "कृपया अपनी पसंदीदा भाषा चुनें: English, Hindi, Marathi.",
        "mr": "कृपया तुमची पसंतीची भाषा निवडा: English, Hindi, Marathi.",
    },
    "name": {
        "en": "Hi! I am your Government Schemes Assistant. I will ask a few simple questions and suggest the most relevant schemes. What is your name?",
        "hi": "नमस्ते! मैं आपका सरकारी योजनाएं सहायक हूं। मैं कुछ आसान सवाल पूछूंगा और आपके लिए सबसे उपयुक्त योजनाएं बताऊंगा। आपका नाम क्या है?",
        "mr": "नमस्कार! मी तुमचा सरकारी योजना सहाय्यक आहे. मी काही सोपे प्रश्न विचारेन आणि तुमच्यासाठी सर्वात योग्य योजना सुचवेन. तुमचे नाव काय आहे?",
    },
    "state": {
        "en": "Which state do you live in?",
        "hi": "आप किस राज्य में रहते हैं?",
        "mr": "तुम्ही कोणत्या राज्यात राहता?",
    },
    "area_type": {
        "en": "Is your area Urban or Rural?",
        "hi": "आपका क्षेत्र शहरी है या ग्रामीण?",
        "mr": "तुमचा भाग शहरी आहे की ग्रामीण?",
    },
    "employment": {
        "en": "What is your employment type? (Student/Unemployed/Self-employed/Private/Government)",
        "hi": "आपका रोजगार प्रकार क्या है? (Student/Unemployed/Self-employed/Private/Government)",
        "mr": "तुमचा रोजगार प्रकार काय आहे? (Student/Unemployed/Self-employed/Private/Government)",
    },
    "income": {
        "en": "What is your monthly income?",
        "hi": "आपकी मासिक आय कितनी है?",
        "mr": "तुमचे मासिक उत्पन्न किती आहे?",
    },
    "education": {
        "en": "What is your highest education level?",
        "hi": "आपकी उच्चतम शिक्षा क्या है?",
        "mr": "तुमचे उच्चतम शिक्षण काय आहे?",
    },
    "interest_sector": {
        "en": "Which sector are you interested in?",
        "hi": "आप किस क्षेत्र में रुचि रखते हैं?",
        "mr": "तुम्हाला कोणत्या क्षेत्रात रस आहे?",
    },
    "user_query": {
        "en": "Great. What would you like help with?",
        "hi": "बहुत बढ़िया। आपको किस बारे में मदद चाहिए?",
        "mr": "छान. तुम्हाला कोणत्या बाबतीत मदत हवी आहे?",
    },
}

UI_TEXT = {
    "en": {
        "missing_phone": "Missing sender phone number.",
        "invalid_language": "Please reply with only one language: English, Hindi, or Marathi.",
        "paused": "Paused. Reply 'resume' anytime to continue.",
        "paused_wait": "Your session is paused. Reply 'resume' to continue.",
        "welcome_back_active": "Welcome back. {question}",
        "welcome_back_completed": "Welcome back. Reply 'more' for a new query, 'update field: value' to edit details, or 'yes' to restart full form.",
        "pending_guidance": "Would you like to search for more schemes? Reply 'more' for a new query, 'update field: value' to edit details, 'yes' to restart full form, or 'stop' to pause.",
        "restart_start": "Great, let's start again. {question}",
        "ask_new_query": "Sure. Please send your new query.",
        "wait_more": "Please wait, finding more schemes for your new query...",
        "update_format_error": "Use this format: update field: value. Example: update income: 30000",
        "allowed_fields": "Allowed fields: preferred_language, name, state, area_type, employment, income, education, interest_sector, user_query.",
        "updated_field": "Updated {field}. Reply 'more' to send a new query, or update another field.",
        "completed_help": "Reply 'more' for a new query, 'update field: value' to edit details, 'yes' to restart full form, or 'stop' to pause.",
        "wait_best": "Please wait, finding the best schemes for you...",
        "fetch_error": "Sorry, something went wrong while fetching your schemes.",
    },
    "hi": {
        "missing_phone": "भेजने वाले का फोन नंबर नहीं मिला।",
        "invalid_language": "कृपया केवल एक भाषा में जवाब दें: English, Hindi, या Marathi।",
        "paused": "सत्र रोका गया है। जारी रखने के लिए कभी भी 'resume' लिखें।",
        "paused_wait": "आपका सत्र रुका हुआ है। जारी रखने के लिए 'resume' लिखें।",
        "welcome_back_active": "वापसी पर स्वागत है। {question}",
        "welcome_back_completed": "वापसी पर स्वागत है। नई क्वेरी के लिए 'more' लिखें, जानकारी बदलने के लिए 'update field: value' लिखें, या पूरा फॉर्म फिर से शुरू करने के लिए 'yes' लिखें।",
        "pending_guidance": "क्या आप और योजनाएं देखना चाहते हैं? नई क्वेरी के लिए 'more' लिखें, जानकारी बदलने के लिए 'update field: value', पूरा फॉर्म फिर से शुरू करने के लिए 'yes', या रोकने के लिए 'stop' लिखें।",
        "restart_start": "ठीक है, फिर से शुरू करते हैं। {question}",
        "ask_new_query": "ज़रूर। कृपया अपनी नई क्वेरी भेजें।",
        "wait_more": "कृपया इंतजार करें, आपकी नई क्वेरी के लिए और योजनाएं खोजी जा रही हैं...",
        "update_format_error": "यह प्रारूप उपयोग करें: update field: value. उदाहरण: update income: 30000",
        "allowed_fields": "Allowed fields: preferred_language, name, state, area_type, employment, income, education, interest_sector, user_query.",
        "updated_field": "{field} अपडेट हो गया। नई क्वेरी भेजने के लिए 'more' लिखें, या कोई और field अपडेट करें।",
        "completed_help": "नई क्वेरी के लिए 'more' लिखें, जानकारी बदलने के लिए 'update field: value', पूरा फॉर्म फिर से शुरू करने के लिए 'yes', या रोकने के लिए 'stop' लिखें।",
        "wait_best": "कृपया इंतजार करें, आपके लिए सबसे उपयुक्त योजनाएं खोजी जा रही हैं...",
        "fetch_error": "माफ कीजिए, योजनाएं लाते समय कुछ गड़बड़ हो गई।",
    },
    "mr": {
        "missing_phone": "पाठवणाऱ्याचा फोन नंबर मिळाला नाही.",
        "invalid_language": "कृपया फक्त एक भाषा निवडा: English, Hindi, किंवा Marathi.",
        "paused": "सेशन थांबवले आहे. पुढे सुरू ठेवण्यासाठी कधीही 'resume' पाठवा.",
        "paused_wait": "तुमचे सेशन थांबले आहे. पुढे सुरू ठेवण्यासाठी 'resume' पाठवा.",
        "welcome_back_active": "पुन्हा स्वागत आहे. {question}",
        "welcome_back_completed": "पुन्हा स्वागत आहे. नवीन query साठी 'more' पाठवा, माहिती बदलण्यासाठी 'update field: value' पाठवा, किंवा पूर्ण form पुन्हा सुरू करण्यासाठी 'yes' पाठवा.",
        "pending_guidance": "तुम्हाला अजून योजना शोधायच्या आहेत का? नवीन query साठी 'more' पाठवा, माहिती बदलण्यासाठी 'update field: value', पूर्ण form पुन्हा सुरू करण्यासाठी 'yes', किंवा थांबवण्यासाठी 'stop' पाठवा.",
        "restart_start": "छान, पुन्हा सुरुवात करूया. {question}",
        "ask_new_query": "नक्की. कृपया तुमची नवीन query पाठवा.",
        "wait_more": "कृपया थांबा, तुमच्या नवीन query साठी अधिक योजना शोधत आहोत...",
        "update_format_error": "हा format वापरा: update field: value. उदाहरण: update income: 30000",
        "allowed_fields": "Allowed fields: preferred_language, name, state, area_type, employment, income, education, interest_sector, user_query.",
        "updated_field": "{field} अपडेट केले. नवीन query साठी 'more' पाठवा, किंवा दुसरे field अपडेट करा.",
        "completed_help": "नवीन query साठी 'more' पाठवा, माहिती बदलण्यासाठी 'update field: value', पूर्ण form पुन्हा सुरू करण्यासाठी 'yes', किंवा थांबवण्यासाठी 'stop' पाठवा.",
        "wait_best": "कृपया थांबा, तुमच्यासाठी सर्वात योग्य योजना शोधत आहोत...",
        "fetch_error": "माफ करा, योजना मिळवताना काहीतरी चूक झाली.",
    },
}
