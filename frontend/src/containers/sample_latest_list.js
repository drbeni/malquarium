import React, {Component} from 'react';
import {Link} from 'react-router-dom';
import {connect} from 'react-redux';
import {Label, Table} from 'react-bootstrap';

import LoadingSpinner from '../components/loading_spinner';
import {getLatestSamples} from '../actions';

class SampleLatestList extends Component {
  constructor(props) {
    super(props);

    this.renderSample = this.renderSample.bind(this);
  }

  componentDidMount() {
    this.props.getLatestSamples();
  }

  renderTags(tag) {
    return (
      <Label bsStyle="default" bsClass="label block-label" key={tag.name}>
        {tag.name}
      </Label>
    )
  }

  renderSample(sample) {
    const date = new Date(sample.create_date);

    return (
      <tr key={sample.sha2}>
        <td>
          {date.toLocaleDateString()} {date.toLocaleTimeString()}
        </td>
        <td>
          <Link to={`/samples/${sample.sha2}`}>{sample.sha2}</Link>
        </td>
        <td>
          {sample.tags.map(this.renderTags)}
        </td>
        <td>
          {sample.source}
        </td>
        <td>
          {sample.vt_result}
        </td>
      </tr>
    );
  }

  render() {
    if (this.props.showLoadingSpinner) {
      return <LoadingSpinner/>
    }

    const samples = this.props.latestSamples;

    return (
      <div className="sample-list">
        <h3>Latest submitted samples</h3>
        <Table responsive>
          <thead>
          <tr>
            <th style={{width: '10%'}}>Submitted</th>
            <th style={{width: '40%'}}>SHA-256</th>
            <th style={{width: '30%'}}>Tags</th>
            <th style={{width: '10%'}}>Source</th>
            <th style={{width: '10%'}}>VT</th>
          </tr>
          </thead>
          <tbody>
          {samples.map(this.renderSample)}
          </tbody>
        </Table>
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