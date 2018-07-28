import {SAMPLE_STATS} from "../actions";

export default function (state = {}, action) {
  switch (action.type) {
    case SAMPLE_STATS:
      return action.payload.data;
    default:
      return state;
  }
}