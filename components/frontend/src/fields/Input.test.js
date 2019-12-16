import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Input } from './Input';

describe("<Input />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<Input value="Hello" />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("Hello");
      expect(wrapper.find("FormInput").prop("readOnly")).toBe(true);
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <Input value="Hello" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("Hello");
      expect(wrapper.find("FormInput").prop("readOnly")).toBe(false);
  })
});