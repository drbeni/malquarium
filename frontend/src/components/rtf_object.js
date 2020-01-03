import React, {Component} from 'react';
import {Glyphicon, Table} from 'react-bootstrap';

export default class RtfObject extends Component {
  constructor(props) {
    super(props);

    this.state = {details_visible: true};

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
        <button className="plusButton" onClick={this.toggleState}>
          {this.state.details_visible ? <Glyphicon glyph="minus"/> : <Glyphicon glyph="plus"/>}
        </button>&nbsp;
        <span>{data.id}</span>
        {this.state.details_visible ?
          <Table condensed className="sample-sub-table">
            <thead>
            <tr>
              <th>ID</th>
              <th>Index</th>
              <th>OLE Object</th>
            </tr>
            </thead>
            <tbody>
            <tr>
              <td>{data.id}</td>
              <td>{data.index}</td>
              <td>
                {data.ole_object.error === undefined ?
                  <span>
                Format type: {data.ole_object.format_type}<br/>
                Data size: {data.ole_object.data_size}<br/>
                    {
                      data.ole_object.CLSID !== undefined ?
                        <span>
                    CLSID: {data.ole_object.CLSID}<br/>
                    CLSID desc: {data.ole_object.CLSID_desc}
                  </span> : null
                    }

                    {
                      data.ole_object.package !== undefined ?
                        <span>
                    Package filename: {data.ole_object.package.filename}<br/>
                    Package source path: {data.ole_object.package.source_path}<br/>
                    Package temp path: {data.ole_object.package.temp_path}<br/>
                    Is Executable: {data.ole_object.package.executable}<br/>
                  </span> : null
                    }

                </span> : <span>{data.ole_object.error}</span>
                }
              </td>
            </tr>
            </tbody>
          </Table>
          : ''
        }
      </div>
    );
  }
}
