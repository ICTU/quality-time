import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { MultipleChoiceInput } from './MultipleChoiceInput';

function input_wrapper(props) {
  return mount(
    <ReadOnlyContext.Provider value={false}>
      <MultipleChoiceInput {...props} />
    </ReadOnlyContext.Provider>
  )
}
let mock_set_value;

describe("<MultipleChoiceInput />", () => {
  beforeEach(() => { mock_set_value = jest.fn(); });

  it('renders the value read only', () => {
    const wrapper = mount(<MultipleChoiceInput value={["hello"]} options={["hello", "again"]} />);
    expect(wrapper.find("FormInput").prop("value")).toStrictEqual(["hello"]);
  });
  it('renders the editable value', () => {
    const wrapper = input_wrapper({ value: ["hello"], options: ["hello", "again"] });
    expect(wrapper.find('FormDropdown').prop("value")).toStrictEqual(["hello"]);
  });
  it('invokes the callback on a change', () => {
    const nativeEvent = { nativeEvent: { stopImmediatePropagation: () => {} } }
    const wrapper = input_wrapper({ allowAdditions: true, value: ["hello"], options: ["hello", "hi", "ho"], set_value: mock_set_value });
    wrapper.find("input").simulate("change", {target: {value: "ciao"}});
    wrapper.find("DropdownItem").simulate("click", nativeEvent);
    expect(mock_set_value).toHaveBeenCalled();
  });
});