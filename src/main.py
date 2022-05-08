from pathlib import Path
import pandas as pd
import stringcase
import pycountry
import json

from cmdline import parse_args
from eqt_homepage import CurrentPortfolio, Divestments
from reference_datasets import Funding, Org

get_source_name = lambda source: stringcase.snakecase(source.__name__)

def country_to_country_code(country):
    """ Handle country values as found on the websize.
    """
    if country == "Dubai":
        country = "United Arab Emirates"
    return pycountry.countries.search_fuzzy(country)[0].alpha_3


class Pipeline(object):

    def __init__(self, data_dir):
        """
        Args:
            data_dir: where to store pipeline outputs
        """
        self.data_dir = Path(data_dir)
        self.org = Org(data_dir)
        self.funding = Funding(data_dir)

    @staticmethod
    def select_enrichment_data(df, additional_data, key):
        print(f"Select data from {additional_data}")
        assert isinstance(key, list)
        df = df[key]

        df_additional = additional_data.get_dataframe()
        df_extracted = df.merge(df_additional, on=key, how="left")[df_additional.columns]
        import ipdb;ipdb.set_trace()
        if isinstance(additional_data, Funding):
            [key] = key
            group = "funding_rounds"
            cols = [key, group]
            df_extracted = df_extracted.set_index(key).dropna(how="all").reset_index()
            df_extracted[group] = (
                df_extracted
                .drop(key, axis=1) # non-additional information
                .apply(dict, axis=1)
            )
            df_extracted = df_extracted[cols].groupby(key).agg(list).reset_index()
            df_extracted = df.merge(df_extracted, on=key, how="left")[cols]

        return df_extracted

    def enrich_with_org_and_funding(self, source, cache=None):
        """ Given either the Current Porfolio, or Divestments,
        this function will match those companies against the entries in the
        Org and Funding datasets.

        Considerations for the matching algorithm used:
        - the Org and Funding datasets have `company uuid`, which seem ideal for matching entries
        between these two datasets.
        - since I did not find company uuid info on the eqt-website, I will try to
        match the website data, with the Org data, using as many matching/relevant fields possible:
        currently this is done by matching company name and country.
        - (Once a company has been identified, proceed to use company uuid for identification)
        """
        df = source.get_dataframe(cache=cache)
        df.columns = df.columns.str.lower()

        # creating keys which will be used to match with org data
        df.rename({"company":"company_name"}, inplace=True, axis=1)
        df["country_code"] = df.country.apply(country_to_country_code)

        org_key = ["company_name", "country_code"]
        df_org = self.select_enrichment_data(df, self.org, key=org_key)
        assert df.index.size == df_org.index.size, "More than 1 org-entry per company!"

        # renaming column, will now use uuid to match with funding data
        df_org.rename({"uuid":"company_uuid"}, inplace=True, axis=1)
        funding_key = ["company_uuid"]
        df_funding = self.select_enrichment_data(df_org, self.funding, key=funding_key)

        dfs = {
            get_source_name(source): df.drop("country_code", axis=1),
            "org": df_org.drop(org_key, axis=1),
            "funding": df_funding.drop(funding_key, axis=1)
        }
        df_enriched = pd.concat(dfs, axis=1)
        summary = pd.Series(dict(
            n_companies=df_enriched.org.index.size,
            n_org_found=df_enriched.org.notnull().any(axis=1).sum()
        ))
        print(summary)
        return df_enriched

    def enrich_and_save(self, source, cache=None):
        source_name = get_source_name(source)
        path = self.data_dir / f"{source_name}_enriched.ndjson"
        df = self.enrich_with_org_and_funding(source, cache)
        with open(path, 'w') as fh:
            for ix in df.index:
                row = df.iloc[ix]
                _dict = dict()
                for name in df.columns.levels[0]:
                    _dict[name] = json.loads(row[name].to_json()) #NaN handling
                _json = json.dumps(_dict)
                fh.write(f"{_json}\n")

    def run(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

        for ds in [self.org, self.funding]:
            ds.download()

        for source in [CurrentPortfolio, Divestments]:
            print()
            print(f"Enriching {source}...")
            self.enrich_and_save(
                source,
                #cache=cache/get_source_name(source)
            )
            print(f"Enriching {source} DONE!")


    @classmethod
    def main(cls, data_dir):
        """ This function will run the assignment pipeline.

        Arguments:
            data_dir: where to keep data generated by this program
        """
        pipeline = cls(data_dir)
        pipeline.run()


if __name__ == "__main__":
    namespace = parse_args()
    Pipeline.main(namespace.data_dir)
