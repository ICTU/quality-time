import React from 'react';
import { mount } from 'enzyme';
import { Avatar } from './Avatar';

it('shows the image when passed an email address', () => {
    const wrapper = mount(<Avatar email="foo@bar" />);
    expect(wrapper.find("Image").length).toBe(1);
});

it('shows an icon when not passed an email address', () => {
    const wrapper = mount(<Avatar email="" />);
    expect(wrapper.find("Icon").length).toBe(1);
});