import streamlit as st

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

# Dummy Data representing the fetched and translated news
news_data = [
    {
        "eng_title": "49ers Secure Crucial Victory in Overtime Thriller",
        "eng_body": "The San Francisco 49ers pulled off a stunning overtime win on Sunday, showcasing their resilient defense and explosive offense to keep their playoff hopes alive.",
        "jp_title": "49ers、延長戦の激闘を制し重要な勝利を収める",
        "jp_body": "サンフランシスコ・49ersは日曜日の試合で驚異的な延長戦での勝利を収め、粘り強いディフェンスと爆発力のあるオフェンスを見せつけ、プレーオフ進出への希望を繋ぎました。"
    },
    {
        "eng_title": "Star Quarterback Returns to Practice After Injury",
        "eng_body": "In a major boost for the team, the 49ers' starting quarterback was seen practicing with the first team today, raising hopes for his return next week.",
        "jp_title": "スターQB、ケガから復帰し練習に参加",
        "jp_body": "チームにとって大きな追い風となるニュースです。49ersの先発クォーターバックが今日、主力チームとの練習に参加しているのが目撃され、来週の復帰への期待が高まっています。"
    },
    {
        "eng_title": "Defense Dominates: 5 Sacks and 3 Interceptions",
        "eng_body": "The 49ers defense delivered a masterclass performance, recording five sacks and forcing three crucial interceptions to shut down the opposing offense.",
        "jp_title": "ディフェンスが圧倒：5サックと3インターセプトを記録",
        "jp_body": "49ersのディフェンス陣は、5つのサックを記録し、3つの決定的なインターセプトを奪うという完璧なパフォーマンスを見せ、相手オフェンスを完全に封じ込めました。"
    }
]

# Displaying each news item
for news in news_data:
    # Do not indent the HTML string inside st.markdown, 
    # as Streamlit's markdown parser will treat 4-space indentations as code blocks.
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
