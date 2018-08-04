import React, {Component} from 'react'
import {Link} from 'react-router-dom';
import {Alert, Button, Col, ControlLabel, Form, FormControl, FormGroup, HelpBlock, Jumbotron} from 'react-bootstrap';

import {CONTACT_EMAIL, SITE_NAME} from "../constants";

export default class LoginForm extends Component {
  constructor(props, context) {
    super(props, context);

    this.handleChange = this.handleChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);

    this.state = {
      username: '',
      password: ''
    };
  }

  componentDidMount() {
    document.title = `${SITE_NAME} - Login`;
  }

  handleChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });


  };

  onSubmit(event) {
    event.preventDefault();
    this.props.onSubmit(this.state.username, this.state.password)
  };

  getValidationState(field) {
    const errors = this.props.errors.data || {};

    if (errors[field] !== undefined) {
      return 'error';
    }
  }

  render() {
    const errors = this.props.errors.data || {};

    return (
      <Jumbotron className="container">
        <Form onSubmit={this.onSubmit} horizontal>
          <h1 className="logo logo-login">{SITE_NAME}</h1>

          <h2>Login</h2>

          <FormGroup
            controlId="authUsername"
            validationState={this.getValidationState('username')}
          >
            <Col componentClass={ControlLabel} sm={2}>
              Username
            </Col>
            <Col sm={10}>
              <FormControl
                type="text"
                placeholder="Username"
                value={this.state.username}
                onChange={this.handleChange}
                name="username"
              />
              <HelpBlock>{errors.username}</HelpBlock>
            </Col>
          </FormGroup>

          <FormGroup
            controlId="authPassword"
            validationState={this.getValidationState('username')}
          >
            <Col componentClass={ControlLabel} sm={2}>
              Password
            </Col>
            <Col sm={10}>
              <FormControl
                type="password"
                placeholder="Password"
                value={this.state.password}
                onChange={this.handleChange}
                name="password"
              />
              <HelpBlock>{errors.password}</HelpBlock>
            </Col>
          </FormGroup>

          {
            errors.non_field_errors ?
              <Alert bsStyle="danger">
                {errors.non_field_errors}
              </Alert> : ""
          }

          <FormGroup>
            <Col smOffset={2} sm={10}>
              <Button type="submit" bsStyle="primary">Sign in</Button>
              <Link role="button" className="btn btn-danger" to="/">Cancel</Link>
            </Col>
          </FormGroup>

          <div>
            Don't have an account? Write an e-mail to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> explaining who you are
            and why you would like access.
          </div>
        </Form>
      </Jumbotron>
    )
  }
}