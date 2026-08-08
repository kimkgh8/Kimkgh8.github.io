from pathlib import Path
from html.parser import HTMLParser
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]

PUBLIC_HTML = [
    ROOT / "index.html",
    ROOT / "apps" / "babyspace" / "index.html",
    ROOT / "apps" / "credit-card-tracker" / "index.html",
    ROOT / "privacy" / "index.html",
    ROOT / "privacy" / "babyspace" / "index.html",
    ROOT / "privacy" / "credit-card-tracker" / "index.html",
    ROOT / "support" / "index.html",
    ROOT / "404.html",
]


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href"):
            self.references.append(attributes["href"])
        if tag in {"img", "link"}:
            reference = attributes.get("src") or attributes.get("href")
            if reference:
                self.references.append(reference)


class SiteStructureTests(unittest.TestCase):
    def test_required_public_files_exist(self):
        required = PUBLIC_HTML + [
            ROOT / ".nojekyll",
            ROOT / "assets" / "css" / "site.css",
            ROOT / "app-ads.txt",
            ROOT / "googlef14fa7669762aee6.html",
            ROOT / "robots.txt",
            ROOT / "sitemap.xml",
        ]
        missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
        self.assertEqual([], missing)

    def test_legacy_portfolio_entry_files_are_removed(self):
        legacy = [
            "about.md",
            "blog.html",
            "projects.html",
            "tags.html",
            "_config.yml",
            "_config-dev.yml",
        ]
        remaining = [path for path in legacy if (ROOT / path).exists()]
        self.assertEqual([], remaining)

    def test_app_ads_content_is_unchanged(self):
        content = (ROOT / "app-ads.txt").read_text(encoding="utf-8").strip()
        self.assertEqual(
            "google.com, pub-2517817899244192, DIRECT, f08c47fec0942fa0",
            content,
        )


class PublicContentTests(unittest.TestCase):
    def setUp(self):
        self.pages = {
            path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
            for path in PUBLIC_HTML
            if path.exists()
        }

    def test_pages_use_korean_semantic_shell(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                self.assertIn('<html lang="ko">', html)
                self.assertIn('name="viewport"', html)
                self.assertIn('class="skip-link"', html)
                self.assertRegex(html, r"<main\b")
                self.assertIn("site-footer", html)

    def test_personal_portfolio_information_is_not_public(self):
        combined = "\n".join(self.pages.values())
        forbidden = [
            "Kim Geunho",
            "김근호",
            "Dream is My life",
            "profile.jpg",
            "Résumé",
            "Skills",
            "신용카드 결제 서비스",
        ]
        found = [term for term in forbidden if term in combined]
        self.assertEqual([], found)

    def test_google_play_apps_are_linked_with_exact_packages(self):
        homepage = self.pages.get("index.html", "")
        self.assertIn("공동 육아 기록 · 베이비스페이스", homepage)
        self.assertIn("실적메이트", homepage)
        self.assertIn(
            "https://play.google.com/store/apps/details?id=com.babyspace",
            homepage,
        )
        self.assertIn(
            "https://play.google.com/store/apps/details?id=com.creditcardtracker.credit_card_tracker",
            homepage,
        )
        self.assertGreaterEqual(homepage.count("play-lh.googleusercontent.com"), 2)

    def test_privacy_pages_cover_google_play_basics(self):
        expected = {
            "privacy/babyspace/index.html": [
                "베이비스페이스",
                "Firebase",
                "Google AdMob",
                "보유",
                "삭제",
                "문의",
            ],
            "privacy/credit-card-tracker/index.html": [
                "실적메이트",
                "기기 내",
                "수집하지 않습니다",
                "보유",
                "삭제",
                "문의",
            ],
        }
        for page, terms in expected.items():
            html = self.pages.get(page, "")
            with self.subTest(page=page):
                missing = [term for term in terms if term not in html]
                self.assertEqual([], missing)

    def test_external_blank_links_are_safe(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                unsafe = re.findall(
                    r'<a\b(?=[^>]*target="_blank")(?![^>]*rel="[^"]*noopener)[^>]*>',
                    html,
                    flags=re.IGNORECASE,
                )
                self.assertEqual([], unsafe)

    def test_internal_links_resolve_to_public_files(self):
        broken = []
        for page_name, html in self.pages.items():
            collector = LinkCollector()
            collector.feed(html)
            for reference in collector.references:
                if not reference.startswith("/") or reference.startswith("//"):
                    continue
                path_text = reference.split("#", 1)[0].split("?", 1)[0]
                if not path_text:
                    path_text = "/"
                candidate = ROOT / path_text.lstrip("/")
                if path_text.endswith("/"):
                    candidate = candidate / "index.html"
                if not candidate.exists():
                    broken.append(f"{page_name}: {reference}")
        self.assertEqual([], broken)

    def test_visible_copy_has_no_em_or_en_dash(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                self.assertNotIn("—", html)
                self.assertNotIn("–", html)


class StylesheetTests(unittest.TestCase):
    def test_responsive_accessible_theme_rules_exist(self):
        css_path = ROOT / "assets" / "css" / "site.css"
        css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        self.assertIn("prefers-color-scheme: dark", css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertRegex(css, r"@media\s*\([^)]*max-width:\s*760px")
        self.assertIn(":focus-visible", css)
        self.assertIn("min-height: 100dvh", css)


if __name__ == "__main__":
    unittest.main()
