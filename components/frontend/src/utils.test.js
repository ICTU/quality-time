import { nice_number, scaled_number, show_message } from './utils';
import * as react_semantic_toast from 'react-semantic-toasts';

jest.mock("react-semantic-toasts");

it('shows a message', () => {
  react_semantic_toast.toast = jest.fn();
  show_message("error", "Error", "Description");
  expect(react_semantic_toast.toast.mock.calls[0][0].type).toBe("error");
});

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
