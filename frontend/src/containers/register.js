import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Redirect} from 'react-router'

import RegisterForm from '../components/register_form'
import {register} from '../actions/auth'
import {authErrors, isAuthenticated} from '../reducers'
import LoadingSpinner from '../components/loading_spinner';

class Register extends Component {

  render() {
    if (this.props.isAuthenticated) {
      return <Redirect to='/'/>
    } else {
      return (
        <div>
          <div className="login-page">
            <RegisterForm {...this.props}/>
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
    dispatch(register(username, password))
  }
});

export default connect(mapStateToProps, mapDispatchToProps)(Register);