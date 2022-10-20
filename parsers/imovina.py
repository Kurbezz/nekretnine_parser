from bs4 import BeautifulSoup
from dateutil.parser import parse

from .base import BaseParser, AnnoncementPreview, Announcement


class ImovinaParser(BaseParser):
    BASE_LINK = "https://imovina.net"
    BASE_SEARCH_LINK = "https://imovina.net/pretraga_nekretnina/izdavanje/"
    BASE_PARAMS = {
        "search": "TRA%8EI",
        "category[]": "2",
        "country": "SR",
        "mainRegion": "25",
        "region[]": "336",
        "regionName": "Centar Novi Sad",
        "offerTypeParent": "39",
        "priceFrom": "",
        "priceTo": "1000",
        "surfaceFrom": "30",
        "surfaceTo": "",
        "fastSearch": "TRAŽI",
        "offerType[]": ["5", "57", "65", "61", "1", "6", "8", "19", "58", "2", "59", "3", "60", "4"]
    }
    PAGE_PARAM = "page"

    @classmethod
    def process_previews_page(cls, bs: BeautifulSoup) -> list[AnnoncementPreview]:
        result: list[AnnoncementPreview] = []

        list_view_el = bs.find("ul", {"class": "offers2"})

        for item in list_view_el.find_all("li"):
            if len(item.contents) != 4:
                continue

            link_el = item.contents[0]
            title_el = item.contents[2]

            result.append(AnnoncementPreview(
                title=title_el.text,
                link=link_el.attrs["href"].split("?")[0],
                update_date=None,
            ))

        return result

    @classmethod
    def process_annoncement_data(cls, bs: BeautifulSoup, preview: AnnoncementPreview) -> Announcement:
        offer_details_el = bs.find("div", {"id": "offerDetailsWrapper"})
        offer_data_el = offer_details_el.find("dl", {"id": "offerData"})
        info_el = offer_details_el.find("div", {"id": "infoListId"})
        publish_info_el = offer_details_el.find("p", {"class": "offerPublished"})

        title_el = offer_details_el.find("h1")
        price_el = offer_details_el.find("div", {"id": "price_EURId"})
        description_el = info_el.contents[2]

        square = ""

        for content in offer_data_el.contents:
            if "Kvadratura m2:" in str(content):
                square = content.nextSibling.contents[0]

        return Announcement(
            title=title_el.text,
            # square=float(square),
            description=description_el.text,
            price=float(price_el.contents[0].replace(" ", "").replace("EUR", "")),
            update_date=parse(publish_info_el.text.split("dana ")[1].split(" god")[0]).date(),
            link=preview.link
        )

