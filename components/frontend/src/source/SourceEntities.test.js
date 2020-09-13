import React from 'react';
import { mount } from 'enzyme';
import { SourceEntities } from './SourceEntities';

const data_model = {
    entities: {
        statuses: {
            unconfirmed: {
                default: true,
                ignore_entity: false
            },
            confirmed: {
                default: true,
                ignore_entity: false
            },
            false_positive: {
                default: true,
                ignore_entity: true
            },
            wont_fix: {
                default: true,
                ignore_entity: true
            },
            fixed: {
                default: true,
                ignore_entity: true
            }
        }
    },
    sources: {
        source_type: {
            entities: {
                metric_type:
                {
                    name: "entity name",
                    attributes: [
                        { key: "integer", type: "integer" },
                        { key: "float", type: "float" },
                        { key: "text", type: "text" },
                        { key: "date", type: "date" },
                        { key: "datetime", type: "datetime" }
                    ]
                }
            }
        }
    }
}

const metric = {
    type: "metric_type",
    sources: {
        source_uuid: {
            type: "source_type"
        }
    }
}

const source = {
    source_uuid: "source_uuid",
    entities: [
        {
            key: "1",
            integer: "1",
            float: "0.3",
            text: "C",
            date: "01-01-2000",
            datetime: "2000-01-01T10:00:00Z"
        },
        {
            key: "2",
            integer: "3",
            float: "0.2",
            text: "B",
            date: "01-01-2002",
            datetime: "2002-01-01T10:00:00Z"
        },
        {
            key: "3",
            integer: "2",
            float: "0.1",
            text: "A",
            date: "01-01-2001",
            datetime: "2001-01-01T10:00:00Z"
        }
    ]
}

describe('<SourceEntities />', () => {
    it('renders', () => {
        const wrapper = mount(<SourceEntities datamodel={data_model} metric={metric} source={source} />);
        expect(wrapper.find("TableRow").at(1).hasClass("status_unknown"))
    });
    it('sorts', () => {
        function expectSorting(columnIndex, ascending, attributes) {
            expect(wrapper.find("TableHeaderCell").at(columnIndex).prop("sorted")).toBe(ascending ? "ascending" : "descending");
            Object.entries(attributes).forEach(([index, value]) => {
                expect(wrapper.find("SourceEntityAttribute").at(index).text()).toBe(value);
            }
            );
        }
        function sortColumn(columnIndex) {
            wrapper.find("TableHeaderCell").at(columnIndex).simulate("click");
        }
        const wrapper = mount(<SourceEntities datamodel={data_model} metric={metric} source={source} />);
        sortColumn(2);
        expectSorting(2, true, { 0: "1", 5: "2", 10: "3" });
        sortColumn(2);
        expectSorting(2, false, { 0: "3", 5: "2", 10: "1" });
        sortColumn(3);
        expectSorting(3, false, { 1: "0.3", 6: "0.2", 11: "0.1" });
        sortColumn(3);
        expectSorting(3, true, { 1: "0.1", 6: "0.2", 11: "0.3" });
        sortColumn(4);
        expectSorting(4, true, { 2: "A", 7: "B", 12: "C" });
        sortColumn(4);
        expectSorting(4, false, { 2: "C", 7: "B", 12: "A" });
        sortColumn(5);
        expectSorting(5, false, { 0: "3", 5: "2", 10: "1" });
        sortColumn(5);
        expectSorting(5, true, { 0: "1", 5: "2", 10: "3" });
        sortColumn(6);
        expectSorting(6, true, { 0: "1", 5: "2", 10: "3" });
        sortColumn(6);
        expectSorting(6, false, { 0: "3", 5: "2", 10: "1" });
    })
});