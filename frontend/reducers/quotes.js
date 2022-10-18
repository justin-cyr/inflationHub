import { RECEIVE_TIPS_PRICES } from "../actions/quotesDaily";

// default state
const _emptyState = {
    daily: { tipsPrices: { priceData: [] }}
}

// Daily quotes reducer
export default (state = _emptyState, action) => {
    Object.freeze(state);
    switch (action.type) {

        case RECEIVE_TIPS_PRICES:
            return {
                ...state,
                daily: { ...state.daily,
                    tipsPrices: {
                        ...state.daily.tipsPrices,
                        priceData: action.response.priceData
                    } 
                }
            };
        
        default:
            return state;
    }
}
