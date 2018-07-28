import React from 'react';
import {Panel} from 'react-bootstrap';

import Navigation from './navigation';
import {API_ROOT_URL, SITE_NAME} from "../constants";

const AboutApiView = (props) => (
  <div className="main-view">
    <Navigation history={props.history}/>
    <h2>{SITE_NAME} API</h2>
    <p>{SITE_NAME} provides a REST API to access all services. You have to generate an Access Token in your Account
      Profile in order to use the API.</p>
    <h3>Documentation</h3>
    <p>
      An automatically generated documentation of the API is available at
      &nbsp;<a href={API_ROOT_URL} target="_blank">{API_ROOT_URL}</a>.
    </p>
    <h3>Sample API Client</h3>
    <p>
      An API Client for {SITE_NAME} written in Python is available on
      &nbsp;<a href="https://github.com/drbeni/malquarium" target="_blank" rel="noopener noreferrer">GitHub</a>.
    </p>
    <div style={{marginTop: '50px'}}>
      <Panel bsStyle="warning">
        <Panel.Heading>
          Sample Downloads
        </Panel.Heading>
        <Panel.Body>
          Samples are always downloaded as encrypted ZIP file with the password "infected", containing a single file
          with the SHA-256 as filename plus the extension guessed by TRiD. Your API client has to do the decryption if
          you want to further process the sample.
        </Panel.Body>
      </Panel>
    </div>
  </div>
);

export default AboutApiView