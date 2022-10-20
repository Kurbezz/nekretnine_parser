from bs4 import BeautifulSoup
import dateparser


from .base import BaseParser, AnnoncementPreview, Announcement

class FzidaParser(BaseParser):
    BASE_LINK = "https://www.4zida.rs"
    BASE_SEARCH_LINK = "https://www.4zida.rs/izdavanje-stanova/novi-sad"
    BASE_PARAMS = {
        "jeftinije_od": "1000eur",
        "vece_od": "36m2",
        "namesteno": ["namesteno", "polunamesteno"],
        "sortiranje": "najnoviji"
    }
    PAGE_PARAM = "strana"

    @classmethod
    def process_previews_page(cls, bs: BeautifulSoup) -> list[AnnoncementPreview]:
        result: list[AnnoncementPreview] = []

        for item in bs.find_all("app-ad-search-preview"):
            title_el = item.find("h3", {"class": "description"})
            link_el = item.find("a")

            result.append(AnnoncementPreview(
                title=title_el.text,
                link=cls.BASE_LINK + link_el.attrs["href"],
                update_date=None
            ))

        return result

    @classmethod
    def process_annoncement_data(cls, bs: BeautifulSoup, preview: AnnoncementPreview) -> Announcement:
        description_el = bs.find("pre", {"class": "ed-description collapsed-description ng-star-inserted"})
        price_el = bs.find("div", {"class": "prices"})
        update_date_el = bs.find("app-info-item", {"label": "Oglas proveren"})
        update_date_value_el = update_date_el.find("strong", {"class": "value"})

        update_date_value = update_date_value_el.text \
            .replace("pre", "ago") \
            .replace("dan", "day") \
            .replace("minuta", "minute") \
            .replace("sati", "hour") \
            .replace("daya", "day") \
            .replace("sekunde", "second") \
            .replace("minut", "minute") \
            .replace("minutee", "minute") \
            .replace("sekundi", "second") \
            .replace("sat", "hour") \
            .replace("houra", "hour") \
            .replace("mesec", "month") \
            .replace("montha", "month")

        update_date = dateparser.parse(update_date_value)

        if update_date is None:
            raise Exception(f"Update_date from {update_date_value}!")

        return Announcement(
            title=description_el.text if description_el else "",
            # square=float(square_value),
            description=description_el.text if description_el else "",
            price=float(price_el.text.split("\xa0")[0].split(".")[0].replace(",", ".")),
            update_date=update_date.date(),
            link=preview.link
        )
