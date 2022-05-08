#TODO add doc
import os
import requests
import pandas as pd

from bs4 import BeautifulSoup

class Fields(object):
    COMPANY = "Company"
    SECTOR = "Sector"
    COUNTRY = "Country"
    FUND = "Fund"
    ENTRY = "Entry"
    EXIT = "Exit"
    SDG = "SDG"

REPEATED_FIELDS = [Fields.FUND]
NONREPEATED_FIELDS = [Fields.COMPANY]

class Base(object):

    class Fields(object):
        COMPANY = "Company"
        SECTOR = "Sector"
        COUNTRY = "Country"
        FUND = "Fund"
        ENTRY = "Entry"
        SDG = "SDG"

    @classmethod
    def _get_unordered_list(cls):
        page = requests.get(cls.URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        [ul] = soup.find_all("ul", class_="sm:border-t sm:border-neutral-light") #TODO check this
        return ul

    @staticmethod
    def get_company(x):
        [span] = x.findAll("span", class_="inline-block") # TODO check this
        return span.get_text()

    @classmethod
    def get_values(cls, x, text):
        siblings = x.find(text=text).parent.findNextSiblings()
        if text == Fields.SDG:
            [sibling] = siblings
            parts = [number, text] = [x.get_text() for x in sibling.find("div").children]
            values = [" ".join(parts)]
        else:
            values = [x.get_text().strip() for x in siblings]
        return tuple(values)

    @classmethod
    def get_value(cls, *args, **kwargs):
        [value] = cls.get_values(*args, **kwargs)
        return value

    @classmethod
    def _parse_li(cls, li):
        parsed_nonrepeated = {x: cls.get_value(li, x) for x in cls.nonrepeated_fields}
        parsed_repeated = {x: cls.get_values(li, x) for x in cls.repeated_fields}

        parsed = dict(
            Company=cls.get_company(li),
            **parsed_nonrepeated,
            **parsed_repeated
        )
        return parsed

    @classmethod
    def get_dataframe(cls, cache=None):
        if cache and os.path.exists(cache):
            df = pd.read_json(cache)
        else:
            unordered_list = cls._get_unordered_list()

            items = []
            for li in unordered_list:
                parsed = cls._parse_li(li)
                items.append(parsed)

            df = pd.DataFrame(items)
            df.Company = df.Company.str.strip() #TODO handle in earlier step
            df.drop_duplicates(ignore_index=True, inplace=True)
        if cache:
            df.to_json(cache)
        return df


class CurrentPortfolio(Base):
    URL = "https://eqtgroup.com/current-portfolio"
    nonrepeated_fields = [
        Fields.COUNTRY,
        Fields.SECTOR,
        Fields.ENTRY,
        Fields.SDG,
    ]
    repeated_fields = [Fields.FUND]


class Divestments(Base):
    URL = "https://eqtgroup.com/current-portfolio/divestments"
    nonrepeated_fields = [
        Fields.SECTOR,
        Fields.COUNTRY,
        Fields.ENTRY,
        Fields.EXIT,
    ]
    repeated_fields = [Fields.FUND]


if __name__ == "__main__":
    df_current_portfolio = CurrentPortfolio.get_dataframe()
    df_divestments = Divestments.get_dataframe()
    print(df_current_portfolio)
    print(df_divestments)
