import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { DateInput } from './DateInput';

function input_wrapper(props) {
  return mount(
    <ReadOnlyContext.Provider value={false}>
      <DateInput {...props} />
    </ReadOnlyContext.Provider>
  )
}
let mock_set_value;

describe("<DateInput />", () => {
  beforeEach(() => { mock_set_value = jest.fn(); });

  it('renders the value read only', () => {
      const wrapper = mount(<DateInput value="2019-09-30" />);
      expect(wrapper.find("FormInput").prop("value")).toStrictEqual("2019-09-30");
  });
  it('renders the editable value', () => {
      const wrapper = input_wrapper({value: "2019-09-30"})
      expect(wrapper.find('EditableDateInput').prop("value")).toStrictEqual("2019-09-30");
  });
  it('submits the value when changed', () => {
    const wrapper = input_wrapper({value: "2019-09-30", set_value: mock_set_value})
    wrapper.find("input").simulate("change", {target: {value: "2020-01-02"}});
    wrapper.find("input").simulate("keydown", {key: "Enter"});
    expect(mock_set_value).toHaveBeenCalled();
  });
  it('does not submit the value when the value is not changed', () => {
    const wrapper = input_wrapper({value: "2020-01-02", set_value: mock_set_value})
    wrapper.find("input").simulate("change", {target: {value: "2020-01-02"}});
    wrapper.find("input").simulate("keydown", {key: "Enter"});
    expect(mock_set_value).not.toHaveBeenCalled();
  });
});