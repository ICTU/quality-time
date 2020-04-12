import { nice_number, show_message } from './utils';
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
