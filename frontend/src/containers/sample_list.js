import React, {Component} from 'react';
import {Link} from 'react-router-dom';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';
import {Label, Table} from 'react-bootstrap';
import Pagination from "react-js-pagination";
import {Redirect} from 'react-router'

import NothingFound from '../components/nothing_found';
import LoadingSpinner from '../components/loading_spinner';

import {searchSamples} from '../actions';

class SampleList extends Component {
  constructor(props) {
    super(props);

    this.renderSample = this.renderSample.bind(this);
    this.handlePageChange = this.handlePageChange.bind(this);

    this.state = {
      activePage: 1,
    }
  }

  renderTags(tag) {
    return (
      <Label bsStyle="default" bsClass="label block-label" key={tag.name}>
        {tag.name}
      </Label>
    )
  }

  renderSample(sample) {
    return (
      <tr key={sample.sha2}>
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

  handlePageChange(pageNumber) {
    this.props.searchSamples(this.props.samples.search_string, pageNumber);
    this.setState({activePage: pageNumber});
  }

  render() {
    if (this.props.showLoadingSpinner) {
      return <LoadingSpinner/>
    }

    const samples = this.props.samples;
    const sample = this.props.sample;

    if (samples.results === undefined) {
      return null
    } else if (samples.count === 0) {
      return (
        <NothingFound message={`No matches found for "${samples.search_string}"`}/>
      )
    } else if (samples.count === 1 && (!sample || samples.results[0].sha2 !== sample.sha2)) {
      return (
        <Redirect to={`/samples/${samples.results[0].sha2}`}/>
      )
    }

    return (
      <div className="sample-list">
        <h4>Results matching "{samples.search_string}"</h4>

        {!(samples.next === null && samples.previous === null) ?
          <Pagination
            activePage={this.state.activePage}
            itemsCountPerPage={20}
            totalItemsCount={samples.count}
            pageRangeDisplayed={5}
            onChange={this.handlePageChange}
          />
          : ''
        }

        <Table responsive>
          <thead>
          <tr>
            <th style={{width: '40%'}}>SHA-256</th>
            <th style={{width: '40%'}}>Tags</th>
            <th style={{width: '10%'}}>Source</th>
            <th style={{width: '10%'}}>VT</th>
          </tr>
          </thead>
          <tbody>
          {samples.results.map(this.renderSample)}
          </tbody>
        </Table>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    samples: state.samples,
    sample: state.sample,
    showLoadingSpinner: state.showLoadingSpinner,
  };
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({searchSamples}, dispatch);
}

export default connect(mapStateToProps, mapDispatchToProps)(SampleList)