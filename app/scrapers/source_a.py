from bs4 import BeautifulSoup

from app.scrapers.base import BaseScraper


class BooksToScrapeScraper(BaseScraper):
    BASE_URL = "https://books.toscrape.com"

    def parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        products = []
        books = soup.find_all("article", class_="product_pod")
        for book in books:
            title = book.find("h3").find("a")["title"]
            price = book.find("p", class_="price_color").text
            availability_text = book.find("p", class_="availability").text
            available = "In stock" in availability_text
            link = book.find("h3").find("a")["href"]

            data = {
                "title": title,
                "price": price,
                "available": available,
                "link": link,
            }
            products.append(data)
        return products
