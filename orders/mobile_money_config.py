# --- Configuration Orange Money MADAGASCAR ---
ORANGE_MONEY_CONFIG = {
    "OPERATOR_NAME": "Orange Money",
    "API_KEY": "API_KEY_ORANGE_SIMULEE_XXX", 
    "SECRET_KEY": "SECRET_KEY_ORANGE_SIMULEE_YYY",
    # Endpoint d'initialisation du paiement (à remplacer par le vrai URL)
    "PAYMENT_INIT_URL": "https://api-sandbox.orange.mg/v1/payment/init", 
    "CURRENCY": "MGA", # Ariary Malgache
    "CALLBACK_URL": "http://votre_domaine.com/orders/orange-callback/", # URL de confirmation après paiement
}

# --- Configuration Airtel Money MADAGASCAR ---
AIRTEL_MONEY_CONFIG = {
    "OPERATOR_NAME": "Airtel Money",
    "API_KEY": "API_KEY_AIRTEL_SIMULEE_AAA",
    "CLIENT_ID": "CLIENT_ID_AIRTEL_SIMULEE_BBB",
    # Endpoint de demande de paiement (à remplacer par le vrai URL)
    "PAYMENT_REQUEST_URL": "https://openapi.airtel.africa/payment/v1/request",
    "CURRENCY": "MGA",
    "CALLBACK_URL": "http://votre_domaine.com/orders/airtel-callback/", 
}