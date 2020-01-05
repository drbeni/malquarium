import React, {Component} from 'react'
import {Redirect} from 'react-router'
import {isAuthenticated} from '../reducers'
import LoadingSpinner from '../components/loading_spinner.js';
import {Alert, Col, FormGroup, Jumbotron} from "react-bootstrap";
import {connect} from "react-redux";
import axios from "axios";
import {Link} from "react-router-dom";

const API_ROOT_URL = process.env.REACT_APP_API_ROOT_URL;

class AccountActivation extends Component {

  constructor(props) {
    super(props);

    this.state = {
      activated: false,
      errorMessage: null,
    };
  }

  componentDidMount() {
    const {uid, token} = this.props.match.params;

    if (uid !== undefined && token !== undefined) {
      const url = `${API_ROOT_URL}auth/activate/${uid}/${token}/`;
      axios.get(url)
        .then(res => (
          this.setState({activated: true})
        ))
        .catch(res => {
          this.setState({errorMessage: `${res.response.data.details}`})
        })
    }
  }


  render() {
    const uid = this.props.match.params.uid;
    const {activated, errorMessage} = this.state;

    if (this.props.isAuthenticated) {
      return <Redirect to='/'/>
    } else {
      return (
        <div>
          <div className="login-page">
            <Jumbotron className="container">
              <h1 className="logo logo-login">{process.env.REACT_APP_SITE_NAME}</h1>
              <h2>Email address confirmation</h2>
              {errorMessage ?
                <div>
                  <Alert bsStyle="danger">
                    <h4>Oh snap! Something went wrong: {errorMessage}</h4>
                  </Alert>
                  <FormGroup>
                    <Col smOffset={0} sm={10}>
                      <Link role="button" className="btn btn-danger" to="/">Cancel</Link>
                    </Col>
                  </FormGroup>

                </div>
                : null
              }
              {activated ?
                <div>
                  <Alert bsStyle="success">
                    <h4>Email address was confirmed successfully! You can now login.</h4>
                  </Alert>
                  <FormGroup>
                    <Col smOffset={0} sm={10}>
                      <Link role="button" className="btn btn-primary" to="/login">Login</Link>
                    </Col>
                  </FormGroup>

                </div>
                : null
              }

              {!uid ?
                <div>
                  <Alert bsStyle="info">
                    <h4>You just got an email. Please confirm your address by clicking on the link in there.</h4>
                  </Alert>
                  <FormGroup>
                    <Col smOffset={0} sm={10}>
                      <Link role="button" className="btn btn-primary" to="/">Go back</Link>
                    </Col>
                  </FormGroup>
                </div>

                : null
              }
            </Jumbotron>
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
  isAuthenticated: isAuthenticated(state),
  showLoadingSpinner: state.showLoadingSpinner,
});

export default connect(mapStateToProps)(AccountActivation);