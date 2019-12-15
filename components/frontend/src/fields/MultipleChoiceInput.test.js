import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { MultipleChoiceInput } from './MultipleChoiceInput';

describe("<MultipleChoiceInput />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<MultipleChoiceInput value={["hello"]} options={["hello", "again"]} />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual(["hello"]);
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <MultipleChoiceInput value={["hello"]} options={["hello", "again"]}/>
        </ReadOnlyContext.Provider>);
      expect(wrapper.find('FormDropdown').prop("value")).toStrictEqual(["hello"]);
  })
});