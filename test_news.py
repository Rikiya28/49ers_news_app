import feedparser
import requests
from newspaper import Article

rss_url = "https://www.ninersnation.com/rss/current.xml"
feed = feedparser.parse(rss_url)

for entry in feed.entries[:3]:
    link = entry.link
    print(link)
    article = Article(link)
    article.download()
    article.parse()
    print(f"Text len: {len(article.text)}")
    print(article.text[:100])
    print("-" * 50)
