import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { DateInput } from './DateInput';

describe("<DateInput />", () => {
  it('renders the value read only', () => {
      const wrapper = mount(<DateInput value="2019-09-30" />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("2019-09-30");
  });
  it('renders the editable value', () => {
      const wrapper = mount(
        <ReadOnlyContext.Provider value={false}>
          <DateInput value="2019-09-30" />
        </ReadOnlyContext.Provider>);
      expect(wrapper.find('EditableDateInput').prop("value")).toStrictEqual("2019-09-30");
  })
});