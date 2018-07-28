import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Button} from 'react-bootstrap';

import {searchSamples} from '../actions';

class SearchBar extends Component {
  constructor(props) {
    super(props);

    this.state = {search_string: ''};

    this.onInputChange = this.onInputChange.bind(this);
    this.onFormSubmit = this.onFormSubmit.bind(this);
  }

  onInputChange(event) {
    this.setState({search_string: event.target.value});
  }

  onFormSubmit(event) {
    event.preventDefault();

    if (this.state.search_string.length > 1) {
      this.props.searchSamples(this.state.search_string);
      this.setState({search_string: ''});
    }

    this.props.history.push('/samples/');
  }

  render() {
    return (
      <div className="search-bar">
        <form onSubmit={this.onFormSubmit} className="input-group">
          <input
            placeholder="Search for hashes or tags"
            className="form-control"
            value={this.state.search_string}
            onChange={this.onInputChange}
          />
          <span className="input-group-btn">
          <Button bsStyle="primary" type="submit">Search</Button>
        </span>
        </form>
      </div>
    );
  }
}


export default connect(null, {searchSamples})(SearchBar);