
import { combineReducers } from 'redux';

import quotesReducer from './quotes';
import referenceDataReducer from './referenceData';

export default combineReducers({
    quotes: quotesReducer,
    referenceData: referenceDataReducer
});
