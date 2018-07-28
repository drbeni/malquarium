import React, {Component} from 'react';

import Navigation from './navigation';
import GlobalError from '../containers/global_errors'
import Profile from '../containers/profile'

import {SITE_NAME} from "../constants";

export default class AccountView extends Component {
  componentDidMount() {
    document.title = `${SITE_NAME} - Profile`;
  }

  render() {
    return (
      <div>
        <Navigation history={this.props.history}/>
        <GlobalError/>
        <Profile/>
      </div>
    );
  }
}