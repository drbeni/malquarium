import React, {Component} from 'react';

import Navigation from './navigation';
import SampleUpload from '../containers/sample_upload';
import GlobalError from '../containers/global_errors';

export default class UploadView extends Component {
  render() {
    return (
      <div>
        <Navigation history={this.props.history}/>
        <SampleUpload/>
        <GlobalError/>
      </div>
    );
  }
}