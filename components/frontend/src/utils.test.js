import { show_message } from './utils';
import * as react_semantic_toast from 'react-semantic-toasts';

jest.mock("react-semantic-toasts");

it('shows a message', () => {
  react_semantic_toast.toast = jest.fn();
  show_message("error", "Error", "Description");
  expect(react_semantic_toast.toast.mock.calls[0][0].type).toBe("error");
});
