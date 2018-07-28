import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {Alert} from 'react-bootstrap';

import {resetErrorMessage} from "../actions";

class GlobalError extends Component {
  constructor(props) {
    super(props);

    this.handleDismiss = this.handleDismiss.bind(this);

    this.state = {
      show: false,
    };
  }

  handleDismiss() {
    this.props.resetErrorMessage();
  }

  render() {
    if (this.props.errorMessage) {
      return (
        <Alert bsStyle="danger" onDismiss={this.handleDismiss}>
          <h4>Oh snap! Something went wrong: {this.props.errorMessage}</h4>
        </Alert>
      );
    }
    return null;
  }
}

function mapStateToProps(state) {
  return {
    errorMessage: state.errorMessage
  }
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({resetErrorMessage}, dispatch);
}


export default connect(mapStateToProps, mapDispatchToProps)(GlobalError);