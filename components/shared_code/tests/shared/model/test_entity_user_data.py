"""Test the entity user data model."""

import unittest
from datetime import datetime, timedelta

from dateutil.tz import tzutc

from shared.model.entity_user_data import EntityUserData


class EntityUserDataTest(unittest.TestCase):
    """Test the entity user data model."""

    def setUp(self):
        """Set up date fixtures."""
        super().setUp()
        now = datetime.now(tz=tzutc())
        self.past = (now - timedelta(days=1)).isoformat()
        self.future = (now + timedelta(days=1)).isoformat()
        self.long_ago = (now - timedelta(days=30)).isoformat()

    def test_status(self):
        """Test that the status can be retrieved."""
        self.assertEqual("fixed", EntityUserData(status="fixed").status)

    def test_missing_status(self):
        """Test that the status is None if the user did not set a status."""
        self.assertIsNone(EntityUserData().status)

    def test_rationale(self):
        """Test that the rationale can be retrieved."""
        self.assertEqual("Not our code", EntityUserData(rationale="Not our code").rationale)

    def test_missing_rationale(self):
        """Test that the rationale is empty if the user did not give one."""
        self.assertEqual("", EntityUserData().rationale)

    def test_statuses_to_ignore(self):
        """Test that entities marked as fixed, false positive, or won't fix are ignored."""
        for status in EntityUserData.STATUSES_TO_IGNORE:
            with self.subTest(status=status):
                self.assertTrue(EntityUserData(status=status).is_ignored())

    def test_statuses_not_to_ignore(self):
        """Test that entities without status or marked as unconfirmed or confirmed are not ignored."""
        for status in (None, "unconfirmed", "confirmed"):
            with self.subTest(status=status):
                self.assertFalse(EntityUserData(status=status).is_ignored())

    def test_status_end_date_in_the_future(self):
        """Test that entities are ignored as long as the status end date has not passed."""
        self.assertTrue(EntityUserData(status="fixed", status_end_date=self.future).is_ignored())

    def test_status_end_date_in_the_past(self):
        """Test that entities are not ignored after the status end date has passed."""
        self.assertFalse(EntityUserData(status="fixed", status_end_date=self.past).is_ignored())

    def test_missing_status_end_date(self):
        """Test that entities are ignored if the user did not set a status end date."""
        self.assertTrue(EntityUserData(status="fixed").is_ignored())

    def test_empty_status_end_date(self):
        """Test that entities are ignored if the status end date is empty."""
        self.assertTrue(EntityUserData(status="fixed", status_end_date="").is_ignored())

    def test_excluded(self):
        """Test that excluded entities are ignored, whatever their status."""
        for status in (None, "unconfirmed", "confirmed", "fixed"):
            with self.subTest(status=status):
                self.assertTrue(EntityUserData(excluded=True, status=status).is_ignored())

    def test_not_excluded(self):
        """Test that entities that are not excluded are not ignored, whatever their status."""
        for status in (None, "unconfirmed", "confirmed", "fixed"):
            with self.subTest(status=status):
                self.assertFalse(EntityUserData(excluded=False, status=status).is_ignored())

    def test_exclusion_end_date_in_the_future(self):
        """Test that excluded entities are ignored as long as the exclusion end date has not passed."""
        entity_user_data = EntityUserData(excluded=True, exclusion_end_date=self.future)
        self.assertTrue(entity_user_data.is_ignored())

    def test_exclusion_end_date_in_the_past(self):
        """Test that excluded entities are not ignored after the exclusion end date has passed."""
        entity_user_data = EntityUserData(excluded=True, exclusion_end_date=self.past)
        self.assertFalse(entity_user_data.is_ignored())

    def test_exclusion_end_date_of_an_entity_that_is_not_excluded(self):
        """Test that the exclusion end date does not ignore entities that are not excluded."""
        entity_user_data = EntityUserData(excluded=False, exclusion_end_date=self.future)
        self.assertFalse(entity_user_data.is_ignored())

    def test_status_end_date_is_not_used_when_the_entity_has_exclusion_attributes(self):
        """Test that the status end date is ignored when the entity user data has been translated."""
        entity_user_data = EntityUserData(excluded=True, status="fixed", status_end_date=self.past)
        self.assertTrue(entity_user_data.is_ignored())

    def test_orphaned(self):
        """Test that entity user data is orphaned if it has an orphaned since date and time."""
        self.assertTrue(EntityUserData(orphaned_since=self.past).is_orphaned())

    def test_not_orphaned(self):
        """Test that entity user data is not orphaned if it has no orphaned since date and time."""
        self.assertFalse(EntityUserData().is_orphaned())

    def test_orphaned_too_long(self):
        """Test that entity user data that has been orphaned for over three weeks has been orphaned too long."""
        self.assertTrue(EntityUserData(orphaned_since=self.long_ago).orphaned_too_long())

    def test_not_orphaned_too_long(self):
        """Test that entity user data that has been orphaned recently has not been orphaned too long."""
        self.assertFalse(EntityUserData(orphaned_since=self.past).orphaned_too_long())

    def test_mark_orphaned(self):
        """Test that entity user data can be marked as orphaned."""
        entity_user_data = EntityUserData(status="fixed")
        entity_user_data.mark_orphaned()
        self.assertTrue(entity_user_data.is_orphaned())
        self.assertFalse(entity_user_data.orphaned_too_long())

    def test_mark_not_orphaned(self):
        """Test that entity user data can be marked as not orphaned."""
        entity_user_data = EntityUserData(status="fixed", orphaned_since=self.past)
        entity_user_data.mark_not_orphaned()
        self.assertFalse(entity_user_data.is_orphaned())
        self.assertEqual("fixed", entity_user_data.status)

    def test_mark_not_orphaned_when_not_orphaned(self):
        """Test that entity user data that is not orphaned can be marked as not orphaned."""
        entity_user_data = EntityUserData(status="fixed")
        entity_user_data.mark_not_orphaned()
        self.assertFalse(entity_user_data.is_orphaned())


class EntityUserDataTranslationTest(unittest.TestCase):
    """Test the translation of the status attributes into the exclusion attributes."""

    @staticmethod
    def translate(**attributes) -> EntityUserData:
        """Return the translated entity user data with the specified attributes."""
        entity_user_data = EntityUserData(**attributes)
        entity_user_data.translate_legacy_attributes()
        return entity_user_data

    def test_entity_user_data_without_status(self):
        """Test that entity user data without status is not excluded."""
        self.assertEqual({"excluded": False}, self.translate())

    def test_unconfirmed(self):
        """Test that an unconfirmed entity is not excluded and keeps its rationale."""
        expected = {"excluded": False, "status": "unconfirmed", "rationale": "Not our code"}
        self.assertEqual(expected, self.translate(status="unconfirmed", rationale="Not our code"))

    def test_confirmed(self):
        """Test that a confirmed entity is not excluded."""
        self.assertEqual({"excluded": False, "status": "confirmed"}, self.translate(status="confirmed"))

    def test_confirmed_with_status_end_date(self):
        """Test that the status end date of a confirmed entity is not translated, as it is not excluded."""
        entity_user_data = self.translate(status="confirmed", status_end_date="3000-01-01")
        self.assertFalse(entity_user_data["excluded"])
        self.assertNotIn("exclusion_end_date", entity_user_data)

    def test_excluding_statuses(self):
        """Test that entities with an ignored status are excluded, with the status end date as exclusion end date."""
        for status in EntityUserData.STATUSES_TO_IGNORE:
            with self.subTest(status=status):
                expected = {
                    "excluded": True,
                    "exclusion_end_date": "3000-01-01",
                    "status": status,
                    "status_end_date": "3000-01-01",
                }
                self.assertEqual(expected, self.translate(status=status, status_end_date="3000-01-01"))

    def test_excluded_without_status_end_date(self):
        """Test that an excluded entity without status end date does not get an exclusion end date."""
        entity_user_data = self.translate(status="fixed")
        self.assertTrue(entity_user_data["excluded"])
        self.assertNotIn("exclusion_end_date", entity_user_data)

    def test_rationale_is_not_translated(self):
        """Test that the rationale is passed through untouched, as the user interface still shows the status."""
        entity_user_data = self.translate(status="false_positive", rationale="Known bug in the linter")
        self.assertEqual("Known bug in the linter", entity_user_data["rationale"])

    def test_orphaned_since_is_not_translated(self):
        """Test that the orphaned since date and time is passed through untouched."""
        entity_user_data = self.translate(status="fixed", orphaned_since="2026-01-01T00:00:00+00:00")
        self.assertEqual("2026-01-01T00:00:00+00:00", entity_user_data["orphaned_since"])

    def test_translated_entity_user_data_is_not_translated_again(self):
        """Test that entity user data that has the exclusion attributes is left alone."""
        attributes = {"excluded": False, "rationale": "Not our code", "status": "fixed"}
        self.assertEqual(attributes, self.translate(**attributes))
