import streamlit as st
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# --------------------------
# IBM Watson API Credentials
# --------------------------
api_key='9c0010c5b6msh43150144b01ab7dp19d4dbjsn45fb1b7f4ede'
url="https://ibmwatsonlanguagetranslatordimasv1.p.rapidapi.com/createModel"

authenticator = IAMAuthenticator(api_key)
language_translator = LanguageTranslatorV3(
    version='2025-05-01',
    authenticator=authenticator
)
language_translator.set_service_url(url)

# --------------------------
# Streamlit App UI
# --------------------------
st.title("🌐 Language Translator App")
st.markdown("Translate text between different languages using IBM Watson Language Translator.")

# Dropdowns for source and target languages
source_lang = st.selectbox("Select the **source** language:", 
                           ('English', 'Arabic', 'Hindi', 'German', 'Spanish', 'Korean'))

target_lang = st.selectbox("Select the **target** language:", 
                           ('English', 'Arabic', 'Hindi', 'German', 'Spanish', 'Korean'))

# Language codes as per IBM Watson
language_codes = {
    'English': 'en',
    'Arabic': 'ar',
    'Hindi': 'hi',
    'German': 'de',
    'Spanish': 'es',
    'Korean': 'ko'
}

# Text input
text_prompt = f"Enter text in {source_lang}:"
input_text = st.text_area(text_prompt, height=200)

# Translate button
if st.button("🔁 Translate"):
    if source_lang == target_lang:
        st.warning("⚠️ Source and target languages must be different.")
    elif not input_text.strip():
        st.error("❌ Please enter some text to translate.")
    else:
        try:
            model_id = f"{language_codes[source_lang]}-{language_codes[target_lang]}"
            response = language_translator.translate(
                text=input_text,
                model_id=model_id
            ).get_result()

            translated_text = response['translations'][0]['translation']
            st.success(f"**Translated text in {target_lang}:**")
            st.write(translated_text)

        except Exception as e:
            st.error(f"❌ Translation failed. Please check your input or credentials.\n\nDetails: {e}")
