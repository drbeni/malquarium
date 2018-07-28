import React, {Component} from 'react';
import {Panel} from 'react-bootstrap';

export default class NothingFound extends Component {
  render() {
    return (
      <Panel bsStyle="info">
        <Panel.Heading>{this.props.message}</Panel.Heading>
      </Panel>
    );
  }
}
