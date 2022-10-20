import json

from bs4 import BeautifulSoup
from dateutil.parser import parse

from .base import BaseParser, AnnoncementPreview, Announcement


class HalooglasiParser(BaseParser):
    BASE_LINK = "https://www.halooglasi.com"
    BASE_SEARCH_LINK = "https://www.halooglasi.com/nekretnine/izdavanje-stanova/novi-sad"
    BASE_PARAMS = {
        "cena_d_to": 1000,
        "cena_d_unit": 4,
        "kvadratura_d_from": 30,
        "kvadratura_d_unit": 1,
        "namestenost_id_l": "563,562"
    }
    PAGE_PARAM = "page"

    @classmethod
    def process_previews_page(cls, bs: BeautifulSoup) -> list[AnnoncementPreview]:
        result: list[AnnoncementPreview] = []

        product_list_el = bs.find("div", {"class": "row product-list"})

        for product_el in product_list_el.find_all("div", {"class": "col-md-12 col-sm-12 col-xs-12 col-lg-12"}):
            publish_date_el = product_el.find("span", {"class": "publish-date"})
            title_el = product_el.find("h3", {"class": "product-title"})
            link_el = title_el.find("a")
            # features_el = product_el.find("ul", {"class": "product-features"})

            result.append(
                AnnoncementPreview(
                    title=title_el.text,
                    # square=float(features_el.contents[0].text.split("\xa0")[0]),
                    # floor=float(features_el.contents[1].text.split("\xa0")[0].replace("+", "")),
                    update_date=parse(publish_date_el.text[:-1]).date(),
                    link=cls.BASE_LINK + link_el.attrs["href"],
                )
            )

        return result

    @classmethod
    def process_annoncement_data(cls, bs: BeautifulSoup, preview: AnnoncementPreview) -> Announcement:
        pre_content = bs.find("div", {"class": "pre-content"})

        data_div = pre_content.contents[3].find("script")
        data_string = data_div.text.split("\r\n")[2] \
            .replace("\tQuidditaEnvironment.CurrentClassified=", "") \
            .replace("; for (var i in QuidditaEnvironment.CurrentClassified.OtherFields) { QuidditaEnvironment.CurrentClassified[i] = QuidditaEnvironment.CurrentClassified.OtherFields[i]; };", "")

        data = json.loads(data_string)

        return Announcement(
            title=data["Title"],
            # square=data["OtherFields"]["kvadratura_d"],
            # floor=float(data["OtherFields"]["broj_soba_s"].replace("+", "")),
            description=data["TextHtml"],
            price=data["OtherFields"]["cena_d"],
            update_date=parse(data["ValidFrom"]).date(),
            link=preview.link
        )
