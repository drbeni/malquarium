import jwtDecode from 'jwt-decode';
import * as auth from '../actions/auth';
import {clearToken, getAccessToken, getRefreshToken, saveToken} from "../auth/jwt";

const initialState = {
  access: {
    token: getAccessToken() || undefined
  },
  refresh: {
    token: getRefreshToken() || undefined
  },
  errors: {},
};

export default (state = initialState, action) => {
  switch (action.type) {
    case auth.LOGIN_SUCCESS:
      saveToken(action.payload);

      return {
        access: {
          token: action.payload.access,
          ...jwtDecode(action.payload.access)
        },
        refresh: {
          token: action.payload.refresh,
          ...jwtDecode(action.payload.refresh)
        },
        errors: {}
      };

    case auth.TOKEN_RECEIVED:
      saveToken(action.payload);

      return {
        ...state,
        refreshingToken: false,
        access: {
          token: action.payload.access,
          ...jwtDecode(action.payload.access)
        }
      };
    case auth.LOGIN_FAILURE:
    case auth.TOKEN_FAILURE:
      clearToken();

      return {
        access: undefined,
        refresh: undefined,
        errors:
        action.payload.response ||
        {'non_field_errors': action.payload.statusText},
      };
    case auth.LOGOUT:
      clearToken();
      return initialState;

    default:
      // parse token from localStorage if user reloaded page
      if (state.access && !state.access.exp && getAccessToken()) {
        return {
          ...state,
          access: {
            token: getAccessToken(),
            ...jwtDecode(getAccessToken())
          },
          refresh: {
            token: getRefreshToken(),
            ...jwtDecode(getRefreshToken())
          },
        }
      }

      return state
  }
}


export function refreshToken(state) {
  if (state && state.refresh) {
    return state.refresh.token
  }
  return getRefreshToken()
}

export function isRefreshTokenExpired(state) {
  let refresh = null;
  if (state && state.refresh && state.refresh.exp) {
    refresh = state.refresh;
  } else {
    const token = refreshToken(state);
    if (token) {
      refresh = jwtDecode(token);
    }
    return true;
  }

  return 1000 * refresh.exp - (new Date()).getTime() < 5000
}

export function isAuthenticated(state) {
  return !isRefreshTokenExpired(state)
}

const get_attribute_from_jwt = (state, attribute, default_value) => {
  if (state && state.refresh) {
    return state.refresh[attribute]
  } else {
    const token = refreshToken(state);
    if (token) {
      return jwtDecode(token)[attribute];
    }
    return default_value;
  }
};

export function username(state) {
  return get_attribute_from_jwt(state, 'username', null);
}

export function capabilities(state) {
  return get_attribute_from_jwt(state, 'capa', {});
}

export function errors(state) {
  return state.errors
}