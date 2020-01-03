import axios from 'axios';
import {push} from 'connected-react-router'
import {anonymousRequest, authenticatedRequest} from '../auth/jwt';
import {API_ROOT_URL} from "../constants";

export const FETCH_SAMPLE = 'FETCH_SAMPLE';
export const SEARCH_SAMPLES = 'SEARCH_SAMPLES';
export const LATEST_SAMPLES = 'LATEST_SAMPLES';
export const SAMPLE_STATS = 'SAMPLE_STATS';
export const FETCH_ALL_TAGS = 'FETCH_ALL_TAGS';
export const ADD_TAG_TO_SAMPLE = 'ADD_TAG_TO_SAMPLE';
export const REMOVE_TAG_FROM_SAMPLE = 'REMOVE_TAG_FROM_SAMPLE';

export const SHOW_LOADING = 'SHOW_LOADING';
export const HIDE_LOADING = 'HIDE_LOADING';

export const FORM_ERROR = 'FORM_ERROR';
export const API_ERROR = 'API_ERROR';
export const RESET_ERROR_MESSAGE = 'RESET_ERROR_MESSAGE';

export function searchSamples(search_string, page = 1) {
  anonymousRequest();
  search_string = encodeURIComponent(encodeURIComponent(search_string));

  const url = `${API_ROOT_URL}query/${search_string}/?page=${page}`;
  const request = axios.get(url);

  return (dispatch) => {
    dispatch({type: SHOW_LOADING});
    request.then(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: SEARCH_SAMPLES, payload: {...data, search_string: search_string}})
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    });
  };
}

export function fetchSample(sha2) {
  anonymousRequest();
  const url = `${API_ROOT_URL}samples/${sha2}/`;
  const request = axios.get(url);

  return (dispatch) => {
    request.then(data => {
      dispatch({type: FETCH_SAMPLE, payload: data});
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    });
  };
}

export function downloadSample(sha2) {
  authenticatedRequest();
  const url = `${API_ROOT_URL}samples/download/zip/${sha2}/`;
  return axios.request({
    responseType: 'arraybuffer',
    url: url,
    method: 'get'
  });
}

export function uploadSample(values) {
  authenticatedRequest();
  const url = `${API_ROOT_URL}samples/`;

  const formData = new FormData();
  formData.append('file', values.sample);
  formData.append('tags', values.tags.map(tag => tag.name));
  formData.append('private', values.private);
  const config = {
    headers: {
      'content-type': 'multipart/form-data'
    }
  };

  const request = axios.post(url, formData, config);

  return (dispatch) => {
    dispatch({type: SHOW_LOADING});
    request.then(data => {
      dispatch({type: HIDE_LOADING});
      dispatch(push(`/samples/${data.data.sha2}`));
    }).catch(err => {
      if (err.response && err.response.status === 401) {
        dispatch(push('/login'));
        dispatch({type: HIDE_LOADING});
      } else {
        dispatch({type: HIDE_LOADING});
        dispatch({type: API_ERROR, error: err});
      }
    })
  }
}

export function getSampleStats() {
  anonymousRequest();
  const url = `${API_ROOT_URL}samples/stats/`;
  const request = axios.get(url);

  return (dispatch) => {
    request.then(data => {
      dispatch({type: SAMPLE_STATS, payload: data});
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    });
  };
}


export function getLatestSamples() {
  anonymousRequest();

  const url = `${API_ROOT_URL}samples/feed/10/`;
  const request = axios.get(url);

  return (dispatch) => {
    dispatch({type: SHOW_LOADING});
    request.then(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: LATEST_SAMPLES, payload: data});
    }).catch(err => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: API_ERROR, error: err});
    });
  };
}

// Resets the currently visible error message.
export const resetErrorMessage = () => ({
  type: RESET_ERROR_MESSAGE
});

export function fetchAllTags() {
  anonymousRequest();
  const url = `${API_ROOT_URL}tags/`;
  const request = axios.get(url);

  return (dispatch) => {
    request.then(data => {
      dispatch({type: FETCH_ALL_TAGS, payload: data})
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    });
  };
}

export function addTag(tag, sample_sha2) {
  authenticatedRequest();
  const url = `${API_ROOT_URL}tags/add/${tag}/${sample_sha2}/`;
  const request = axios.post(url, {});

  return (dispatch) => {
    request.then(data => {
      dispatch({type: ADD_TAG_TO_SAMPLE, payload: data})
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    });
  };
}

export function removeTag(tag, sample_sha2) {
  authenticatedRequest();
  const url = `${API_ROOT_URL}tags/remove/${tag}/${sample_sha2}/`;
  const request = axios.post(url, {});

  return (dispatch) => {
    request.then(data => {
      dispatch({type: REMOVE_TAG_FROM_SAMPLE, payload: data})
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    });
  };
}
