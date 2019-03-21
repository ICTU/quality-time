import React, { Component } from 'react'
import { Dropdown } from 'semantic-ui-react'

const options = [
  { key: 'English', text: 'English', value: 'English' },
  { key: 'French', text: 'French', value: 'French' },
  { key: 'Spanish', text: 'Spanish', value: 'Spanish' },
  { key: 'German', text: 'German', value: 'German' },
  { key: 'Chinese', text: 'Chinese', value: 'Chinese' },
]
  
const renderLabel = label => ({
  color: 'blue',
  content: `${label.text}`,
  icon: 'check',
})


class MultipleChoiceParameterAddition extends Component {
  state = { options }
  

  handleAddition = (e, { value }) => {
    this.setState({
      options: [{ text: value, value }, ...this.state.options],
    })
  }
  

  handleChange = (e, { value }) => this.setState({ currentValues: value })

  render() {
    const { currentValues } = this.state
    

    return (
      <Dropdown
        options={this.state.options}
        placeholder='Choose Languages'
        search
        selection
        fluid
        multiple
        allowAdditions
        value={currentValues}
        onAddItem={this.handleAddition}
        onChange={this.handleChange}
        renderLabel={renderLabel}
      />
    )
  }
}
export {MultipleChoiceParameterAddition};
