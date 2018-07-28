import React, {Component} from 'react';
import {Glyphicon} from 'react-bootstrap';

export default class PEImport extends Component {
  constructor(props) {
    super(props);

    this.state = {details_visible: false};

    this.toggleState = this.toggleState.bind(this);
  }

  toggleState(event) {
    event.preventDefault();
    this.setState({details_visible: !this.state.details_visible});
  }

  renderImportFunction(functionItem) {
    return (
      <li key={functionItem.Address}>{functionItem.Name}</li>
    )
  }

  render() {
    const dll = this.props.dll;
    return (
      <div>
        <a href="" onClick={this.toggleState}><Glyphicon glyph="plus"/></a>&nbsp;
        <span>{dll.Name}</span>
        {this.state.details_visible ?
          <div className="pe-import-details">
            <ul>
              {dll.Imports.map(this.renderImportFunction)}
            </ul>
          </div>
          : ''
        }
      </div>
    );
  }
}
