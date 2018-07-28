import {FORM_ERROR} from "../actions";

export default function (state = {}, action) {
  switch (action.type) {
    case FORM_ERROR:
      return action.payload.data;
    default:
      return state;
  }
}