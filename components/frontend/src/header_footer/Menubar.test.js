import React from 'react';
import { mount } from 'enzyme';
import { Menubar } from './Menubar';

it('calls the go-home callback on click', () => {
  const mockCallBack = jest.fn();
  const wrapper = mount(<Menubar report_date_string="2019-10-10" onDate={console.log} go_home={mockCallBack}/>);
  wrapper.find("MenuItem").at(0).simulate("click");
  expect(mockCallBack).toHaveBeenCalled();
});

it('calls the scroll-to-dashboard callback on click', () => {
  const mockCallBack = jest.fn();
  const wrapper = mount(<Menubar report_date_string="2019-10-10" onDate={console.log} go_dashboard={mockCallBack} />);
  wrapper.find("Button").at(0).simulate("click");
  expect(mockCallBack).toHaveBeenCalled();
});