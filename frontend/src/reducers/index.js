import {combineReducers} from 'redux';
import {connectRouter, LOCATION_CHANGE} from 'connected-react-router'
import {reducer as formReducer} from 'redux-form';

import auth, * as fromAuth from './reducer_auth';
import ProfileReducer from './reducer_profile';
import {fetchSample, latestSamples, searchSamples} from './reducer_samples';
import StatsReducer from './reducer_stats';
import TagReducer from './reducer_tags';
import FormErrors from './reducer_form_errors';
import {HIDE_LOADING, RESET_ERROR_MESSAGE, SHOW_LOADING} from "../actions";

const errorMessage = (state = null, action) => {
  const {type, error} = action;

  if (type === RESET_ERROR_MESSAGE || type === HIDE_LOADING || type === LOCATION_CHANGE) {
    return null
  } else if (error) {
    if (error.response && error.response.data && error.response.data.details)
      return error.response.data.details;
    if (error.message !== undefined)
      return error.message;
  }

  return state
};

const showLoadingSpinner = (state = null, action) => {
  switch (action.type) {
    case SHOW_LOADING:
      return true;
    case HIDE_LOADING:
      return null;
    default:
      return state;
  }
};

const urlHistory = (state = [], action) => {
  if (action.type === LOCATION_CHANGE) {
    return [action.payload.pathname].concat(state.slice(0, 5));
  } else {
    return state;
  }
};

const rootReducer = history => combineReducers({
  auth: auth,
  profile: ProfileReducer,
  samples: searchSamples,
  sample: fetchSample,
  latestSamples: latestSamples,
  stats: StatsReducer,
  tags: TagReducer,
  form: formReducer,
  errorMessage: errorMessage,
  formErrors: FormErrors,
  urlHistory: urlHistory,
  showLoadingSpinner: showLoadingSpinner,
  router: connectRouter(history),
});

export const isAuthenticated = state => fromAuth.isAuthenticated(state.auth);
export const authErrors = state => fromAuth.errors(state.auth);
export const username = state => fromAuth.username(state.auth);
export const capabilities = state => fromAuth.capabilities(state.auth);

export default rootReducer;
