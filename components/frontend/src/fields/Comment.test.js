import React from 'react';
import { shallow } from 'enzyme';
import { Comment } from './Comment';

describe("<Comment />", () => {
    it('renders the comment label', () => {
        const wrapper = shallow(<Comment />);
        expect(wrapper.find('TextInput').prop("label")).toBe("Comment");
    });
    it('renders a placeholder', () => {
        const wrapper = shallow(<Comment />);
        const placeholder = "Enter comments here (HTML allowed; URL's are transformed into links)";
        expect(wrapper.find('TextInput').prop("placeholder")).toBe(placeholder);
    })
});