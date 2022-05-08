import pandas as pd
from pathlib import Path
import urllib.request
import gzip
import shutil

class Base(object):

    def __init__(self, dirpath):
        self.dirpath = Path(dirpath)
        self.path = self.dirpath / f"{self.filename}"

    def download(self):
        url = f"https://storage.googleapis.com/motherbrain-external-test/{self.filename}.gz"
        gz_path = Path(f"{self.path}.gz")
        if not self.path.exists() and not gz_path.exists():
            print(f"Downloading {self}...")
            urllib.request.urlretrieve(url, gz_path)
            print("Done!")
        if not self.path.exists():
            with gzip.open(gz_path, 'rb') as f_in, open(self.path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    def get_dataframe(self):
        return pd.read_json(self.path, lines=True)

    def __str__(self):
        name = self.__class__.__name__
        path = str(self.path)
        return f"{name}({path})"


class Funding(Base):
    filename = "interview-test-funding.json"

class Org(Base):
    filename = "interview-test-org.json"

    # clean this up
    not_found = ['Allee Center', 'Anticimex', 'Beijer Ref', 'Bluestep Bank', 'Cast & Crew', 'Cerba Healthcare', 'Colisee', 'Cypress Creek', 'DELTA Fiber', 'EC-Council', 'Facile', 'Fiberklaar', 'First Student and First Transit', 'GlobalConnect', 'HMI Group', 'IVC Evidensia', 'Icon Group', 'Idealista', 'Indesso', 'Kodiak Gas Services, LLC', 'Kuoni Group / VFS Global', 'MHC Asia', 'ManyPets', 'Meine Radiologie / Blikk', 'Melita', 'Metlifecare', 'O2 Power', 'Oterra', 'Parexel', 'Recover', 'SAUR', 'SEGRA', 'SHL Medical', 'Saturn', 'Schülke', 'Smart Parc', 'Solarpack', 'Southside', 'Stendörren', 'Storable', 'Svenska Verksamhetsfastigheter', 'Torghatten', 'Unum', 'Utimaco', 'WASH', 'thinkproject']
    uncertain = ['Azelis', 'Banking Circle', 'Campus', 'Concept', 'Dunlop', 'GPA Global', 'Lima', 'Mambu', 'Minerva', 'Nest', 'Osmose Utilities Services, Inc.', 'RIMES Technologies', 'Sitecore', 'WS Audiology']
    likely_same_but_country_mismatch_web = ['Azelis', 'Banking Circle']


if __name__ == "__main__":
    df_funding = Funding.get_dataframe()
    df_org = Org.get_dataframe()
