import unittest
from nsaph_utils.utils.context import Context, Argument, Cardinality

class MadeUpContext(Context):
    _thing = Argument("thing",
                     help = "a thing",
                     default = "45")

    def __init__(self):
        super().__init__(MadeUpContext)

    def validate(self, attr, value):
        value = super().validate(attr, value)

        if attr == "thing":
            value = "thing"

        return value




class MyTestCase(unittest.TestCase):

    def test_default_context(self):
        context = Context(Context).instantiate()
        self.assertEqual(context.years, list(range(1990, 2021)))

    def test_custom_validate(self):
        context = MadeUpContext().instantiate()

        self.assertEqual(context.thing, "thing")


if __name__ == '__main__':
    unittest.main()
