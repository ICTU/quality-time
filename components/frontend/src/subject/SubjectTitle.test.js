import React from 'react';
import { mount } from 'enzyme';
import { EDIT_REPORT_PERMISSION, ReadOnlyContext } from '../context/ReadOnly';
import { SubjectTitle } from './SubjectTitle';

const datamodel = { subjects: { subject_type: { name: "Subject type"} }, metrics: { metric_type: { tags: [] } } }
const report = { report_uuid: "report_uuid", subjects: { subject_uuid: { type: "subject_type", name: "Subject title", metrics: { metric_uuid: { type: "metric_type", tags: [] } } } } };

describe("<SubjectTitle />", () => {
  it('renders the buttons when editable', () => {
      const wrapper = mount(
          <ReadOnlyContext.Provider value={[EDIT_REPORT_PERMISSION]}>
              <SubjectTitle datamodel={datamodel} report={report} reports={[report]} subject={{type: "subject_type"}} />
          </ReadOnlyContext.Provider>
      );
      wrapper.find("Header").simulate("click");
      expect(wrapper.find("DeleteButton").length).toBe(1);
  });
});
