import unittest
from repology_api import RepologyApi
from functools import cache
import operator


class TestRepologyApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        self.api = RepologyApi(send=True)
        super().__init__(*args, **kwargs)

    def test_project(self):
        packages = self.api.project("firefox")
        package = [package for package in packages if package["repo"] == "freebsd"][0]
        correct_package = {
            "repo": "freebsd",
            "srcname": "www/firefox",
            "binname": "firefox",
            "visiblename": "www/firefox",
            # "version": "50.1.0",
            # "origversion": "50.1.0_4,1",
            "status": "newest",
            # "summary": "Widely used web browser",
            "categories": ["www"],
            # "licenses": ["GPLv2+"],
            # "maintainers": ["gecko@FreeBSD.org"],
        }
        self.assertEqual(package, package | correct_package)

    @cache
    def firefox_package_info(self):
        return self.api.project("firefox")

    def _test_projects(self, param, func):
        projects = self.api.projects(**{param: "firefox"})
        self.assertEqual(len(projects), 200)
        self.assertEqual(
            [
                project
                for project_name, project in projects.items()
                if project_name == "firefox"
            ],
            [self.firefox_package_info()],
        )
        self.assertTrue(
            all(func(project_name, "firefox") for project_name in projects.keys())
        )

    def test_projects(self):
        projects = self.api.projects()
        self.assertEqual(len(projects), 200)

    def test_projects_from(self):
        self._test_projects("from_", operator.__ge__)

    def test_projects_to(self):
        self._test_projects("to", operator.__le__)

    def test_problems(self):
        self.api.problems("freebsd")

    def test_problems_with_maintainer(self):
        self.api.problems("freebsd", "ports@freebsd.org")


unittest.main()
