import os 
import time
import random
import requests

BASE_URL = os.getenv("BASE_URL", "http://nginx")
QPS = float(os.getenv("OPS", "2"))

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_1) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) "
    "Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "python-requests/2.31.0",
    "curl/8.5.0",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Bingbot/2.0 (+http://www.bing.com/bingbot.htm)"
]

paths = [
    ("/", 0.22),
    ("/products", 0.14),
    ("/product/101", 0.08),
    ("/product/102", 0.06),
    ("/search?q=shoes", 0.06),
    ("/search?q=bag", 0.04),
    ("/cart", 0.05),
    ("/checkout", 0.02),
    ("/login", 0.03),
    ("/logout", 0.01),
    ("/api/products?page=1", 0.08),
    ("/api/products?page=2", 0.04),
    ("/api/product?id=101", 0.05),
    ("/api/product?id=102", 0.03),
    ("/api/orders", 0.06),
    ("/api/orders?page=1", 0.02),
    ("/api/orders?page=2", 0.01),
    ("/favicon.ico", 0.03),
    ("/robots.txt", 0.01),
    ("/sitemap.xml", 0.01),
    ("/healthz", 0.02),
    ("/api/missing", 0.02),
    ("/wp-login.php", 0.01)
]

def pick_path():
    r = random.random()
    s = 0.0
    for p, w in paths:
        s += w
        if r <= s:
            return p
    return paths[-1][0]

while True:
    p = pick_path()
    try:
