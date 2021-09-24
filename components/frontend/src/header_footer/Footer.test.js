import React from 'react';
import { mount } from 'enzyme';
import { Footer } from './Footer';

describe("<Footer />", () => {
  it('renders the report title when there is a report', () => {
      const last_update = new Date();
      const wrapper = mount(<Footer report={{title: "Report"}} last_update={last_update} />);
      expect(wrapper.find("AboutReportColumn").find("ListItem").at(0).text()).toStrictEqual("Report");
      expect(wrapper.find("AboutReportColumn").find("ListItem").at(0).prop('href')).not.toBe(null);
      expect(wrapper.find("AboutReportColumn").find("ListItem").at(0).prop('href')).not.toBe(undefined);
  });
  it('renders the quote title when there is no report', () => {
      const wrapper = mount(<Footer />);
      expect(wrapper.find("QuoteColumn").find("ListItem").at(2).text()).toStrictEqual("Johan Cruyff");
  });
});