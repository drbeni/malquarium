import React from 'react'
import {connect} from 'react-redux'
import {Redirect} from 'react-router'
import {logout} from '../actions/auth'
import {isAuthenticated} from '../reducers'

const Logout = (props) => {

  if (props.isAuthenticated) {
    props.logout();

  }
  return (
    <Redirect to='/'/>
  )
};

const mapStateToProps = (state) => ({
  isAuthenticated: isAuthenticated(state)
});

const mapDispatchToProps = (dispatch) => ({
  logout: () => {
    dispatch(logout())
  }
});

export default connect(mapStateToProps, mapDispatchToProps)(Logout);