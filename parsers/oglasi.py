from bs4 import BeautifulSoup
from dateutil.parser import parse

from .base import BaseParser, AnnoncementPreview, Announcement


class OglasiParser(BaseParser):
    BASE_LINK = "https://www.oglasi.rs"
    BASE_SEARCH_LINK = "https://www.oglasi.rs/nekretnine/izdavanje-stanova/novi-sad"
    BASE_PARAMS = {
        "s": "d",
        "pr[e]": "1000",
        "pr[c]": "EUR",
        "d[Kvadratura][0]": "30",
        "d[Kvadratura][1]": "40",
        "d[Kvadratura][2]": "50",
        "d[Kvadratura][3]": "60",
        "d[Kvadratura][4]": "70",
        "d[Kvadratura][5]": "80",
        "d[Kvadratura][6]": "90",
        "d[Kvadratura][7]": "100",
        "d[Kvadratura][8]": "110",
        "d[Kvadratura][9]": "120",
        "d[Kvadratura][10]": "130",
        "d[Kvadratura][11]": "140"
    }
    PAGE_PARAM = "p"

    @classmethod
    def process_previews_page(cls, bs: BeautifulSoup) -> list[AnnoncementPreview]:
        result: list[AnnoncementPreview] = []

        for item in bs.find_all("div", {"class": "fpogl-holder advert_list_item_normalan"}):
            title_el = item.find("h2", {"itemprop": "name"})
            update_date_el = item.find("time")
            link_el = item.find("a", {"class": "fpogl-list-title"})

            result.append(
                AnnoncementPreview(
                    title=title_el.text,
                    update_date=parse(update_date_el.attrs["datetime"]).date(),
                    link=cls.BASE_LINK + link_el.attrs["href"],
                )
            )

        return result

    @classmethod
    def process_annoncement_data(cls, bs: BeautifulSoup, preview: AnnoncementPreview) -> Announcement:
        description_el = bs.find("div", {"itemprop": "description"})
        price_el = bs.find("span", {"itemprop": "price"})
        time = bs.find("time")

        # attr_table = bs.find("table")
        # attrs_els = attr_table.find_all("tr")

        # square = ""
        # for attr in attrs_els:
        #     if "Kvadratura" in attr.text:
        #         square = attr.contents[3].text.split("m")[0].lstrip()

        return Announcement(
            title=preview.title,
            # square=float(square),
            description=description_el.text,
            price=float(price_el.text.split(",")[1]) if price_el else -1.0,
            update_date=parse(time.text).date(),
            link=preview.link
        )
