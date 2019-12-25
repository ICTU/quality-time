import React from 'react';
import { mount } from 'enzyme';
import { ReadOnlyContext } from '../context/ReadOnly';
import { Subjects } from './Subjects';

const report = { subjects: { subject_uuid: { name: "Subject title", metrics: [] } } };

describe("<Subjects />", () => {
    it('shows the subjects', () => {
        const wrapper = mount(<Subjects datamodel={{ subjects: [] }} report={report} />);
        expect(wrapper.find("SubjectTitle").find("HeaderContent").text()).toStrictEqual("Subject title");
    });
    it('shows the add subject button when editable', () => {
        const wrapper = mount(<ReadOnlyContext.Provider value={false}>
            <Subjects datamodel={{ subjects: [] }} report={report} />
        </ReadOnlyContext.Provider>);
        expect(wrapper.find("AddButton").at(1).prop("item_type")).toStrictEqual("subject");
    });
});