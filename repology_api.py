from requests import Request, Session
from dataclasses import dataclass
from urllib.parse import urlunsplit


@dataclass
class RepologyApi:
    scheme: str = "https"
    host: str = "repology.org"
    base_path: str = "/api/v1"
    prepare: bool = False
    send: bool = False
    session: Session = None

    def __post_init__(self):
        if self.send and self.session is None:
            self.session = Session()
        elif self.session is not None and not self.send:
            self.send = True

    def request(self, endpoint, method="GET", prepare=None, **kwargs):
        if prepare is None:
            prepare = self.prepare
        url = urlunsplit(
            (self.scheme, self.host, f"{self.base_path}{endpoint}", "", "")
        )
        request = Request(
            method=method,
            url=url,
            **kwargs,
        )
        if self.prepare or self.send:
            request = request.prepare()
        if self.send:
            response = self.session.send(request)
            response.raise_for_status()
            return response.json()
        else:
            return request

    def project(self, project):
        return self.request(f"/project/{project}")

    def _projects(self, project="", **params):
        return self.request(f"/projects/{project}", params=params)

    def projects(self, from_=None, to=None, **params):
        arguments = {
            "search": str,
            "maintainer": str,
            "category": str,
            "inrepo": str,
            "notinrepo": str,
            "repos": int,
            "families": int,
            "repos_newest": int,
            "families_newest": int,
            "newest": bool,
            "outdated": bool,
            "problematic": bool,
        }
        for argument, value in params.items():
            try:
                type = arguments[argument]
            except KeyError as err:
                raise TypeError(
                    f"{repr(argument)} is an invalid keyword argument for RepologyApi.projects()"
                ) from err
            if type == int and isinstance(value, (list, tuple)):
                start, end = value
                params[argument] = "-".join((str(x) if x else "") for x in [start, end])
            elif type == bool:
                params[argument] = int(bool(value))
        if from_ is not None and to is not None:
            ...  # TODO raise
        if from_ is not None:
            project = f"{from_}"
        elif to is not None:
            project = f"..{to}"
        else:
            project = ""
        return self._projects(project, **params)

    def problems(self, repository, maintainer=None):
        return self.request(
            f"/repository/{repository}/problems"
            if maintainer is None
            else f"/maintainer/{maintainer}/problems-for-repo/{repository}"
        )
