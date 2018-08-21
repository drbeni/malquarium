import {FETCH_SAMPLE, LATEST_SAMPLES, SEARCH_SAMPLES} from "../actions";

export const searchSamples = (state = {}, action) => {
  switch (action.type) {
    case SEARCH_SAMPLES:
      const search_string = decodeURIComponent(decodeURIComponent(action.payload.search_string));
      return {...action.payload.data, search_string: search_string};
    default:
      return state;
  }
};

export const fetchSample = (state = {}, action) => {
  switch (action.type) {
    case FETCH_SAMPLE:
      return action.payload.data;
    default:
      return state;
  }
};

export const latestSamples = (state = [], action) => {
  switch (action.type) {
    case LATEST_SAMPLES:
      return action.payload.data;
    default:
      return state;
  }
};