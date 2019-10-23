import React from 'react';
import ReactDOM from 'react-dom';
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import { shallow } from 'enzyme';
import { StringInput } from './StringInput';

Enzyme.configure({ adapter: new Adapter() });

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<StringInput />, div);
  ReactDOM.unmountComponentAtNode(div);
});

it('renders the value of the Input', () => {
  const wrapper = shallow(<StringInput value="Hello" />);
  expect(wrapper.find('Input').prop('value')).toBe("Hello");
});

it('renders the value of the StringInputWithSuggestions', () => {
  const wrapper = shallow(<StringInput value="Hello" options='x' />);
  expect(wrapper.find('StringInputWithSuggestions').prop('value')).toBe("Hello");
});

it('renders error prop to true when warning is set to true', () => {
  const wrapper = shallow(<StringInput warning={true}  options='x' />);
  expect(wrapper.find('StringInputWithSuggestions').dive().find('Form').find('FormDropdown').prop('error')).toBe(true);
});

it('renders error prop to true when the field is required and empty and the warning is undefined', () => {
  const wrapper = shallow(<StringInput required={true} value='' options='x' />);
  expect(wrapper.find('StringInputWithSuggestions').dive().find('Form').find('FormDropdown').prop('error')).toBe(true);
});

it('renders error prop to false when the field is required and not empty and the warning is undefined', () => {
  const wrapper = shallow(<StringInput required={true} value='x' options='x' />);
  expect(wrapper.find('StringInputWithSuggestions').dive().find('Form').find('FormDropdown').prop('error')).toBe(false);
});

it('renders error prop to true when the field is required and empty and the warning is false', () => {
  const wrapper = shallow(<StringInput required={true} warning={false} value='' options='x' />);
  expect(wrapper.find('StringInputWithSuggestions').dive().find('Form').find('FormDropdown').prop('error')).toBe(true);
});

it('renders error prop to false when the field is required and not empty and the warning is false', () => {
  const wrapper = shallow(<StringInput required={true} warning={false} value='x' options='x' />);
  expect(wrapper.find('StringInputWithSuggestions').dive().find('Form').find('FormDropdown').prop('error')).toBe(false);
});