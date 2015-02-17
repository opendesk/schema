import unittest
from decimal import Decimal

from winnow.values import value_factory
from winnow.values.numeric_values import NumericNumberSieveValue, \
    NumericSetSieveValue, \
    NumericRangeSieveValue, \
    NumericStepSieveValue
from winnow.constants import *

from winnow.exceptions import OptionsExceptionFailedValidation, OptionsExceptionIncompatibleTypes



class TestNumberSieveCreation(unittest.TestCase):

    def test_convienence_methods_single_values(self):

        number = value_factory(2)
        value = number.as_json()

        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal(2))

        number = value_factory(2.5)
        value = number.as_json()

        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal(2.5))

        number = value_factory(Decimal(2.5))
        value = number.as_json()

        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal(2.5))


    def test_convienence_methods_lists(self):

        number = value_factory([2])
        value = number.as_json()

        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal("2"))

        number = value_factory([2, 3.8])
        value = number.as_json()

        self.assertTrue(isinstance(number, NumericSetSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_SET)
        self.assertTrue(isinstance(value[u"value"], list))
        self.assertEqual(value[u"value"], [Decimal("2"), Decimal(3.8)])

        number = value_factory([2, 3.8, "5"])
        value = number.as_json()

        self.assertTrue(isinstance(number, NumericSetSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_SET)
        self.assertTrue(isinstance(value[u"value"], list))
        self.assertEqual(value[u"value"], [Decimal("2"), Decimal(3.8), Decimal("5")])

        self.assertRaises(OptionsExceptionFailedValidation, value_factory, [2, 3.8, "poo"])


    #     TODO think about nan


    def test_create_numbers(self):

        number = value_factory({
            "type": VALUE_TYPE_NUMERIC_NUMBER,
            "value": Decimal(2)
        })

        value = number.as_json()

        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal(2))


    def test_create_set(self):

        number = value_factory({
            "type": VALUE_TYPE_NUMERIC_SET,
            "value": [Decimal("2"), Decimal("17.4")]
        })

        value = number.as_json()

        self.assertTrue(isinstance(number, NumericSetSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_SET)
        self.assertTrue(isinstance(value[u"value"], list))
        self.assertEqual(value[u"value"],  [Decimal("2"), Decimal("17.4")])

        # casts down
        number = value_factory({
            "type": VALUE_TYPE_NUMERIC_SET,
            "value": [Decimal("2")]
        })

        value = number.as_json()

        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal("2"))


    def test_create_range(self):

        number = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("21.5"),
            "min": Decimal("13.4"),
        })

        value = number.as_json()
        self.assertTrue(isinstance(number, NumericRangeSieveValue))

        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_RANGE)
        self.assertTrue(isinstance(value[u"max"], Decimal))
        self.assertTrue(isinstance(value[u"min"], Decimal))
        self.assertEqual(value[u"max"],  Decimal("21.5"))
        self.assertEqual(value[u"min"],  Decimal("13.4"))


    def test_create_step(self):

        number = value_factory({
            "type": VALUE_TYPE_NUMERIC_STEP,
            "max": Decimal("21.5"),
            "min": Decimal("13.4"),
            "start": Decimal("13.4"),
            "step": Decimal("3.0"),
        })

        value = number.as_json()
        self.assertTrue(isinstance(number, NumericStepSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_STEP)
        self.assertTrue(isinstance(value[u"max"], Decimal))
        self.assertTrue(isinstance(value[u"min"], Decimal))
        self.assertEqual(value[u"max"],  Decimal("21.5"))
        self.assertEqual(value[u"min"],  Decimal("13.4"))
        self.assertEqual(number.possible_values(), {Decimal("13.4"), Decimal("16.4"), Decimal("19.4")})

        # casts down
        number = value_factory({
            "type": VALUE_TYPE_NUMERIC_STEP,
            "max": Decimal("21.5"),
            "min": Decimal("13.4"),
            "start": Decimal("13.4"),
            "step": Decimal("10.0"),
        })

        value = number.as_json()
        self.assertTrue(isinstance(number, NumericNumberSieveValue))
        self.assertEqual(value[u"type"], VALUE_TYPE_NUMERIC_NUMBER)
        self.assertTrue(isinstance(value[u"value"], Decimal))
        self.assertEqual(value[u"value"], Decimal("13.4"))



    def test_is_subset(self):

        number1 = value_factory(2)
        number2 = value_factory(2)

        self.assertTrue(number1.issubset(number2))

        number3 = value_factory([2, 4])

        self.assertTrue(number1.issubset(number3))
        self.assertFalse(number3.issubset(number1))

        number4 = value_factory([4, 8])
        number5 = value_factory([4, 8])

        self.assertFalse(number3.issubset(number4))
        self.assertFalse(number4.issubset(number3))
        self.assertTrue(number4.issubset(number5))

        number6 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("8"),
            "min": Decimal("4"),
        })

        number7 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("10"),
            "min": Decimal("2"),
        })

        number8 = value_factory(7)

        self.assertTrue(number4.issubset(number6))
        self.assertTrue(number6.issubset(number4))

        self.assertTrue(number4.issubset(number7))
        self.assertFalse(number7.issubset(number4))

        self.assertTrue(number8.issubset(number7))
        self.assertFalse(number7.issubset(number8))

        number9 = value_factory({
            "type": VALUE_TYPE_NUMERIC_STEP,
            "max": Decimal("9"),
            "min": Decimal("2"),
            "start": Decimal("2"),
            "step": Decimal("3"),
        })

        self.assertTrue(number1.issubset(number9))
        self.assertFalse(number3.issubset(number9))

        self.assertTrue(number9.issubset(number7))
        self.assertFalse(number7.issubset(number9))


    def test_intersection(self):

        number1 = value_factory(2)
        number2 = value_factory(2)
        number3 = value_factory([2, 4])
        number4 = value_factory([4, 8])
        number5 = value_factory([4, 8])

        number6 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("8"),
            "min": Decimal("4"),
        })

        number7 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("10"),
            "min": Decimal("2"),
        })

        number8 = value_factory(7)

        number9 = value_factory({
            "type": VALUE_TYPE_NUMERIC_STEP,
            "max": Decimal("9"),
            "min": Decimal("2"),
            "start": Decimal("2"),
            "step": Decimal("3"),
        })

        number10 = number1.intersection(number3)

        self.assertTrue(isinstance(number10, NumericNumberSieveValue))
        self.assertEqual(number10.as_json()[u"value"], Decimal(2))

        number11 = number4.intersection(number3)
        number12 = value_factory([4, 8, 10])

        self.assertTrue(isinstance(number11, NumericNumberSieveValue))
        self.assertEqual(number11.as_json()[u"value"], Decimal(4))

        number13 = number12.intersection(number5)

        self.assertTrue(isinstance(number13, NumericSetSieveValue))
        self.assertEqual(set(number13.as_json()[u"value"]), {Decimal("4"), Decimal("8")})

        number14 = number12.intersection(number6)

        self.assertTrue(isinstance(number14, NumericSetSieveValue))
        self.assertEqual(set(number14.as_json()[u"value"]), {Decimal("4"), Decimal("8")})

        number15 = number6.intersection(number12)

        self.assertTrue(isinstance(number15, NumericSetSieveValue))
        self.assertEqual(set(number15.as_json()[u"value"]), {Decimal("4"), Decimal("8")})

        number16 = number7.intersection(number9)

        self.assertTrue(isinstance(number16, NumericStepSieveValue))
        self.assertEqual(number16.possible_values(), {Decimal("2"), Decimal("5"), Decimal("8")})

        number17 = number9.intersection(number7)

        self.assertTrue(isinstance(number17, NumericStepSieveValue))
        self.assertEqual(number17.possible_values(), {Decimal("2"), Decimal("5"), Decimal("8")})

        number18 = value_factory({
            "type": VALUE_TYPE_NUMERIC_STEP,
            "max": Decimal("12"),
            "min": Decimal("6"),
            "start": Decimal("2"),
            "step": Decimal("2"),
        })

        number20 = value_factory({
            "type": VALUE_TYPE_NUMERIC_STEP,
            "max": Decimal("12"),
            "min": Decimal("0"),
            "start": Decimal("0"),
            "step": Decimal("2"),
        })

        number19 = number9.intersection(number18)

        self.assertTrue(isinstance(number19, NumericNumberSieveValue))
        self.assertEqual(number19.as_json()[u"value"], Decimal("8"))

        number21 = number20.intersection(number18)

        self.assertTrue(isinstance(number21, NumericSetSieveValue))
        self.assertEqual(set(number21.as_json()[u"value"]), {Decimal("6"), Decimal("8"), Decimal("10"), Decimal("12")})


    def test_isdisjoint(self):

        number1 = value_factory(2)
        number2 = value_factory(2)
        number3 = value_factory([2, 4])
        number4 = value_factory([4, 8])

        self.assertFalse(number1.isdisjoint(number2))
        self.assertFalse(number1.isdisjoint(number3))
        self.assertTrue(number1.isdisjoint(number4))


        number6 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("8"),
            "min": Decimal("4"),
        })

        number7 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("10"),
            "min": Decimal("2"),
        })

        number8 = value_factory({
            "type": VALUE_TYPE_NUMERIC_RANGE,
            "max": Decimal("10"),
            "min": Decimal("9"),
        })

        self.assertTrue(number6.isdisjoint(number8))