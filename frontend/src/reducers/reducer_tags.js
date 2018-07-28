import {FETCH_ALL_TAGS} from "../actions";

export default function (state = [], action) {
  switch (action.type) {
    case FETCH_ALL_TAGS:
      return action.payload.data;
    default:
      return state;
  }
}