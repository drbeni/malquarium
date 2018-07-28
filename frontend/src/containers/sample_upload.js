import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Link} from 'react-router-dom';

import {fetchAllTags, uploadSample} from "../actions";
import LoadingSpinner from '../components/loading_spinner';
import SampleUploadForm from '../components/sample_upload_form';
import {isAuthenticated, capabilities} from "../reducers";

class SampleUpload extends Component {

  onSubmit(values) {
    this.props.uploadSample(values, () => {
      this.props.history.push('/');
    });
  }

  componentDidMount() {
    this.props.fetchAllTags();
  }

  render() {
    if (this.props.isAuthenticated) {
      return (
        <div>
          <div>
            <SampleUploadForm {...this.props}/>
          </div>
          <div>
            {this.props.showLoadingSpinner ? <LoadingSpinner/> : ''}
          </div>
        </div>
      )
    } else {
      return <div>
        Please <Link to="/login/">login</Link> to upload your samples
      </div>
    }
  }
}

const mapStateToProps = (state) => ({
  isAuthenticated: isAuthenticated(state),
  capabilities: capabilities(state),
  showLoadingSpinner: state.showLoadingSpinner,
  allTags: state.tags,
});


export default connect(mapStateToProps, {uploadSample, fetchAllTags})(SampleUpload);