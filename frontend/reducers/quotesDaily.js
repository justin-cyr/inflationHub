import { RECEIVE_TIPS_PRICES } from "../actions/quotesDaily";

// default state
const _emptyState = {
    quotes: { daily: {} }
}

// Daily quotes reducer
export default (state = _emptyState, action) => {
    Object.freeze(state);
    switch (action.type) {

        case RECEIVE_TIPS_PRICES:
            return Object.assign({}, { quotes: { daily: { ...state.quotes.daily, 'tipsPrices': action.response } }});
        
        default:
            return state;
    }
}
