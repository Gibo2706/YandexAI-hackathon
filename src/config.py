TARGET_KEYWORDS = [
    "scam", "fraud", "legit", "ponzi", "pyramid scheme", "rug pull", 
    "hacked", "stolen", "fake", "suspicious", "phishing", "wallet drainer",
    "is this real", "too good to be true", "guaranteed return", "safe to use",
    "review", "trustpilot", "scammer", "rip off", "chargeback"
]

# Filteri kvaliteta
MIN_TEXT_LENGTH = 40      
MIN_POSITIVE_SCORE = 2
MAX_NEGATIVE_SCORE = -2

# NOVO: Reči koje prolaze filter IAKO su kratke (bitne za sentiment)
SHORT_TEXT_WHITELIST = {
    "yes", "no", "scam", "legit", "fake", "real", "true", "false", 
    "safe", "unsafe", "yup", "nope", "avoid", "run"
}

# Putanje (prilagodi svojim folderima)
RAW_DATA_PATH = "./dataset"
PROCESSED_DATA_PATH = "./dataset/processed"
DOCUMENTS_OUTPUT_FILE = "./dataset/processed/final_documents.jsonl"

# Dokumenti logika
MAX_COMMENTS_PER_POST = 8   
MIN_COMMENT_POSITIVE_SCORE = 2
MAX_COMMENT_NEGATIVE_SCORE = -2