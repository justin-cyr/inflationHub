import { RECEIVE_TIPS_PRICES, RECEIVE_OTR_TSY_QUOTES_WSJ } from "../actions/quotesDaily";

// default state
const _emptyState = {
    daily: { tipsPrices: { priceData: [] }, tsys: { otr: {} }}
}

// Daily quotes reducer
export default (state = _emptyState, action) => {
    Object.freeze(state);
    switch (action.type) {

        case RECEIVE_TIPS_PRICES:
            return {
                ...state,
                daily: {
                    ...state.daily,
                    tipsPrices: {
                        ...state.daily.tipsPrices,
                        priceData: action.response.priceData
                    } 
                }
            };
        
        case RECEIVE_OTR_TSY_QUOTES_WSJ:
            const data = action.response.data;
            let newOtrTsys = {};

            // Update quotes for the first time or replace older quotes
            for (let record of data) {
                const quoteTime = new Date(record.timestamp)
                if (!state.daily.tsys.otr[record.standardName] ||
                    (quoteTime > state.daily.tsys.otr[record.standardName].timestamp)) {
                    newOtrTsys[record.standardName] = {
                        price: record.price,
                        priceChange: record.priceChange,
                        timestamp: quoteTime,
                        yield: record.yield,
                        yieldChange: record.yieldChange
                    }
                }
                else {
                    // keep existing quote
                    newOtrTsys = state.daily.tsys.otr;
                }
            }

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tsys: {
                        ...state.daily.tsys,
                        otr: newOtrTsys
                    }
                }
            };
            

        default:
            return state;
    }
}
