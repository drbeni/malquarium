import React, {Component} from 'react';
import {Glyphicon, Table} from 'react-bootstrap';

export default class OleDirectoryEntry extends Component {
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
    const data = this.props.data;
    return (
      <div>
        <a href="" onClick={this.toggleState}>
          {this.state.details_visible ? <Glyphicon glyph="minus"/> : <Glyphicon glyph="plus"/>}
        </a>&nbsp;
        <span>{data.name}</span>
        {this.state.details_visible ?
          <Table condensed className="sample-sub-table">
            <tbody>
            <tr>
              <th>Name</th>
              <td>{data.name}</td>
            </tr>
            <tr>
              <th>Sid</th>
              <td>{data.id}</td>
            </tr>
            <tr>
              <th>Size</th>
              <td>{data.size}</td>
            </tr>
            <tr>
              <th>Type Literal</th>
              <td>{data.type}</td>
            </tr>
            </tbody>
          </Table>
          : ''
        }
      </div>
    );
  }
}
