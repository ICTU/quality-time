import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { SingleChoiceInput } from './SingleChoiceInput';

describe("<SingleChoiceInput />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<SingleChoiceInput value="hello" options={[{text: "hello", value: "hello"}]} />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("hello");
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <SingleChoiceInput value="hello" options={[{text: "hello", value: "hello"}]}/>
        </ReadOnlyContext.Provider>);
      expect(wrapper.find('FormDropdown').prop("value")).toStrictEqual("hello");
  })
});