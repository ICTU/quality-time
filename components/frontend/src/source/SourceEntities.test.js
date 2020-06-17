import React from 'react';
import { mount } from 'enzyme';
import { SourceEntities } from './SourceEntities';

const data_model = {
    sources: {
        source_type: {
            entities: {
                metric_type:
                {
                    name: "entity name",
                    attributes: [
                        { key: "integer", type: "integer" }, { key: "float", type: "float" }, { key: "text", type: "text" }
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
            text: "C"
        },
        {
            key: "2",
            integer: "3",
            float: "0.2",
            text: "B"
        },
        {
            key: "3",
            integer: "2",
            float: "0.1",
            text: "A"
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
        expectSorting(2, true, { 0: "1", 3: "2", 6: "3" });
        sortColumn(2);
        expectSorting(2, false, { 0: "3", 3: "2", 6: "1" });
        sortColumn(3);
        expectSorting(3, false, { 1: "0.3", 4: "0.2", 7: "0.1" });
        sortColumn(3);
        expectSorting(3, true, { 1: "0.1", 4: "0.2", 7: "0.3" });
        sortColumn(4);
        expectSorting(4, true, { 2: "A", 5: "B", 8: "C" });
        sortColumn(4);
        expectSorting(4, false, { 2: "C", 5: "B", 8: "A" });
    })
});