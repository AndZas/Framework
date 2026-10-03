import unittest
from pathlib import Path
from theme import Theme, CUSTOM, DEFAULTS, parse, resolve


class ThemeChecks(unittest.TestCase):
    def test_equivalent_sources(self):
        css = Theme.load(Path(__file__).with_name('lagoon.theme'))
        self.assertEqual(css.tokens, CUSTOM.tokens)
        self.assertEqual(resolve(css), resolve(CUSTOM))

    def test_precedence_and_partial_fallback(self):
        theme = Theme('partial', accent='#123456', opacity=0.5)
        style = resolve(theme, {'accent': '#abcdef'})
        self.assertEqual(style['accent'], '#abcdef')
        self.assertEqual(style['opacity'], 0.5)
        self.assertEqual(style['radius'], DEFAULTS['radius'])
        self.assertEqual(resolve(Theme('empty')), DEFAULTS)

    def test_invalid_syntax_reports_source(self):
        for text in ['Button { accent: #123456; }', ':theme { radius: 2px; }',
                     ':theme { opacity: 2; }', ':theme { background: red; }',
                     ':theme { alien: 3; }', ':theme { radius: 4; radius: 5; }',
                     ':theme { radius: 4 }', ':theme { gradient: linear-gradient(red, blue); }',
                     ':theme {} :theme {}', ':theme { /* comment */ radius: 4; }',
                     ':theme { radius: -1; }', ':theme { accent: #fff; }',
                     ':theme { gradient: linear-gradient(90deg, #123456, #654321); }']:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'broken.theme'):
                parse(text, 'broken.theme')

    def test_python_validation(self):
        for tokens in [dict(opacity=float('nan')), dict(radius=True), dict(radius=49),
                       dict(gradient=['#123456']), dict(gradient=['#123456', 'red']),
                       dict(opacity='0.5'), dict(radius=-1), dict(unknown=1)]:
            with self.subTest(tokens=tokens), self.assertRaises(ValueError):
                Theme('bad Python', **tokens)

    def test_normalization_and_defensive_copy(self):
        theme = parse(':theme { accent: #ABCDEF; radius: 0; opacity: 0; }')
        self.assertEqual(theme.tokens['accent'], '#abcdef')
        tokens = theme.tokens
        tokens['radius'] = 99
        self.assertEqual(theme.tokens['radius'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
