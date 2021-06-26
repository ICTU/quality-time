import React from 'react';
import ReactDOM from 'react-dom';
import { mount, shallow } from 'enzyme';
import { Permissions } from '../context/Permissions';
import { StringInput } from './StringInput';

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
  const wrapper = mount(<Permissions.Provider value={false}><StringInput value="Hello" options='x' /></Permissions.Provider>);
  expect(wrapper.find('StringInputWithSuggestions').prop('value')).toBe("Hello");
});

it('renders error prop to true when warning is set to true', () => {
  const wrapper = mount(<Permissions.Provider value={false}><StringInput warning={true}  options='x' /></Permissions.Provider>);
  expect(wrapper.find('FormDropdown').prop('error')).toBe(true);
});

it('renders error prop to true when the field is required and empty and the warning is undefined', () => {
  const wrapper = mount(<Permissions.Provider value={false}><StringInput required={true} value='' options='x' /></Permissions.Provider>);
  expect(wrapper.find('FormDropdown').prop('error')).toBe(true);
});

it('renders error prop to false when the field is required and not empty and the warning is undefined', () => {
  const wrapper = mount(<Permissions.Provider value={false}><StringInput required={true} value='x' options='x' /></Permissions.Provider>);
  expect(wrapper.find('FormDropdown').prop('error')).toBe(false);
});

it('renders error prop to true when the field is required and empty and the warning is false', () => {
  const wrapper = mount(<Permissions.Provider value={false}><StringInput required={true} warning={false} value='' options='x' /></Permissions.Provider>);
  expect(wrapper.find('FormDropdown').prop('error')).toBe(true);
});

it('renders error prop to false when the field is required and not empty and the warning is false', () => {
  const wrapper = mount(<Permissions.Provider value={false}><StringInput required={true} warning={false} value='x' options='x' /></Permissions.Provider>);
  expect(wrapper.find('FormDropdown').prop('error')).toBe(false);
});