import axios from "axios/index";

import {AUTH_URL} from "../actions/auth";

export const ACCESS_TOKEN_NAME = 'jwtAccessToken';
export const REFRESH_TOKEN_NAME = 'jwtRefreshToken';
const TOKEN_REFRESH_URL = 'api/auth/token/refresh/';

export const authenticatedRequest = () => {
  axios.defaults.headers.common['Authorization'] = `Bearer ${getAccessToken()}`;

  axios.interceptors.response.use(undefined, function (err) {
    if (err.response && err.response.status === 401 && err.config && !err.config.url.endsWith(TOKEN_REFRESH_URL)) {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw(err);
      }

      const url = `${AUTH_URL}refresh/`;
      const request = axios.post(url, {refresh: refreshToken});

      return request
        .then(function (success) {
          saveToken(success.data);

          err.config.headers.Authorization = `Bearer ${getAccessToken()}`;
          return axios(err.config);
        })
        .catch(function (error) {
          clearToken();
          throw err;
        });
    }
    throw err;
  });
};


export const anonymousRequest = () => {
  if (!getRefreshToken()) {
    delete axios.defaults.headers.common['Authorization']
  } else {
    authenticatedRequest();
  }
};

export const getAccessToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_NAME);
};


export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_NAME);
};

export const saveToken = (data) => {
  localStorage.setItem(ACCESS_TOKEN_NAME, data.access);

  if (data.refresh) {
    localStorage.setItem(REFRESH_TOKEN_NAME, data.refresh);
  }
};

export const clearToken = () => {
  localStorage.removeItem(ACCESS_TOKEN_NAME);
  localStorage.removeItem(REFRESH_TOKEN_NAME);
};