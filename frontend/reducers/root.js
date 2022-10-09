
import { combineReducers } from 'redux';

import quotesDailyReducer from './quotesDaily';

export default combineReducers({
    quotesDaily: quotesDailyReducer
});
