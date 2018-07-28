import React, {Component} from 'react';

import Navigation from './navigation';
import SearchBar from '../containers/search_bar';
import SampleStats from '../containers/sample_stats';
import SampleLatestList from '../containers/sample_latest_list';
import {SITE_NAME} from "../constants";

export default class IndexView extends Component {
  componentDidMount() {
    document.title = SITE_NAME;
  }

  render() {
    return (
      <div className="main-view">
        <Navigation history={this.props.history}/>

        <div>
          <h1>A free Malware Repository</h1>
          <p>
            Providing security researchers and other curious people access to malware samples.
          </p>
          <br/>
          <br/>
        </div>
        <SearchBar history={this.props.history}/>
        <br/>
        <br/>
        <SampleLatestList/>
        <SampleStats/>
      </div>
    );
  }
}