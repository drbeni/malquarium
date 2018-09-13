import React, {Component} from 'react';
import {Link} from 'react-router-dom';
import {Label, Table} from 'react-bootstrap';


class SampleList extends Component {
  constructor(props) {
    super(props);

    this.renderSample = this.renderSample.bind(this);
  }

  renderTags(tag) {
    return (
      <Label bsStyle="default" bsClass="label block-label" key={tag.name}>
        {tag.name}
      </Label>
    )
  }

  renderSample(sample, hasMatchScores) {
    const date = new Date(sample.create_date);

    return (
      <tr key={sample.sha2}>
        <td>
          {date.toLocaleDateString()} {date.toLocaleTimeString()}
        </td>
        <td>
          <Link to={`/samples/${sample.sha2}`}>{sample.sha2}</Link>
        </td>
        <td>
          {sample.tags.map(this.renderTags)}
        </td>
        <td>
          {sample.source}
        </td>
        <td>
          {sample.vt_result}
        </td>
        {hasMatchScores ?
        <td>
          {sample.match_score}%
        </td>
        :null }
      </tr>
    );
  }

  render() {
    const samples = this.props.samples;
    let hasMatchScores = false;
    
    for (const sample of samples){
      if (sample.match_score !== undefined){
        hasMatchScores = true;
        break;
      }
    }

    return (
      <div className="sample-list">
        <Table responsive>
          <thead>
          <tr>
            <th style={{width: '10%'}}>Submitted</th>
            <th style={{width: '40%'}}>SHA-256</th>
            <th style={{width: '30%'}}>Tags</th>
            <th style={{width: '10%'}}>Source</th>
            <th style={{width: '10%'}}>VT</th>
            {hasMatchScores ?
              <th style={{width: '10%'}}>Match</th>
              : null
            }
          </tr>
          </thead>
          <tbody>
          {samples.map(s => this.renderSample(s, hasMatchScores))}
          </tbody>
        </Table>
      </div>
    );
  }
}

export default SampleList;