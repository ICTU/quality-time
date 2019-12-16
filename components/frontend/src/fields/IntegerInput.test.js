import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { IntegerInput } from './IntegerInput';

describe("<IntegerInput />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<IntegerInput value="42" />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
      expect(wrapper.find("FormInput").prop("readOnly")).toBe(true);
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <IntegerInput value="42" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("42");
      expect(wrapper.find("FormInput").prop("readOnly")).toBe(false);
  })
});