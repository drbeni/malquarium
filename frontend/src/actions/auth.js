import axios from 'axios';
import {push} from 'connected-react-router'
import {API_ERROR, HIDE_LOADING, SHOW_LOADING} from "./index";
import {authenticatedRequest} from "../auth/jwt";

export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGOUT = 'LOGOUT';
export const REGISTER_SUCCESS = 'REGISTER_SUCCESS';
export const REGISTER_FAILURE = 'REGISTER_FAILURE';

export const TOKEN_RECEIVED = 'TOKEN_RECEIVED';
export const TOKEN_FAILURE = 'TOKEN_FAILURE';

export const FETCH_PROFILE = 'FETCH_PROFILE';
const API_ROOT_URL = process.env.REACT_APP_API_ROOT_URL;
export const AUTH_URL = `${API_ROOT_URL}auth/token/`;


export function login(username, password) {
  const url = `${AUTH_URL}obtain/`;
  const request = axios.post(url, {username: username, password: password});

  return (dispatch) => {
    dispatch({type: SHOW_LOADING});
    request.then(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: LOGIN_SUCCESS, payload: data.data});
    }).catch(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: LOGIN_FAILURE, payload: data})
    })
  }
}

export function logout() {
  return {type: LOGOUT, payload: undefined}
}

export function register(email, password) {
  const url = `${API_ROOT_URL}auth/register/`;
  const request = axios.post(url, {email: email, password: password});

  return (dispatch) => {
    dispatch({type: SHOW_LOADING});
    request.then(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: REGISTER_SUCCESS, payload: data.data});
      dispatch(push('/activate'));
    }).catch(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: REGISTER_FAILURE, payload: data})
    })
  }
}


export function fetchProfile() {
  authenticatedRequest();
  const url = `${API_ROOT_URL}auth/profile/`;
  const request = axios.get(url);

  return (dispatch) => {
    dispatch({type: SHOW_LOADING});

    request.then(data => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: FETCH_PROFILE, payload: data.data})
    }).catch(err => {
      dispatch({type: HIDE_LOADING});
      dispatch({type: API_ERROR, error: err});
    });
  };
}

export function resetApiToken() {
  authenticatedRequest();

  const url = `${API_ROOT_URL}token/reset/`;
  const request = axios.post(url, {});

  return (dispatch) => {
    request.then(data => {
      dispatch({type: FETCH_PROFILE, payload: data.data})
    }).catch(err => {
      dispatch({type: API_ERROR, error: err});
    })
  }
}
