import React, {Component} from 'react';
import {Glyphicon} from 'react-bootstrap';

export default class MacroCodeStream extends Component {
  constructor(props) {
    super(props);

    this.state = {details_visible: false};

    this.toggleState = this.toggleState.bind(this);
  }

  toggleState(event) {
    event.preventDefault();
    this.setState({details_visible: !this.state.details_visible});
  }


  render() {
    const macro = this.props.macro;
    return (
      <div>
        <a href="" onClick={this.toggleState}>
          {this.state.details_visible ? <Glyphicon glyph="minus"/> : <Glyphicon glyph="plus"/>}
        </a>&nbsp;
        <span>{macro.vba_filename}</span>
        {this.state.details_visible ?
          <div className="macro-code-details">
            {macro.vba_code}
          </div>
          : ''
        }
      </div>
    );
  }
}
