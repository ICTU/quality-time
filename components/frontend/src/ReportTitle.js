import React, { Component } from 'react';
import { Form, Icon } from 'semantic-ui-react';


class ReportTitle extends Component {
  constructor(props) {
    super(props);
    this.state = {title: "Quality-time", edit: false, editable: false}
  }
  componentDidMount() {
    let self = this;
    fetch('http://localhost:8080/report/title')
      .then(function(response) {
        return response.json();
      })
      .then(function(json) {
        self.setState({title: json.title});
      });
  }
  onClick() {
    this.setState({edit: true});
  }
  onChange(event) {
    this.setState({title: event.target.value});
  }
  onKeyDown(event) {
    if (event.key === "Escape") {
      this.setState((state) => ({edit: false, title: state.title}))
    }
  }
  onMouseEnter(event) {
    this.setState({editable: true})
  }
  onMouseLeave(event) {
    this.setState({editable: false})
  }
  onSubmit(event) {
    event.preventDefault();
    this.setState({edit: false});
    fetch('http://localhost:8080/report/title', {
      method: 'post',
      mode: 'cors',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({title: this.state.title})
    })
  }
  render() {
    if (this.state.edit) {
      return (
        <Form onSubmit={(e) => this.onSubmit(e)}>
          <Form.Input autoFocus focus defaultValue={this.state.title}
            onChange={(e) => this.onChange(e)} onKeyDown={(e) => this.onKeyDown(e)} />
        </Form>
      )
    }
    const style = this.state.title ? {marginRight: "10px"} : {marginRight: "10px"};
    return (
      <div onClick={(e) => this.onClick(e)} onMouseEnter={(e) => this.onMouseEnter(e)}
           onMouseLeave={(e) => this.onMouseLeave(e)}>
        <span style={style}>
          <font size="+3">
            {this.state.title}
          </font>
        </span>
        {this.state.editable && <Icon color='grey' name='edit' />}
      </div>
    )
  }
}

export { ReportTitle };
