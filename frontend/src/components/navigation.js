import React, {Component} from 'react';
import {Link} from 'react-router-dom';
import {Glyphicon, Nav, Navbar, NavItem} from 'react-bootstrap';

import {SITE_NAME} from "../constants";
import AccountNavigation from '../containers/account_navigation';

export default class Navigation extends Component {

  getActiveMenu() {
    const pathname = this.props.history.location.pathname;
    return pathname.endsWith('/') ? pathname.substring(0, pathname.length - 1) : pathname;
  }

  render() {
    return (
      <div>
        <Navbar fixedTop>
          <Navbar.Header>
            <Navbar.Brand>
              <Link to="/" className="logo">{SITE_NAME}</Link>
            </Navbar.Brand>
            <Navbar.Toggle/>
          </Navbar.Header>
          <Navbar.Collapse>
            <Nav
              activeKey={this.getActiveMenu()}
              onSelect={key => this.props.history.push(key)}
            >
              <NavItem eventKey={'/upload'}><Glyphicon glyph="cloud-upload"/></NavItem>
              <NavItem eventKey={'/samples'}><Glyphicon glyph="search"/></NavItem>
            </Nav>
            <AccountNavigation history={this.props.history}/>
          </Navbar.Collapse>
        </Navbar>
      </div>
    );
  }
}