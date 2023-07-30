import logging
import re
from urllib.parse import quote

import requests

from py3data import xmltodict

try:
    from py3data._version import __version__
except ImportError:
    __version__ = "0.0.0"


class Config(dict):
    def __getattr__(self, key):
        return super().__getitem__(key)

    def __setattr__(self, key, value):
        return super().__setitem__(key, value)


LIST_TYPES = [
    "pidSystems",
    "repositoryContacts",
    "institutions",
    "software",
    "apis",
    "additionalNames",
    "contentTypes",
    "policies",
    "certificates",
    "dataAccess",
    "subjects",
    "dataLicenses",
    "syndications",
    "dataUploadLicense",
    "types",
    "keywords",
    "aidSystems",
    "dataUploads",
    "repositoryIdentifier",
    "metadataStandards",
    "repositoryLanguages",
    "providerTypes",
]

MAPPING = {
    "aidSystem": "aidSystems",
    "api": "apis",
    "additionalName": "additionalNames",
    "certificate": "certificates",
    "contentType": "contentTypes",
    "country": "countries",
    "dataAccess": "dataAccess",
    "dataAccessRestriction": "dataAccessRestrictions",
    "databaseAccess": "databaseAccess",
    "databaseAccessRestriction": "databaseAccessRestrictions",
    "databaseLicense": "databaseLicenses",
    "dataLicense": "dataLicenses",
    "dataUpload": "dataUploads",
    "dataUploadLicense": "dataUploadLicenses",
    "dataUploadRestriction": "dataUploadRestrictions",
    "enhancedPublication": "enhancedPublication",
    "institution": "institutions",
    "institutionType": "institutionType",
    "keyword": "keywords",
    "metadataStandard": "metadataStandards",
    "pidSystem": "pidSystems",
    "policy": "policies",
    "providerType": "providerTypes",
    "qualityManagement": "qualityManagement",
    "repositoryIdentifier": "repositoryIdentifiers",
    "repositoryLanguage": "repositoryLanguages",
    "repositoryContact": "repositoryContacts",
    "responsibilityType": "responsibilityTypes",
    "subject": "subjects",
    "syndication": "syndications",
    "type": "types",
}

config = Config(email=None, api_url="https://www.re3data.org/api/beta/")


def _fix_schema(d):

    new_d = {}

    for k, v in d.items():

        # rename items
        if k in MAPPING:
            k = MAPPING[k]

        # make lists out of list_types
        if k in LIST_TYPES and v == "none":
            v = None
        if k in LIST_TYPES and v is not None and not isinstance(v, list):
            v = [v]

        new_d[k] = v

    if "subjects" in new_d:
        subjects = []
        for s in new_d["subjects"]:
            subjects.append(
                {"subjectScheme": s["@subjectScheme"], "subjectName": s["#text"]}
            )
        new_d["subjects"] = subjects

    if "syndications" in new_d:
        syndication_types = []
        for s in new_d["syndications"]:
            syndication_types.append(
                {"syndicationType": s["@syndicationType"], "syndication": s["#text"]}
            )
        new_d["syndications"] = syndication_types

    if "contentTypes" in new_d:
        content_types = []
        for s in new_d["contentTypes"]:
            content_types.append(
                {
                    "contentTypeScheme": s["@contentTypeScheme"],
                    "contentTypeName": s["#text"],
                }
            )
        new_d["contentTypes"] = content_types

    if "apis" in new_d:
        apis = []
        for s in new_d["apis"]:
            apis.append({"apiType": s["@apiType"], "api": s["#text"]})
        new_d["apis"] = apis

    if "metadataStandards" in new_d:
        md_standard = []
        for s in new_d["metadataStandards"]:
            md_standard.append(
                {
                    "metadataStandardScheme": s["metadataStandardName"][
                        "@metadataStandardScheme"
                    ],
                    "metadataStandardName": s["metadataStandardName"]["#text"],
                }
            )
        new_d["metadataStandards"] = md_standard

    if "institutions" in new_d:

        res_institutions = []
        for institution in new_d["institutions"]:

            if "institutionAdditionalName" in institution:

                if isinstance(institution["institutionAdditionalName"], dict):
                    institution["institutionAdditionalName"] = institution[
                        "institutionAdditionalName"
                    ]["#text"]

                if not isinstance(institution["institutionAdditionalName"], list):
                    institution["institutionAdditionalName"] = [
                        institution["institutionAdditionalName"]
                    ]

                institution["institutionAdditionalNames"] = institution[
                    "institutionAdditionalName"
                ]
                del institution["institutionAdditionalName"]
            res_institutions.append(institution)

        new_d["institutions"] = res_institutions

    if "size" in new_d:
        new_d["sizeUpdated"] = new_d["size"]["@updated"]
        if "#text" in new_d["size"] and new_d["size"]["#text"]:
            new_d["size"] = new_d["size"]["#text"]
        else:
            new_d["size"] = None

    if "versioning" in new_d and new_d["versioning"] == "yes":
        new_d["versioning"] = True
    if "versioning" in new_d and new_d["versioning"] == "no":
        new_d["versioning"] = False

    return new_d


def _params_merge(params, add_params):

    for k, _v in add_params.items():
        if (
            k in params
            and isinstance(params[k], dict)
            and isinstance(add_params[k], dict)
        ):
            _params_merge(params[k], add_params[k])
        elif (
            k in params
            and not isinstance(params[k], list)
            and isinstance(add_params[k], list)
        ):
            # example: params="a" and add_params=["b", "c"]
            params[k] = [params[k]] + add_params[k]
        elif (
            k in params
            and isinstance(params[k], list)
            and not isinstance(add_params[k], list)
        ):
            # example: params=["b", "c"] and add_params="a"
            params[k] = params[k] + [add_params[k]]
        elif k in params:
            params[k] = [params[k], add_params[k]]
        else:
            params[k] = add_params[k]


class Repository(dict):
    pass


class Repositories:
    """Base class for repositories"""

    resource_class = Repository

    def __init__(self, params=None):

        self.params = params

    def __getattr__(self, key):

        return getattr(self, key)

    def __getitem__(self, record_id):

        if isinstance(record_id, list):
            return self._get_multi_items(record_id)

        url = config.api_url + "repository/" + record_id
        res = requests.get(
            url,
            headers={"User-Agent": "py3data/" + __version__, "From": config.email},
        )
        res.raise_for_status()

        text_clean = res.text.replace("r3d:", "")
        text_clean = re.sub(r" language=\"\w+\"", "", text_clean)

        res_xml = xmltodict.parse(text_clean, process_namespaces=False)["re3data"][
            "repository"
        ]

        res_xml = _fix_schema(res_xml)

        return self.resource_class(res_xml)

    @property
    def url(self):

        if not self.params:
            return config.api_url + "repositories"

        l_params = []
        for k, v in self.params.items():

            if v is None:
                pass
            elif isinstance(v, list):
                for q in v:
                    l_params.append(k + "=" + quote(q))
            else:
                l_params.append(k + "=" + quote(str(v)))

        if l_params:
            return config.api_url + "repositories" + "?" + "&".join(l_params)

        return config.api_url + "repositories"

    def count(self):
        m = self.get()

        return len(m)

    def get(self):

        res = requests.get(
            self.url,
            headers={"User-Agent": "py3data/" + __version__, "From": config.email},
        )
        res.raise_for_status()

        res_dict = xmltodict.parse(res.text)

        # Fix link results
        res_dict_new = []
        for repo in res_dict["list"]["repository"]:
            repo["link"] = repo["link"]["@href"]
            res_dict_new.append(repo)

        results = [self.resource_class(ent) for ent in res_dict_new]

        return results

    def _add_params(self, argument, new_params):

        if self.params is None:
            self.params = {argument: new_params}
        elif argument in self.params and isinstance(self.params[argument], dict):
            _params_merge(self.params[argument], new_params)
        else:
            self.params[argument] = new_params

        logging.debug("Params updated:", self.params)

    def filter(self, **kwargs):

        for k, v in kwargs.items():
            self._add_params(f"{k}[]", v)

        return self

    def query(self, q):

        self._add_params("query", q)
        return self
