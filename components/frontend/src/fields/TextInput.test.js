import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { TextInput } from './TextInput';

describe("<TextInput />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<TextInput value="Hello" />);
      expect(wrapper.find("FormTextArea").prop("value")).toStrictEqual("Hello");
      expect(wrapper.find("FormTextArea").prop("readOnly")).toBe(true);
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <TextInput value="Hello" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find("FormTextArea").prop("value")).toStrictEqual("Hello");
      expect(wrapper.find("FormTextArea").prop("readOnly")).toBe(false);
  })
});