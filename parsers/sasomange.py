from bs4 import BeautifulSoup
from dateutil.parser import parse

from .base import BaseParser, AnnoncementPreview, Announcement


class SasomangleParser(BaseParser):
    BASE_LINK = "https://sasomange.rs"
    BASE_SEARCH_LINK = "https://sasomange.rs/c/stanovi-iznajmljivanje/f/novi-sad"
    BASE_PARAMS = {
        "productsFacets.facets": "priceValue:(*-1000),facility_area_range_flat_rent:(36-*)"
    }
    PAGE_PARAM = "currentPage"

    @classmethod
    def process_previews_page(cls, bs: BeautifulSoup) -> list[AnnoncementPreview]:
        result: list[AnnoncementPreview] = []

        list_view_el = bs.find("ul", {"class": "list-view js-list-view-item"})

        for item in list_view_el.find_all("a", {"class": "product-item"}):
            title_el = item.find("h3", {"class": "name"})
            update_date = item.find("div", {"class": "start-date-content"})

            result.append(AnnoncementPreview(
                title=title_el.text,
                update_date=parse(update_date.text[:-1]).date(),
                link=cls.BASE_LINK + item.attrs["href"],
            ))

        return result

    @classmethod
    def process_annoncement_data(cls, bs: BeautifulSoup, preview: AnnoncementPreview) -> Announcement:
        title_el = bs.find("h1", {"class": "name"})
        description_el = bs.find("div", {"class": "body-text-content"})
        price_el = bs.find("span", {"class": "price-content"})
        date_el = bs.find("em", {"class": "icon icon-clock"})
        date_value_el = date_el.parent.find("span", {"class": "value"})

        date_text = date_value_el.text.rstrip().lstrip()[:-1]

        # square_value = ""
        # product_attributes_el = bs.find("ul", {"class": "product-attributes-list"})
        # for attribute in product_attributes_el.find_all("li", {"class": "list-item"}):
        #     if "Površina" in attribute.text:
        #         square_value_el = attribute.find("p", {"class": "value"})
        #         square_value = square_value_el.contents[1].text

        return Announcement(
            title=title_el.text,
            # square=float(square_value),
            description=description_el.text,
            price=float(price_el.text.split("\xa0")[0].split(".")[0].replace(",", ".")),
            update_date=parse(date_text).date(),
            link=preview.link
        )
