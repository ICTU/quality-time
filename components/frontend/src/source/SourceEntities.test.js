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
                    attributes: [{key: "1"}, {key: "2"}]
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
            key: "1"
        },
        {
            key: "2"
        }
    ]
}

describe('<SourceEntities />', () => {
    it('renders', () => {
        const wrapper = mount(<SourceEntities datamodel={data_model} metric={metric} source={source} />);
        expect(wrapper.find("TableRow").at(1).hasClass("status_unknown"))
    });
    it('sorts', () => {
        const wrapper = mount(<SourceEntities datamodel={data_model} metric={metric} source={source} />);
        wrapper.find("TableHeaderCell").at(1).simulate("click");
        expect(wrapper.find("TableHeaderCell").at(1).prop("sorted")).toBe("ascending");
        wrapper.find("TableHeaderCell").at(1).simulate("click");
        expect(wrapper.find("TableHeaderCell").at(1).prop("sorted")).toBe("descending");
        wrapper.find("TableHeaderCell").at(2).simulate("click");
        expect(wrapper.find("TableHeaderCell").at(2).prop("sorted")).toBe("descending");
        wrapper.find("TableHeaderCell").at(2).simulate("click");
        expect(wrapper.find("TableHeaderCell").at(2).prop("sorted")).toBe("ascending");
    })
});