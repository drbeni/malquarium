import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Redirect} from 'react-router'
import {Button, Table} from 'react-bootstrap';

import {fetchProfile, resetApiToken} from "../actions/auth";
import {isAuthenticated} from '../reducers'

import LoadingSpinner from '../components/loading_spinner';

class Profile extends Component {

  componentDidMount() {
    if (this.props.isAuthenticated) {
      this.props.fetchProfile();
    }
  }

  render() {
    if (!this.props.isAuthenticated) {
      return (
        <Redirect to='/'/>
      )
    }

    const profile = this.props.profile;
    const service_plan = profile.service_plan;
    const usage_stats = profile.usage_stats;

    const token_button_text = profile.auth_token ? 'Reset Token' : 'Create Token';

    if (this.props.showLoadingSpinner || !service_plan) {
      return <LoadingSpinner/>
    }

    return (
      <div className="main-view">
        <h2>Profile</h2>
        <Table>
          <tbody>
          <tr>
            <th style={{width: '10em'}}>Username</th>
            <td>{profile.username}</td>
          </tr>
          <tr>
            <th>First name</th>
            <td>{profile.first_name}</td>
          </tr>
          <tr>
            <th>Last name</th>
            <td>{profile.last_name}</td>
          </tr>
          <tr>
            <th>Email</th>
            <td>{profile.email}</td>
          </tr>
          <tr>
            <th>API Token</th>
            <td>
              {profile.auth_token}
              <span style={{marginLeft: '15px'}}>
                <Button onClick={() => this.props.resetApiToken()} bsStyle="danger">{token_button_text}</Button>
              </span>
            </td>
          </tr>
          </tbody>
        </Table>

        <h3>Service Plan</h3>
        <Table responsive>
          <thead>
          <tr>
            <th>Current plan</th>
            <th>Today's Download Quota</th>
            <th>Today's Upload Quota</th>
          </tr>
          </thead>
          <tbody>
          <tr>
            <td>{service_plan.name}</td>
            <td>{usage_stats.download_requests.toLocaleString()} / {service_plan.download_quota.toLocaleString()}</td>
            <td>{usage_stats.upload_requests.toLocaleString()} / {service_plan.upload_quota.toLocaleString()}</td>
          </tr>
          </tbody>
        </Table>
      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    profile: state.profile,
    isAuthenticated: isAuthenticated(state),
    showLoadingSpinner: state.showLoadingSpinner,
  };
}

export default connect(mapStateToProps, {fetchProfile, resetApiToken})(Profile)