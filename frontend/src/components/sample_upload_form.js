import React, {Component} from 'react'
import {Button, Checkbox, ControlLabel, Form, FormControl, FormGroup, HelpBlock} from 'react-bootstrap';
import ReactTags from 'react-tag-autocomplete';

import {SITE_NAME} from "../constants";

export default class SampleUploadForm extends Component {
  constructor(props, context) {
    super(props, context);

    this.handleChange = this.handleChange.bind(this);
    this.onSubmit = this.onSubmit.bind(this);

    this.state = {
      sample: null,
      tags: [],
      private: false,
      changed: false,
      errors: null
    }
  };

  componentDidMount() {
    document.title = `${SITE_NAME} - Upload`;
  }

  handleChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? target.checked : target.value;
    const name = target.name;

    if (target.files) {
      this.setState({
        sample: target.files[0],
        changed: true
      })
    } else {
      this.setState({
        [name]: value,
        changed: true
      });
    }
  };

  onSubmit(event) {
    event.preventDefault();

    if (this.state.changed && !this.getValidationState('sample')) {
      this.props.uploadSample(this.state)
    } else {
      this.setState({errors: 'Select sample to upload'});
      this.setState({changed: true});
      this.getValidationState('sample');
    }

  };

  getValidationState(field) {
    if (!this.state.changed) {
      return null;
    }
    if (field === 'sample' && !this.state.sample) {
      return 'error';
    }

    return null;
  }

  handleDelete(i) {
    const tags = this.state.tags.slice(0);
    tags.splice(i, 1);
    this.setState({tags})
  }

  handleAddition(tag) {
    const tags = [].concat(this.state.tags, tag);
    this.setState({tags});
    this.setState({changed: true});
  }

  render() {
    const errors = this.state.errors || '';

    return (
      <div className="sample-upload-form">
        <h2>Upload new sample</h2>
        <br/>
        <Form onSubmit={this.onSubmit}>
          <FormGroup
            controlId="authUsername"
            validationState={this.getValidationState('sample')}
          >
            <ControlLabel>Sample (max. 20MB)</ControlLabel>
            <FormControl
              type="file"
              onChange={this.handleChange}
              name="sample"
            />
            <HelpBlock>{errors}</HelpBlock>
          </FormGroup>

          <FormGroup>
            <ControlLabel>Tags</ControlLabel>
            <ReactTags
              tags={this.state.tags}
              suggestions={this.props.allTags}
              handleDelete={this.handleDelete.bind(this)}
              handleAddition={this.handleAddition.bind(this)}
              allowNew={true}
              maxSuggestionsLength={15}
            />

          </FormGroup>
          {this.props.capabilities['ps'] ?
            <FormGroup>
              <Checkbox
                name="private"
                onChange={this.handleChange}
              >Private Sample</Checkbox>
            </FormGroup>
            : ''
          }
          <div style={{margin: '10px 0 20px'}}>
            By uploading a sample, you allow {SITE_NAME} to share the sample.
          </div>

          <Button type="submit" bsStyle="primary">Upload Sample</Button>
        </Form>
      </div>
    )
  }
}