import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Redirect} from 'react-router'

import LoginForm from '../components/login_form'
import {login} from '../actions/auth'
import {authErrors, isAuthenticated} from '../reducers'
import LoadingSpinner from '../components/loading_spinner';

class Login extends Component {

  render() {
    if (this.props.isAuthenticated) {
      if (this.props.urlHistory[1] && !this.props.urlHistory[1].startsWith('/activate/')) {
        return <Redirect to={this.props.urlHistory[1]}/>
      } else {
        return <Redirect to='/'/>
      }
    } else {
      return (
        <div>
          <div className="login-page">
            <LoginForm {...this.props}/>
          </div>
          <div>
            {this.props.showLoadingSpinner ? <LoadingSpinner/> : ''}
          </div>
        </div>
      )
    }
  }
}

const mapStateToProps = (state) => ({
  errors: authErrors(state),
  isAuthenticated: isAuthenticated(state),
  showLoadingSpinner: state.showLoadingSpinner,
  urlHistory: state.urlHistory
});

const mapDispatchToProps = (dispatch) => ({
  onSubmit: (username, password) => {
    dispatch(login(username, password))
  }
});

export default connect(mapStateToProps, mapDispatchToProps)(Login);