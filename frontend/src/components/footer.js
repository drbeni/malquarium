import React, {Component} from 'react';
import {Nav, Navbar, NavItem} from 'react-bootstrap';

import {SITE_NAME, CONTACT_EMAIL} from "../constants";

export default class Footer extends Component {

  render() {
    return (
      <div id="footer">
        <Navbar inverse>
          <Nav onSelect={key => this.props.history.push(key)}>
            <NavItem eventKey="/about-api">API</NavItem>
            <NavItem href={`mailto:${CONTACT_EMAIL}`}>Contact</NavItem>
          </Nav>
          <Navbar.Text>© 2018 drbeni</Navbar.Text>
          <Navbar.Text pullRight>
            Project on <a href="https://github.com/drbeni/malquarium" target="_blank" rel="noopener noreferrer">GitHub</a>
          </Navbar.Text>
        </Navbar>
      </div>
    );
  }
}