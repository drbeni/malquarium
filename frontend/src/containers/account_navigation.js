import React, {Component} from 'react'
import {connect} from 'react-redux'
import {Glyphicon, Nav, NavDropdown, NavItem} from 'react-bootstrap';
import {isAuthenticated} from '../reducers'

class AccountNavigation extends Component {


  render() {
    if (this.props.isAuthenticated) {
      return (
        <Nav pullRight
             activeKey={this.props.history.location.pathname}
             onSelect={key => this.props.history.push(key)}
        >
          <NavDropdown
            id="nav-dropdown"
            title={<span><Glyphicon glyph="user"/> Account</span>}
          >
            <NavItem eventKey={'/profile'}>Profile</NavItem>
            <NavItem eventKey={'/logout'}>Logout</NavItem>
          </NavDropdown>
        </Nav>
      )
    }
    return (
      <Nav pullRight
           activeKey={this.props.history.location.pathname}
           onSelect={key => this.props.history.push(key)}
      >
        <NavItem eventKey={'/register'}>Register</NavItem>
        <NavItem eventKey={'/login'}>Login</NavItem>
      </Nav>
    )
  }
}

const mapStateToProps = (state) => ({
  isAuthenticated: isAuthenticated(state),
  auth: state.auth,
});

export default connect(mapStateToProps)(AccountNavigation);