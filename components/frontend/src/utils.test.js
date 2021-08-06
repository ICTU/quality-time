import { getUserPermissions, get_metric_tags, get_metric_target, get_source_name, get_subject_name, nice_number, scaled_number, show_message, format_minutes } from './utils';
import { EDIT_REPORT_PERMISSION, EDIT_ENTITY_PERMISSION } from './context/Permissions';

it('rounds numbers nicely', () => {
  expect(nice_number(15)).toBe(20);
  expect(nice_number(16)).toBe(20);
  expect(nice_number(17)).toBe(50);
  expect(nice_number(39)).toBe(50);
  expect(nice_number(40)).toBe(50);
  expect(nice_number(41)).toBe(100);
  expect(nice_number(79)).toBe(100);
  expect(nice_number(80)).toBe(100);
  expect(nice_number(81)).toBe(200);
});

it('adds a scale', () => {
  expect(scaled_number(1)).toBe("1");
  expect(scaled_number(12)).toBe("12");
  expect(scaled_number(123)).toBe("123");
  expect(scaled_number(1234)).toBe("1k");
  expect(scaled_number(12345)).toBe("12k");
  expect(scaled_number(123456)).toBe("123k");
  expect(scaled_number(1234567)).toBe("1m");
  expect(scaled_number(12345678)).toBe("12m");
  expect(scaled_number(123456789)).toBe("123m");
});

it('formats minutes', () => {
  expect(format_minutes(0)).toBe("0:00");
  expect(format_minutes(1)).toBe("0:01");
  expect(format_minutes(10)).toBe("0:10");
  expect(format_minutes(59)).toBe("0:59");
  expect(format_minutes(60)).toBe("1:00");
  expect(format_minutes(61)).toBe("1:01");
  expect(format_minutes(600)).toBe("10:00");
});

it('gives users all permissions if permissions have not been limited', () => {
  const permissions = getUserPermissions("jodoe", "john.doe@example.org", false, null, {});
  expect(permissions).toStrictEqual([EDIT_REPORT_PERMISSION, EDIT_ENTITY_PERMISSION]);
});

it('gives users edit report permissions if edit report permissions have been granted', () => {
  const permissions = getUserPermissions("jodoe", "john.doe@example.org", false, null, {[EDIT_REPORT_PERMISSION]: ["jodoe"], [EDIT_ENTITY_PERMISSION]: ["jadoe"]});
  expect(permissions).toStrictEqual([EDIT_REPORT_PERMISSION]);
});

it('gives users edit entity permissions if edit entity permissions have been granted', () => {
  const permissions = getUserPermissions("jodoe", "john.doe@example.org", false, null, {[EDIT_REPORT_PERMISSION]: ["jadoe"], [EDIT_ENTITY_PERMISSION]: ["jodoe"]});
  expect(permissions).toStrictEqual([EDIT_ENTITY_PERMISSION]);
});

it('gives users no permissions if they have not logged in', () => {
  const permissions = getUserPermissions(null, null, false, null, {});
  expect(permissions).toStrictEqual([]);
});

it('gives users no permissions if the report date is in the past', () => {
  const permissions = getUserPermissions("jodoe", "john.doe@example.org", false, new Date(), {});
  expect(permissions).toStrictEqual([]);
});

it('gives users no permissions if the report is a tag report', () => {
  const permissions = getUserPermissions("jodoe", "john.doe@example.org", true, null, {});
  expect(permissions).toStrictEqual([]);
});

it('gets the metric tags sorted', () => {
  expect(get_metric_tags({tags: ["foo", "bar"]})).toStrictEqual(["bar", "foo"]);
});

it('gets the metric tags even if there are none', () => {
  expect(get_metric_tags({})).toStrictEqual([]);
});

it('gets the metric target, even if the target is missing', () => {
  expect(get_metric_target({})).toStrictEqual("0");
});

it('gets the metric debt target, if technical debt has been accepted', () => {
  expect(get_metric_target({accept_debt: true, debt_target: "1"})).toStrictEqual("1");
});

it('gets the metric target, if technical debt has not been accepted', () => {
  expect(get_metric_target({accept_debt: false, target: "2"})).toStrictEqual("2");
});

it('gets the source name', () => {
  expect(get_source_name({name: "source"}, {})).toStrictEqual("source")
});

it('gets the source name from the data model if the source has no name', () => {
  expect(get_source_name({type: "source_type"}, {sources: {"source_type": {name: "source"}}})).toStrictEqual("source")
});

it('gets the subject name', () => {
  expect(get_subject_name({name: "subject"}, {})).toStrictEqual("subject")
});

it('gets the subject name from the data model if the subject has no name', () => {
  expect(get_subject_name({type: "subject_type"}, {subjects: {"subject_type": {name: "subject"}}})).toStrictEqual("subject")
});
