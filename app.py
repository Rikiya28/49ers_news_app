import streamlit as st
import feedparser
import re
import html

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
    
    /* News Container */
    .news-container {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border-left: 6px solid #AA0000;
        border-right: 6px solid #B3995D;
    }
    .eng-title {
        color: #555;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .eng-body {
        color: #777;
        font-style: italic;
        font-size: 0.95rem;
        margin-bottom: 15px;
        padding-left: 10px;
        border-left: 3px solid #ddd;
    }
    .jp-title {
        color: #AA0000;
        font-size: 1.3rem;
        font-weight: 900;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .jp-body {
        color: #222;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .divider {
        height: 2px;
        background: linear-gradient(to right, #AA0000, #B3995D);
        margin: 15px 0;
        border-radius: 1px;
    }
    .lang-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
        vertical-align: middle;
    }
    .badge-en {
        background-color: #e9ecef;
        color: #495057;
    }
    .badge-jp {
        background-color: #AA0000;
        color: #FFFFFF;
        border: 1px solid #AA0000;
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
    # Using Google News RSS for 49ers
    rss_url = "https://news.google.com/rss/search?q=San+Francisco+49ers&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    
    # Get top 5 news items
    for entry in feed.entries[:5]:
        eng_title = entry.title
        
        # Google News summary is usually HTML. We extract actual text if possible.
        raw_summary = getattr(entry, 'summary', '')
        clean_summary = html.unescape(re.sub('<[^<]+?>', '', raw_summary)).strip()
        
        # Remove repeated title from the beginning of google news summary if present
        if clean_summary.startswith(eng_title):
            clean_summary = clean_summary.replace(eng_title, "", 1).strip()
            
        source = getattr(entry, 'source', {}).get('title', 'Google News')
        published = getattr(entry, 'published', '')
        link = getattr(entry, 'link', '')
        
        # Build English body
        summary_disp = f"{clean_summary}<br/><br/>" if clean_summary else ""
        eng_body = f"{summary_disp}Source: {source} <br/> Published: {published} <br/> <a href='{link}' target='_blank'>Read Full Article</a>"
        
        # Default placeholder for translation
        jp_title = "翻訳結果：考え中..."
        jp_body = f"{summary_disp}配信元: {source} <br/> 日時: {published} <br/> <a href='{link}' target='_blank'>記事を読む (英語)</a>"
        
        if translator_instance:
            try:
                # Attempt to translate the title
                translated_title = translator_instance.translate(eng_title)
                if translated_title:
                    jp_title = translated_title
                
                # Attempt to translate the summary if present
                if clean_summary:
                    translated_summary = translator_instance.translate(clean_summary)
                    if translated_summary:
                        jp_body = f"{translated_summary}<br/><br/>配信元: {source} <br/> 日時: {published} <br/> <a href='{link}' target='_blank'>記事を読む (英語)</a>"
            except Exception as e:
                # Fallback to placeholder if translation API fails
                st.error(f"Translation failed: {e}")
                print(f"Translation Exception: {e}")
                pass
                
        news_items.append({
            "eng_title": eng_title,
            "eng_body": eng_body,
            "jp_title": jp_title,
            "jp_body": jp_body
        })
        
    return news_items

with st.spinner('Fetching latest 49ers news...'):
    news_data = fetch_49ers_news()

if not news_data:
    st.warning("ニュースの取得に失敗しました。後でもう一度お試しください。")
else:
    # Displaying each news item
    for news in news_data:
        html_content = f"""<div class="news-container">
    <div class="eng-title"><span class="lang-badge badge-en">EN</span> {news['eng_title']}</div>
    <div class="eng-body">{news['eng_body']}</div>
    <div class="divider"></div>
    <div class="jp-title"><span class="lang-badge badge-jp">JP</span> {news['jp_title']}</div>
    <div class="jp-body">{news['jp_body']}</div>
    </div>"""
        st.markdown(html_content, unsafe_allow_html=True)

# Sidebar information
with st.sidebar:
    st.header("About")
    st.info("This is a prototype Streamlit application for displaying translated news about the San Francisco 49ers.")
    
    st.markdown("---")
    st.caption("Powered by Streamlit")
