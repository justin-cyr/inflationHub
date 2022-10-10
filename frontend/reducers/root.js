
import { combineReducers } from 'redux';

import quotesDailyReducer from './quotesDaily';
import referenceDataReducer from './referenceData';

export default combineReducers({
    quotesDaily: quotesDailyReducer,
    referenceData: referenceDataReducer
});
