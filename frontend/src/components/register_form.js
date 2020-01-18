import React, {Component} from 'react'
import {Link} from 'react-router-dom';
import {Alert, Button, Col, ControlLabel, Form, FormControl, FormGroup, HelpBlock, Jumbotron} from 'react-bootstrap';

export default class RegisterForm extends Component {
  constructor(props, context) {
    super(props, context);

    this.handleChange = this.handleChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);

    this.state = {
      email: '',
      password: ''
    };
  }

  componentDidMount() {
    document.title = `${process.env.REACT_APP_SITE_NAME} - Register`;
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
    this.props.onSubmit(this.state.email, this.state.password)
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
          <h1 className="logo logo-login">{process.env.REACT_APP_SITE_NAME}</h1>

          <h2>Register for a new account</h2>

          <FormGroup
            controlId="authEmail"
            validationState={this.getValidationState('email')}
          >
            <Col componentClass={ControlLabel} sm={2}>
              Email
            </Col>
            <Col sm={10}>
              <FormControl
                type="text"
                placeholder="Email"
                value={this.state.email}
                onChange={this.handleChange}
                name="email"
              />
              <HelpBlock>{errors.email}</HelpBlock>
            </Col>
          </FormGroup>

          <FormGroup
            controlId="authPassword"
            validationState={this.getValidationState('password')}
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
              <Button type="submit" bsStyle="primary">Register</Button>
              <Link role="button" className="btn btn-danger" to="/">Cancel</Link>
            </Col>
          </FormGroup>

        </Form>
      </Jumbotron>
    )
  }
}