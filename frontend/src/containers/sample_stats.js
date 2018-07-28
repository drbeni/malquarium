import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Well} from 'react-bootstrap';

import {getSampleStats} from "../actions";


class SampleStats extends Component {

  componentDidMount() {
    this.props.getSampleStats();
  }

  render() {
    if (this.props.stats.count) {
      return (
        <Well>Total Samples: {this.props.stats.count.toLocaleString()}</Well>
      )
    }
    return '';
  }
}

const mapStateToProps = (state) => ({
  stats: state.stats
});


export default connect(mapStateToProps, {getSampleStats})(SampleStats);