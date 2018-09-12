import React, {Component} from 'react';
import {connect} from 'react-redux';

import SampleList from '../components/sample_list';
import LoadingSpinner from '../components/loading_spinner';
import {getLatestSamples} from '../actions';

class SampleLatestList extends Component {
  componentDidMount() {
    this.props.getLatestSamples();
  }

  render() {
    if (this.props.showLoadingSpinner) {
      return <LoadingSpinner/>
    }

    const samples = this.props.latestSamples;

    return (
      <div>
        <h3>Latest submitted samples</h3>
        <SampleList samples={samples}/>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    latestSamples: state.latestSamples,
    showLoadingSpinner: state.showLoadingSpinner,
  };
}

export default connect(mapStateToProps, {getLatestSamples})(SampleLatestList)