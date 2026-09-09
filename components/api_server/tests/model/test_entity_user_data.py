"""Unit tests for the entity user data model."""

import unittest
from datetime import date, timedelta

from shared.utils.date_time import now

from model.entity_user_data import EntityUserData
from model.report import Report


class SetAttributeTest(unittest.TestCase):
    """Unit tests for setting an entity attribute."""

    ENTITY_DESCRIPTION = "entity title/foo"

    def setUp(self):
        """Override to set up the report under test."""
        self.report = Report({}, {"title": "Report"})

    def set_attribute(self, entity_user_data: EntityUserData, attribute: str, value: str) -> str:
        """Set the attribute and return the description of the change."""
        return entity_user_data.set_attribute(attribute, value, self.ENTITY_DESCRIPTION, self.report)

    def expected_user_entity_data(self, deadline: date) -> dict[str, bool | str]:
        """Return an expected user entity data dict."""
        return {
            "excluded": True,
            "exclusion_end_date": str(deadline),
            "status": "false_positive",
            "status_end_date": str(deadline),
        }

    def test_set_attribute(self):
        """Test that the attribute is set and the change described."""
        entity_user_data = EntityUserData()
        description = self.set_attribute(entity_user_data, "rationale", "Not our code")
        self.assertEqual({"excluded": False, "rationale": "Not our code"}, entity_user_data)
        self.assertEqual(f"changed the rationale of '{self.ENTITY_DESCRIPTION}' from '' to 'Not our code'", description)

    def test_change_attribute(self):
        """Test that the old value of the attribute is part of the description."""
        entity_user_data = EntityUserData(rationale="Not our code")
        description = self.set_attribute(entity_user_data, "rationale", "Third party code")
        self.assertEqual({"excluded": False, "rationale": "Third party code"}, entity_user_data)
        expected = f"changed the rationale of '{self.ENTITY_DESCRIPTION}' from 'Not our code' to 'Third party code'"
        self.assertEqual(expected, description)

    def test_set_rationale_sanitizes_html(self):
        """Test that dangerous HTML is removed from the rationale, because the frontend renders it as HTML."""
        entity_user_data = EntityUserData()
        description = self.set_attribute(entity_user_data, "rationale", '<img src="x" onerror="alert(1)">Why not')
        self.assertEqual({"excluded": False, "rationale": '<img src="x">Why not'}, entity_user_data)
        self.assertIn("to '<img src=\"x\">Why not'", description)

    def test_set_empty_rationale(self):
        """Test that an empty rationale is not sanitized, because sanitizing empty HTML throws an error."""
        entity_user_data = EntityUserData(rationale="Not our code")
        self.set_attribute(entity_user_data, "rationale", "")
        self.assertEqual({"excluded": False, "rationale": ""}, entity_user_data)

    def test_set_status_derives_the_status_end_date(self):
        """Test that setting the status also sets the status end date, and describes both changes."""
        deadline = (now() + timedelta(days=180)).date()
        entity_user_data = EntityUserData()
        description = self.set_attribute(entity_user_data, "status", "false_positive")
        self.assertEqual(self.expected_user_entity_data(deadline), entity_user_data)
        self.assertEqual(
            f"changed the status of '{self.ENTITY_DESCRIPTION}' from '' to 'false_positive' "
            f"and changed the status end date from 'None' to '{deadline}'",
            description,
        )

    def test_set_status_uses_the_desired_response_times_of_the_report(self):
        """Test that the status end date is derived from the desired response times of the report."""
        deadline = (now() + timedelta(days=10)).date()
        self.report["desired_response_times"] = {"false_positive": 10}
        entity_user_data = EntityUserData()
        self.set_attribute(entity_user_data, "status", "false_positive")
        self.assertEqual(str(deadline), entity_user_data["status_end_date"])

    def test_set_status_does_not_change_an_unchanged_status_end_date(self):
        """Test that the status end date is not described as changed if it does not change."""
        deadline = (now() + timedelta(days=10)).date()
        self.report["desired_response_times"] = {"false_positive": 10}
        entity_user_data = EntityUserData(status_end_date=str(deadline))
        description = self.set_attribute(entity_user_data, "status", "false_positive")
        self.assertEqual(self.expected_user_entity_data(deadline), entity_user_data)
        self.assertEqual(f"changed the status of '{self.ENTITY_DESCRIPTION}' from '' to 'false_positive'", description)

    def test_set_status_without_desired_response_time(self):
        """Test that no status end date is set if the status has no desired response time."""
        entity_user_data = EntityUserData()
        description = self.set_attribute(entity_user_data, "status", "unconfirmed")
        self.assertEqual({"excluded": False, "status": "unconfirmed"}, entity_user_data)
        self.assertEqual(f"changed the status of '{self.ENTITY_DESCRIPTION}' from '' to 'unconfirmed'", description)

    def test_set_status_with_desired_response_time_turned_off(self):
        """Test that no status end date is set if the desired response time of the status has been turned off."""
        self.report["desired_response_times"] = {"false_positive": None}
        entity_user_data = EntityUserData()
        self.set_attribute(entity_user_data, "status", "false_positive")
        self.assertEqual({"excluded": True, "status": "false_positive"}, entity_user_data)

    def test_statuses_that_exclude_the_entity(self):
        """Test that the statuses that ignore the entity set the excluded attribute to true."""
        for status in EntityUserData.STATUSES_TO_IGNORE:
            with self.subTest(status=status):
                entity_user_data = EntityUserData()
                self.set_attribute(entity_user_data, "status", status)
                self.assertTrue(entity_user_data["excluded"])

    def test_statuses_that_do_not_exclude_the_entity(self):
        """Test that the statuses that do not ignore the entity set the excluded attribute to false."""
        for status in ("unconfirmed", "confirmed"):
            with self.subTest(status=status):
                entity_user_data = EntityUserData()
                self.set_attribute(entity_user_data, "status", status)
                self.assertFalse(entity_user_data["excluded"])

    def test_including_an_entity_removes_the_exclusion_end_date(self):
        """Test that changing the status to a status that does not exclude removes the exclusion end date."""
        entity_user_data = EntityUserData(status="fixed", status_end_date="3000-01-01")
        self.set_attribute(entity_user_data, "status", "unconfirmed")
        self.assertFalse(entity_user_data["excluded"])
        self.assertNotIn("exclusion_end_date", entity_user_data)

    def test_set_status_end_date_of_an_excluded_entity(self):
        """Test that the exclusion end date follows the status end date of an excluded entity."""
        entity_user_data = EntityUserData(excluded=True, exclusion_end_date="2000-01-01", status="fixed")
        self.set_attribute(entity_user_data, "status_end_date", "3000-01-01")
        self.assertEqual("3000-01-01", entity_user_data["exclusion_end_date"])

    def test_set_status_end_date_of_an_included_entity(self):
        """Test that an entity that is not excluded does not get an exclusion end date."""
        entity_user_data = EntityUserData(status="confirmed")
        self.set_attribute(entity_user_data, "status_end_date", "3000-01-01")
        self.assertNotIn("exclusion_end_date", entity_user_data)

    def test_set_rationale_does_not_change_the_exclusion(self):
        """Test that setting the rationale keeps the exclusion attributes of an excluded entity."""
        entity_user_data = EntityUserData(status="wont_fix", status_end_date="3000-01-01")
        self.set_attribute(entity_user_data, "rationale", "Not our code")
        self.assertTrue(entity_user_data["excluded"])
        self.assertEqual("3000-01-01", entity_user_data["exclusion_end_date"])

    def test_the_exclusion_attributes_are_not_described(self):
        """Test that the changelog does not describe the exclusion attributes, as the user did not change them."""
        entity_user_data = EntityUserData()
        description = self.set_attribute(entity_user_data, "status", "wont_fix")
        self.assertNotIn("exclu", description)

    def test_set_status_end_date_does_not_derive_attributes(self):
        """Test that setting the status end date does not change the status."""
        entity_user_data = EntityUserData(status="false_positive")
        description = self.set_attribute(entity_user_data, "status_end_date", "3000-01-01")
        self.assertEqual(self.expected_user_entity_data(date(3000, 1, 1)), entity_user_data)
        expected = f"changed the status_end_date of '{self.ENTITY_DESCRIPTION}' from '' to '3000-01-01'"
        self.assertEqual(expected, description)
