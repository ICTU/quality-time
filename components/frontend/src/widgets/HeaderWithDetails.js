import React, { Component } from 'react';
import { Header, Icon } from 'semantic-ui-react';

export class HeaderWithDetails extends Component {
    constructor(props) {
        super(props);
        this.state = { show_details: false };
    }
    expand_or_collapse_details(event) {
        event.preventDefault();
        this.setState((state) => ({ show_details: !state.show_details }));
    }
    render() {
        const margin_top = this.props.level === 'h1' ? 50 : 0;
        return (<>
            <Header as={this.props.level} onClick={(e) => this.expand_or_collapse_details(e)} onKeyPress={(e) => this.expand_or_collapse_details(e)} style={{ marginTop: margin_top }} tabIndex="0">
                <Icon name={this.state.show_details ? "caret down" : "caret right"} size='large' />
                <Header.Content>
                    {this.props.header}
                    <Header.Subheader>{this.props.subheader}</Header.Subheader>
                </Header.Content>
            </Header>
            {this.state.show_details && this.props.children}
        </>);
    }
}
