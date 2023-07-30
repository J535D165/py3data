import json

import pytest
from requests import HTTPError

import py3data
from py3data import Repositories
from py3data import Repository

RANDOM_REPOS = [
    "r3d100014130",
    "r3d100013901",
    "r3d100012756",
    "r3d100012808",
    "r3d100010135",
    "r3d100010154",
    "r3d100010622",
    "r3d100011512",
    "r3d100011784",
    "r3d100012119",
    "r3d100012990",
    "r3d100013000",
    "r3d100013022",
    "r3d100011189",
    "r3d100012793",
]


def test_config():
    py3data.config.email = "py3data_github_unittests@example.com"
    assert py3data.config.email == "py3data_github_unittests@example.com"


@pytest.mark.parametrize("re3data_id", RANDOM_REPOS)
def test_singleton(re3data_id):

    assert isinstance(Repositories()[re3data_id], Repository)
    assert isinstance(Repositories()[re3data_id]["repositoryName"], str)


def test_singleton_error():

    with pytest.raises(HTTPError):
        Repositories()["NotAWorkID"]


def test_singleton_serialize():

    json.dumps(Repositories()["r3d100011986"], indent=2)


def test_collection():

    res = Repositories().get()

    assert isinstance(res, list)
    assert isinstance(res[0], Repository)


def test_collection_url():

    url_expected = "https://www.re3data.org/api/beta/repositories?countries[]=CAN&subjects[]=2%20Life%20Sciences&subjects[]=3%20Natural%20Sciences&pidSystems[]=DOI&query=University"

    url_single = (
        Repositories()
        .filter(
            countries="CAN",
            subjects=["2 Life Sciences", "3 Natural Sciences"],
            pidSystems="DOI",
        )
        .query("University")
        .url
    )

    url_pipe = (
        Repositories()
        .filter(countries="CAN")
        .filter(subjects=["2 Life Sciences", "3 Natural Sciences"])
        .filter(pidSystems="DOI")
        .query("University")
        .url
    )

    assert url_single == url_pipe == url_expected


def test_collection_filter_query():

    get_no_query = (
        Repositories()
        .filter(countries="CAN")
        .filter(subjects=["2 Life Sciences", "3 Natural Sciences"])
        .filter(pidSystems="DOI")
        .get()
    )

    get_query = (
        Repositories()
        .filter(countries="CAN")
        .filter(subjects=["2 Life Sciences", "3 Natural Sciences"])
        .filter(pidSystems="DOI")
        .query("University")
        .get()
    )

    assert len(get_no_query) > len(get_query)


def test_unparsed_records():
    def _is_unparsed(d):

        for k, v in d.items():

            print(k, v)
            if isinstance(v, dict) and _is_unparsed(v):
                return True
            elif isinstance(v, list):
                for vi in v:
                    if isinstance(vi, dict) and _is_unparsed(vi):
                        return True
            else:
                if "@" in k:
                    return True

        return False

    get_queries = (
        Repositories()
        .filter(countries="CAN")
        .filter(subjects=["2 Life Sciences", "3 Natural Sciences"])
        .get()
    )

    for repo in get_queries:

        print(repo["id"])
        assert not _is_unparsed(Repositories()[repo["id"]])


pytest.mark.skip(reason="Extend test for testing list types")


def test_list_types():

    get_queries = (
        Repositories()
        .filter(countries="CAN")
        .filter(subjects=["2 Life Sciences", "3 Natural Sciences"])
        .get()
    )

    list_types_set = set()

    for repo in get_queries:

        repo_full = Repositories()[repo["id"]]

        for k, v in repo_full.items():
            if isinstance(v, list):
                list_types_set.add(k)

    print(list(list_types_set))
