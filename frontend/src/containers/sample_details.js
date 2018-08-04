import _ from 'lodash';
import React, {Component} from 'react';
import {connect} from 'react-redux';
import {Button, Label, Panel, Table} from 'react-bootstrap';
import ReactTags from 'react-tag-autocomplete';

import fileDownload from '../modules/file-download';
import {addTag, downloadSample, fetchAllTags, fetchSample, removeTag} from "../actions";
import PEImport from '../components/pe_import';
import MacroCodeStream from '../components/macro_code_stream';
import OleDirectoryEntry from '../components/ole_directory_entry';
import RtfObject from '../components/rtf_object';
import {isAuthenticated, username} from '../reducers'

import LoadingSpinner from '../components/loading_spinner';

class SampleDetails extends Component {

  constructor(props) {
    super(props);

    this.state = {
      tags: null,
      downloading: false
    };
  }

  componentDidMount() {
    this.props.fetchAllTags();
  }

  componentDidUpdate() {
    if (this.props.sample.sha2 !== this.props.sha2) {
      this.props.fetchSample(this.props.sha2);
    }
  }

  renderFileSize(fileSize) {
    if (fileSize < 1024) {
      return `${fileSize} Bytes`
    } else if (fileSize < 1024 * 1024) {
      return `${_.round(fileSize / 1024, 2)} KB`
    } else {
      return `${_.round(fileSize / 1024 / 1024, 2)} MB`
    }
  }

  renderTags(tag) {
    return (
      <span style={{fontSize: '1.3em'}} key={tag.name}>
        <Label bsStyle="default" bsClass="label block-label">
          {tag.name}
        </Label>
      </span>
    )
  }

  renderTrID(trid) {
    return (
      <p key={trid.format}>
        {trid.format} ({trid.match})
      </p>
    )
  }

  renderPEInfos(sample) {
    if (sample.analyzer_results.pefile) {
      const {data} = sample.analyzer_results.pefile;

      const header = data.Header;
      const sections = data.Sections;
      const imports = data.Imports;

      return (
        <div className="sample-pe-infos">
          <Panel id="pe-infos" defaultExpanded>
            <Panel.Heading>
              <Panel.Title toggle>PE Infos</Panel.Title>
            </Panel.Heading>
            <Panel.Collapse>
              <Panel.Body>
                <h4>Header</h4>
                <Table condensed className="sample-detail-table">
                  <tbody>
                  <tr>
                    <th>Target Machine</th>
                    <td>{header.TargetMachine}</td>
                  </tr>
                  <tr>
                    <th>Compilation Timestamp</th>
                    <td>{header.CompilationTimestamp}</td>
                  </tr>
                  <tr>
                    <th>Entry Point</th>
                    <td>{header.EntryPoint}</td>
                  </tr>
                  <tr>
                    <th>Contained Sections</th>
                    <td>{header.ContainedSections}</td>
                  </tr>
                  </tbody>
                </Table>
                <h4>Sections</h4>
                <Table condensed>
                  <thead>
                  <tr>
                    <th>Name</th>
                    <th>Virtual Address</th>
                    <th>Virtual Size</th>
                    <th>Raw Size</th>
                    <th>Entropy</th>
                    <th>MD5</th>
                  </tr>
                  </thead>
                  <tbody>
                  {sections.map(this.renderPESection)}
                  </tbody>
                </Table>
                <h4>Imports</h4>
                <Table condensed>
                  <tbody>
                  <tr>
                    <th>Imphash</th>
                    <td>{data.Imphash}</td>
                  </tr>
                  </tbody>
                </Table>
                {imports.map(this.renderImport)}
              </Panel.Body>
            </Panel.Collapse>
          </Panel>
        </div>
      )
    }
    return null;
  }


  renderPESection(section) {
    return (
      <tr key={section.VirtualAddress}>
        <td>{section.Name}</td>
        <td>{section.VirtualAddress}</td>
        <td>{section.VirtualSize}</td>
        <td>{section.RawSize}</td>
        <td>{_.round(section.Entropy, 2)}</td>
        <td>{section.MD5}</td>
      </tr>
    )
  }

  renderImport(dll) {
    return (
      <PEImport dll={dll} key={dll.Name}/>
    )
  }

  renderExifToolInfos(sample) {
    if (sample.analyzer_results.exiftool) {
      const {data} = sample.analyzer_results.exiftool;

      return (
        <div className="sample-exiftool-infos">
          <Panel id="exiftool-infos" defaultExpanded>
            <Panel.Heading>
              <Panel.Title toggle>ExifTool File Metadata</Panel.Title>
            </Panel.Heading>
            <Panel.Collapse>
              <Panel.Body>
                <Table condensed className="sample-detail-table">
                  <tbody>
                  {data.map(this.renderExifToolLine)}
                  </tbody>
                </Table>
              </Panel.Body>
            </Panel.Collapse>
          </Panel>
        </div>
      )
    }
    return null;
  }

  renderOLEInfos(sample) {
    if (sample.analyzer_results.oletools) {
      const {data} = sample.analyzer_results.oletools;
      const {macros, metadata, rtf_objects, directory_entries} = data;

      return (
        <div className="sample-ole-infos">
          <Panel id="ole-infos" defaultExpanded>
            <Panel.Heading>
              <Panel.Title toggle>OLE Infos</Panel.Title>
            </Panel.Heading>
            <Panel.Collapse>
              <Panel.Body>
                {
                  macros && macros.macro_analysis !== undefined && macros.macro_analysis.length > 0 ?
                    <div>
                      <h4>Commonly Abused Properties</h4>
                      <ul>
                        {this.containsMacroCharacteristic(macros.macro_analysis, "Document_open") ?
                          <li>Runs when document is opened</li> : null}
                        {this.containsMacroCharacteristic(macros.macro_analysis, "Shell") ?
                          <li>May run an executable file or a system command</li> : null}
                        {(this.containsMacroCharacteristic(macros.macro_analysis, "Chr")
                          || this.containsMacroCharacteristic(macros.macro_analysis, "Xor")
                          || this.containsMacroCharacteristic(macros.macro_analysis, "Base64 Strings")
                          || this.containsMacroCharacteristic(macros.macro_analysis, "Hex Strings")
                        )
                          ? <li>Seems to contain deobfuscation code</li> : null}
                      </ul>
                    </div> : null
                }

                {
                  macros && macros.extracted_macros !== undefined && macros.extracted_macros.length > 0 ?
                    <div>
                      <h4>Macros and VBA Code streams</h4>
                      {macros.extracted_macros.map(macro => (
                        <MacroCodeStream key={macro.vba_filename} macro={macro}/>))}

                    </div> : null
                }

                {
                  metadata !== undefined && metadata.SummaryInformation !== undefined ?
                    <div>
                      <h4>Summary Info</h4>
                      <Table condensed className="sample-detail-table">
                        <tbody>
                        <tr>
                          <th>Application Name</th>
                          <td>{metadata.SummaryInformation.creating_application}</td>
                        </tr>
                        <tr>
                          <th>Character Count</th>
                          <td>{metadata.SummaryInformation.num_chars}</td>
                        </tr>
                        <tr>
                          <th>Code Page</th>
                          <td>{metadata.SummaryInformation.codepage}</td>
                        </tr>
                        <tr>
                          <th>Creation Datetime</th>
                          <td>{metadata.SummaryInformation.create_time}</td>
                        </tr>
                        <tr>
                          <th>Edit Time</th>
                          <td>{metadata.SummaryInformation.total_edit_time}</td>
                        </tr>
                        <tr>
                          <th>Last Saved</th>
                          <td>{metadata.SummaryInformation.last_saved_time}</td>
                        </tr>
                        <tr>
                          <th>Page Count</th>
                          <td>{metadata.SummaryInformation.num_pages}</td>
                        </tr>
                        <tr>
                          <th>Revision Number</th>
                          <td>{metadata.SummaryInformation.revision_number}</td>
                        </tr>
                        <tr>
                          <th>Security</th>
                          <td>{metadata.SummaryInformation.security}</td>
                        </tr>
                        <tr>
                          <th>Template</th>
                          <td>{metadata.SummaryInformation.template}</td>
                        </tr>
                        <tr>
                          <th>Word Count</th>
                          <td>{metadata.SummaryInformation.num_words}</td>
                        </tr>
                        </tbody>
                      </Table>


                      <h4>Document Summary Info</h4>
                      <Table condensed className="sample-detail-table">
                        <tbody>
                        <tr>
                          <th>Characters With Spaces</th>
                          <td>{metadata.DocumentSummaryInformation.chars_with_spaces}</td>
                        </tr>
                        <tr>
                          <th>Code Page</th>
                          <td>{metadata.DocumentSummaryInformation.codepage_doc}</td>
                        </tr>
                        <tr>
                          <th>Hyperlinks Changed</th>
                          <td>{metadata.DocumentSummaryInformation.hlinks_changed}</td>
                        </tr>
                        <tr>
                          <th>Line Count</th>
                          <td>{metadata.DocumentSummaryInformation.lines}</td>
                        </tr>
                        <tr>
                          <th>Links Dirty</th>
                          <td>{metadata.DocumentSummaryInformation.links_dirty}</td>
                        </tr>
                        <tr>
                          <th>Paragraph Count</th>
                          <td>{metadata.DocumentSummaryInformation.paragraphs}</td>
                        </tr>
                        <tr>
                          <th>Scale</th>
                          <td>{metadata.DocumentSummaryInformation.scale_crop}</td>
                        </tr>
                        <tr>
                          <th>Shared Document</th>
                          <td>{metadata.DocumentSummaryInformation.shared_doc}</td>
                        </tr>
                        <tr>
                          <th>Version</th>
                          <td>{metadata.DocumentSummaryInformation.None}</td>
                        </tr>
                        </tbody>
                      </Table>

                    </div> : null
                }

                {
                  directory_entries !== undefined && directory_entries.length > 0 ?
                    <div>
                      <h4>OLE Streams</h4>
                      {directory_entries.map(data => <OleDirectoryEntry key={data.id} data={data}/>)}
                    </div> : null
                }

                {
                  rtf_objects && rtf_objects.length > 0 ?
                    <div>
                      <h4>RTF Objects</h4>
                      {rtf_objects.map(data => <RtfObject data={data}/>)}
                    </div> : null
                }

              </Panel.Body>
            </Panel.Collapse>
          </Panel>
        </div>
      )
    }
    return null;
  }


  containsMacroCharacteristic(macro_analysis, characteristic) {
    for (const ma of macro_analysis) {
      if (ma.keyword === characteristic)
        return true;
    }
    return false;

  }

  renderExifToolLine(exif_info) {
    return (
      <tr key={exif_info.key + exif_info.value}>
        <th>{exif_info.key}</th>
        <td>{exif_info.value}</td>
      </tr>
    )
  }

  handleDelete(i) {
    const existingTags = this.state.tags || this.props.sample.tags;
    const tags = existingTags.slice(0);
    const deletedTagName = tags[i].name;

    if (window.confirm(`Remove tag ${deletedTagName}`)) {
      tags.splice(i, 1);
      this.setState({tags});
      this.props.removeTag(deletedTagName, this.props.sample.sha2)
    }
  }

  handleAddition(tag) {
    const existingTags = this.state.tags || this.props.sample.tags;
    const tags = [].concat(existingTags, tag);
    this.setState({tags});
    this.props.addTag(tag.name, this.props.sample.sha2)
  }

  handleDownload(sha2) {
    if (!this.state.downloading) {
      this.setState({downloading: true});
      const request = downloadSample(sha2);
      request.then(data => {
        fileDownload(data.data, `${sha2}.zip`, 'application/zip');
        this.setState({downloading: false});
      }).catch(err => {
        if (err.response && err.response.status === 404) {
          alert("Ups! This sample escaped the farm...")
        } else if (err.response && err.response.status === 403) {
          alert("Error: Download Quota exceeded")
        } else {
          alert("Error: Something went wrong while fetching the sample. Try again later")
        }
      });
    }
  }

  render() {
    const sample = this.props.sample;

    if (this.props.errorMessage) {
      return null;
    }

    if (sample.sha2 !== this.props.sha2) {
      return <LoadingSpinner/>
    }

    const createDate = new Date(sample.create_date);

    return (
      <div className="main-view">
        <div className="sample-overview">
          <h3>Sample Details</h3>
          <Table>
            <tbody>
            <tr>
              <th>SHA-256</th>
              <td>{sample.sha2}</td>
            </tr>
            <tr>
              <th>File name</th>
              <td>{sample.original_filename}</td>
            </tr>
            <tr>
              <th>Submitted</th>
              <td>{createDate.toLocaleDateString()} {createDate.toLocaleTimeString()}</td>
            </tr>
            {sample.source && sample.source.name ?
              <tr>
                <th>Source</th>
                <td>{sample.source.name}</td>
              </tr>
              : null}
            {sample.vt_total ?
              <tr>
                <th>VT</th>
                <td><a href={sample.vt_permalink} target="_blank">{sample.vt_positives} / {sample.vt_total}</a></td>
              </tr>
              : null}
            {this.props.isAuthenticated
              ?
              <tr>
                <th>
                  <Button
                    disabled={this.state.downloading}
                    bsStyle="primary"
                    onClick={() => this.handleDownload(sample.sha2)}>
                    Download
                  </Button>
                </th>
                <td>
                  Password: infected
                </td>
              </tr>
              : <tr>
                <th>Download</th>
                <td>Log in to download sample</td>
              </tr>
            }
            </tbody>
          </Table>
        </div>
        <div className="sample-basic-properties">
          <Panel id="basic-properties" defaultExpanded>
            <Panel.Heading>
              <Panel.Title toggle>Basic Properties</Panel.Title>
            </Panel.Heading>
            <Panel.Collapse>
              <Panel.Body>
                <Table condensed className="sample-detail-table">
                  <tbody>
                  <tr>
                    <th>MD5</th>
                    <td>{sample.md5}</td>
                  </tr>
                  <tr>
                    <th>SHA-1</th>
                    <td>{sample.sha1}</td>
                  </tr>
                  <tr>
                    <th>Magic</th>
                    <td>{sample.magic}</td>
                  </tr>
                  <tr>
                    <th>SSDeep</th>
                    <td>{sample.ssdeep}</td>
                  </tr>
                  {sample.analyzer_results.trid ?
                    <tr>
                      <th>TRiD</th>
                      <td>{sample.analyzer_results.trid.data.map(this.renderTrID)}</td>
                    </tr>
                    : null}
                  <tr>
                    <th>File size</th>
                    <td>{this.renderFileSize(sample.size)}</td>
                  </tr>
                  </tbody>
                </Table>
              </Panel.Body>
            </Panel.Collapse>
          </Panel>
        </div>
        <div className="sample-tags">
          <Panel id="tags" defaultExpanded>
            <Panel.Heading>
              <Panel.Title toggle>Tags</Panel.Title>
            </Panel.Heading>
            <Panel.Collapse>
              <Panel.Body>
                {this.props.isAuthenticated && this.props.username === sample.uploader ?
                  <ReactTags
                    tags={this.state.tags || sample.tags}
                    suggestions={this.props.allTags}
                    handleDelete={this.handleDelete.bind(this)}
                    handleAddition={this.handleAddition.bind(this)}
                    allowNew={true}
                  />
                  :
                  <div>
                    {sample.tags.map(this.renderTags)}
                  </div>
                }
              </Panel.Body>
            </Panel.Collapse>
          </Panel>
        </div>
        {this.renderPEInfos(sample)}
        {this.renderOLEInfos(sample)}
        {this.renderExifToolInfos(sample)}

      </div>
    )
  }
}

function mapStateToProps(state) {
  return {
    sample: state.sample,
    isAuthenticated: isAuthenticated(state),
    username: username(state),
    errorMessage: state.errorMessage,
    allTags: state.tags
  };
}

export default connect(mapStateToProps, {fetchSample, fetchAllTags, addTag, removeTag})(SampleDetails)