"""Scholarly regression fixtures from the IFAO Papyrus Prisse project.

Source: https://prisse.ifao.egnet.net/verse
The selected short transliteration samples exercise real editorial punctuation,
Unicode transliteration characters, and historical aleph/ayin forms.
"""

import unittest

from egypttranslit import normalize_unicode, parse


class ScholarlyFixtureTests(unittest.TestCase):
    def test_ifao_prisse_samples_are_stable_while_canonical_mode_is_available(self):
        fixtures = [
            (
                "ḫr ḥm n(y) n(y)-sw.t bjt(y) Jssj ʿnḫ(=w) ḏ.t r nḥḥ",
                "ḫr ḥm n(y) n(y)-sw.t bjt(y) Jssj ꜥnḫ(=w) ḏ.t r nḥḥ",
            ),
            (
                "jr ḥms(w)=k ḥnʿ ʿšȝ.t msd t mrr(w)=k",
                "jr ḥms(w)=k ḥnꜥ ꜥšꜣ.t msd t mrr(w)=k",
            ),
            (
                "ȝ.t pw kt.t dȝ{jr}<rj> jb",
                "ꜣ.t pw kt.t dꜣ{jr}<rj> jb",
            ),
            (
                "wstn ẖ.t m pr=sn",
                "wstn ẖ.t m pr=sn",
            ),
        ]

        for source, canonical in fixtures:
            with self.subTest(source=source):
                self.assertEqual(normalize_unicode(source), canonical)
                self.assertEqual(parse(source), source)

    def test_real_unicode_samples_remain_idempotent(self):
        samples = [
            "ḫr ḥm n(y) n(y)-sw.t bjt(y) Jssj ʿnḫ(=w) ḏ.t r nḥḥ",
            "jr ḥms(w)=k ḥnʿ ʿšȝ.t msd t mrr(w)=k",
            "ȝ.t pw kt.t dȝ{jr}<rj> jb",
            "wstn ẖ.t m pr=sn",
        ]

        for source in samples:
            with self.subTest(source=source):
                once = parse(source)
                self.assertEqual(parse(once), once)


if __name__ == "__main__":
    unittest.main()
