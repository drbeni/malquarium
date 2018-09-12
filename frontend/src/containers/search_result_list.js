import React, {Component} from 'react';
import {connect} from 'react-redux';
import {bindActionCreators} from 'redux';
import Pagination from "react-js-pagination";
import {Redirect} from 'react-router'

import SampleList from '../components/sample_list';
import NothingFound from '../components/nothing_found';
import LoadingSpinner from '../components/loading_spinner';

import {searchSamples} from '../actions';

class SearchResultList extends Component {
  constructor(props) {
    super(props);

    this.handlePageChange = this.handlePageChange.bind(this);

    this.state = {
      activePage: 1,
    }
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

        <SampleList samples={samples.results}/>
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

export default connect(mapStateToProps, mapDispatchToProps)(SearchResultList)