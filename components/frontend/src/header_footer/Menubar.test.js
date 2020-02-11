import React from 'react';
import { mount } from 'enzyme';
import { Menubar } from './Menubar';

it('calls the callback on click', () => {
  const mockCallBack = jest.fn();
  const wrapper = mount(<Menubar report_date_string="2019-10-10" onDate={console.log} go_home={mockCallBack}/>);
  wrapper.find("MenuItem").at(0).simulate("click");
  expect(mockCallBack).toHaveBeenCalled();
});