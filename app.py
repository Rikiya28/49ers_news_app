import streamlit as st
import feedparser
import re
import html
import requests
from newspaper import Article

try:
    from deep_translator import GoogleTranslator
    translator_instance = GoogleTranslator(source='auto', target='ja')
except ImportError as e:
    print("ImportError of deep_translator:", e)
    translator_instance = None

# Page configuration
st.set_page_config(
    page_title="49ers News Translator",
    page_icon="🏈",
    layout="centered"
)

# Custom CSS for 49ers colors (Red: #AA0000, Gold: #B3995D)
st.markdown("""
<style>
<style>
    /* App background */
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
    }
    
    /* Header (Top bar) */
    [data-testid="stHeader"] {
        background-color: #AA0000 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #B3995D !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Main title */
    h1 {
        color: #AA0000;
        text-align: center;
        text-shadow: 1px 1px 2px #B3995D;
        margin-bottom: 20px;
    }
    .header-logo {
        text-align: center;
        font-size: 3rem;
        margin-bottom: -10px;
    }
    
    /* Expander adjustments */
    [data-testid="stExpander"] {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #AA0000;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-logo'>🏈</div>", unsafe_allow_html=True)
st.title("San Francisco 49ers Latest News")
st.markdown("<p style='text-align: center; color: #666;'>Latest updates on the 49ers, translated into Japanese.</p>", unsafe_allow_html=True)

# Appending a thin visual divider below title
st.write("")

if not translator_instance:
    st.warning("⚠️ **翻訳機能が無効化されています** (`deep-translator` が見つかりません)。\n\nVS Codeで「推奨(Recommended)」のPython環境を選択した場合は、**現在Streamlitを実行しているターミナルをゴミ箱アイコンで閉じ（または `Ctrl+C` で終了し）、新しいターミナルを開いてから `python -m streamlit run app.py`** で起動し直してください。")

# Function to fetch and translate news
@st.cache_data(ttl=1800) # Cache for 30 minutes to avoid hitting API/RSS limits
def fetch_49ers_news():
    # Using Niners Nation RSS directly instead of Google News to bypass scraping protections
    rss_url = "https://www.ninersnation.com/rss/current.xml"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    
    # Get top 5 news items
    for entry in feed.entries[:5]:
        eng_title = entry.title
        
        # Summary might be HTML. Extract actual text if possible.
        raw_summary = getattr(entry, 'summary', '')
        clean_summary = html.unescape(re.sub('<[^<]+?>', '', raw_summary)).strip()
        
        # Remove repeated title from the beginning of google news summary if present
        if clean_summary.startswith(eng_title):
            clean_summary = clean_summary.replace(eng_title, "", 1).strip()
            
        source = getattr(entry, 'source', {}).get('title', 'Google News')
        published = getattr(entry, 'published', '')
        link = getattr(entry, 'link', '')
        
        # Build English body
        full_eng_text = ""
        actual_link = link
        if link:
            try:
                article = Article(actual_link)
                article.download()
                article.parse()
                full_eng_text = article.text
                print(f"DEBUG: Parsed {actual_link}. Text length: {len(full_eng_text)}")
            except Exception as e:
                print(f"DEBUG: Newspaper3k error for {actual_link}: {e}")
        
        if not full_eng_text:
            print(f"DEBUG: Newspaper3k returned empty text for {eng_title}. Falling back to summary.")
            full_eng_text = clean_summary

        eng_body = f"**Source:** {source} | **Published:** {published} \n\n[Read Full Article]({link})\n\n{full_eng_text}"
        
        # Default placeholder for translation
        jp_title = "翻訳結果取得中..."
        jp_body = f"**配信元:** {source} | **日時:** {published} \n\n[記事を読む (英語)]({link})\n\n(翻訳に失敗しました)"
        
        if translator_instance:
            try:
                # Attempt to translate the title with context hack
                translated_title_raw = translator_instance.translate("NFL news: " + eng_title)
                if translated_title_raw:
                    jp_title = translated_title_raw
                    for prefix in ["NFLニュース: ", "NFLニュース：", "NFL ニュース: ", "NFL ニュース：", "NFL news: "]:
                        if jp_title.startswith(prefix):
                            jp_title = jp_title[len(prefix):].strip()
                            break
                elif eng_title:
                    jp_title = translator_instance.translate(eng_title)
                
                # Attempt to translate the full text in paragraphs to avoid limit issues and keep structure
                if full_eng_text:
                    paragraphs = full_eng_text.split('\n')
                    translated_paragraphs = []
                    
                    for i, p in enumerate(paragraphs):
                        p = p.strip()
                        if p:
                            try:
                                # Improve entity preservation: Match only sequence of 2-3 capitalized words 
                                # to catch names like "Brock Purdy", "Kyle Shanahan", "San Francisco 49ers"
                                # but avoid grabbing entire sentences wrapped in quotes or Title Case headings
                                entity_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
                                entities = re.findall(entity_pattern, p)
                                
                                # Filter out common false positives (e.g. "The 49ers", "If The")
                                ignore_words = {"The", "A", "An", "And", "But", "Or", "For", "Nor", "On", "At", "To", "From", "By", "In", "I", "He", "She", "It", "They"}
                                filtered_entities = []
                                for ent in entities:
                                    words = ent.split()
                                    if len(words) >= 2 and words[0] not in ignore_words:
                                        # Only keep if ALL words start with capital (re.findall should guarantee this, but extra check)
                                        if all(w[0].isupper() for w in words):
                                            filtered_entities.append(ent)
                                        
                                # Create a mapping for placeholders
                                placeholder_map = {}
                                temp_p = p
                                # Sort by length descending so we replace longer entities first (e.g. San Francisco 49ers before San Francisco)
                                for idx, ent in enumerate(sorted(set(filtered_entities), key=len, reverse=True)):
                                    placeholder = f"__ENT{idx}__"
                                    placeholder_map[placeholder] = ent
                                    # Use regex replacement to match exact phrases and avoid partial replacements
                                    temp_p = re.sub(r'\b' + re.escape(ent) + r'\b', placeholder, temp_p)
                                
                                # If a paragraph is extremely long, we need to split it by sentences to translate safely
                                if len(temp_p) > 3000:
                                    sentences = re.split(r'(?<=[.!?]) +', temp_p)
                                    trans_sentences = []
                                    for s in sentences:
                                        if s.strip():
                                            try:
                                                ts = translator_instance.translate(s)
                                                trans_sentences.append(ts if ts else s)
                                            except Exception as se:
                                                print(f"DEBUG: Sentence translation error: {se}")
                                                trans_sentences.append(s)
                                    trans = " ".join(trans_sentences)
                                else:
                                    # Translate the whole chunk
                                    trans = translator_instance.translate(temp_p)
                                
                                if trans:
                                    # Restore the English entities with Japanese brackets
                                    for ph, original_ent in placeholder_map.items():
                                        trans = trans.replace(ph, f"『{original_ent}』")
                                    translated_paragraphs.append(trans)
                                else:
                                    translated_paragraphs.append(p)
                            except Exception as chunk_e:
                                print(f"DEBUG: Chunk translation error at index {i}: {chunk_e}")
                                # Try one more time without entity preservation if it failed
                                try:
                                    trans_fallback = translator_instance.translate(p[:3000])
                                    if trans_fallback:
                                        translated_paragraphs.append("⚠️(直訳) " + trans_fallback)
                                    else:
                                        translated_paragraphs.append(p)
                                except Exception:
                                    translated_paragraphs.append(p)
                    
                    # Join with double newlines to preserve Markdown paragraphs
                    full_jp_text = "\n\n".join(translated_paragraphs)
                    jp_body = f"**配信元:** {source} | **日時:** {published} \n\n[🔗 記事を読む (英語の元サイトへ)]({link})\n\n---\n\n{full_jp_text}"
            except Exception as e:
                # Fallback to placeholder if translation API fails
                st.error(f"Translation failed completely for an article: {e}")
                print(f"Translation Exception: {e}")
                pass
                
        news_items.append({
            "eng_title": eng_title,
            "eng_body": eng_body,
            "eng_text_len": len(full_eng_text),
            "jp_title": jp_title,
            "jp_body": jp_body,
            "link": link
        })
        
    return news_items

with st.spinner('Fetching latest 49ers news...'):
    news_data = fetch_49ers_news()

if not news_data:
    st.warning("ニュースの取得に失敗しました。後でもう一度お試しください。")
else:
    st.info("💡 **翻訳に関するお知らせ:** 無料の `deep-translator` (Google翻訳) を使用しているため、アメフト専門用語（プレー、ポジション名など）が不自然に翻訳される場合があります。見出しには翻訳精度向上のため擬似的に文脈を与えていますが、限界がある点をご了承ください。")
    
    # Displaying each news item using expander
    for news in news_data:
        # We use a short snippet of Japanese title for the expander header
        with st.expander(f"🏈 {news['jp_title']}"):
            st.caption(f"🔧 Debug: 抽出されたオリジナル英語本文の文字数 = {news['eng_text_len']} 文字")
            
            # --- Translated Section ---
            st.markdown("### 🇯🇵 翻訳タイトル")
            st.markdown(f"**{news['jp_title']}**")
            
            st.markdown("### 📝 日本語翻訳本文")
            st.markdown(news['jp_body'])
            
            st.divider()
            
            # --- Original English Section ---
            st.markdown("### 🇺🇸 原文タイトル (English)")
            st.markdown(f"**{news['eng_title']}**")
            
            st.markdown("### 📰 原文記事 (Original Text)")
            st.markdown(news['eng_body'])

# Sidebar information
with st.sidebar:
    st.header("About")
    st.info("This is a prototype Streamlit application for displaying translated news about the San Francisco 49ers.")
    
    st.markdown("---")
    st.caption("Powered by Streamlit")
