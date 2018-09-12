import React, {Component} from 'react';

import Navigation from './navigation';
import GlobalError from '../containers/global_errors'
import SearchBar from '../containers/search_bar';
import SearchResultList from '../containers/search_result_list';
import {SITE_NAME} from "../constants";

export default class SampleListView extends Component {
  componentDidMount() {
    document.title = `${SITE_NAME} - Search`;
  }

  render() {
    return (
      <div>
        <Navigation history={this.props.history}/>
        <GlobalError/>
        <SearchBar history={this.props.history}/>
        <SearchResultList/>
      </div>
    );
  }
}