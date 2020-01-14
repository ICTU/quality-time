import React from 'react';
import { mount } from 'enzyme';
import { StatusIcon } from './StatusIcon';

describe('<StatusIcon/>' , () => {
  it('renders a checkmark if the status is target_met', () => {
    const wrapper = mount(<StatusIcon status="target_met" />);
    expect(wrapper.find("Icon").prop("name")).toBe("check");
  })
  it('renders a question mark if the status is missing', () => {
    const wrapper = mount(<StatusIcon/>);
    expect(wrapper.find("Icon").prop("name")).toBe("question");
  })
})