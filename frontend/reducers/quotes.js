import { RECEIVE_TIPS_PRICES, RECEIVE_OTR_TSY_QUOTES_WSJ, RECEIVE_OTR_TSY_QUOTES_CNBC } from "../actions/quotesDaily";

// default state
const _emptyState = {
    daily: { tipsPrices: { priceData: [] }, tsys: { otr: { wsj: {}, cnbc: {}, mw: {}, cme: {} } }}
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
        {
            const data = action.response.data;
            let newOtrTsys = {};

            // Update quotes for the first time or replace older quotes
            for (let record of data) {
                const quoteTime = new Date(record.timestamp)
                if (!(record.standardName in state.daily.tsys.otr.wsj) ||
                    (quoteTime > state.daily.tsys.otr.wsj[record.standardName].timestamp)) {
                    newOtrTsys[record.standardName] = {
                        price: Number(record.price),
                        priceChange: record.priceChange,
                        timestamp: quoteTime,
                        yield: Number(record.yield),
                        yieldChange: record.yieldChange
                    }
                }
                else {
                    // keep existing quote
                    newOtrTsys[record.standardName] = state.daily.tsys.otr.wsj[record.standardName];
                }
            }

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tsys: {
                        ...state.daily.tsys,
                        otr: {
                            ...state.daily.tsys.otr,
                            wsj: newOtrTsys
                        }
                    }
                }
            };
        }
        case RECEIVE_OTR_TSY_QUOTES_CNBC:
        {
            const data = action.response.data;
            let newOtrTsys = {};

            // Update quotes for the first time or replace older quotes
            for (let record of data) {
                const quoteTime = new Date(record.timestamp)
                if (!(record.standardName in state.daily.tsys.otr.cnbc) ||
                    (quoteTime > state.daily.tsys.otr.cnbc[record.standardName].timestamp)) {
                    newOtrTsys[record.standardName] = {
                        price: Number(record.price),
                        priceChange: record.priceChange,
                        timestamp: quoteTime,
                        yield: Number(record.yield),
                        yieldChange: record.yieldChange
                    }
                }
                else {
                    // keep existing quote
                    newOtrTsys[record.standardName] = state.daily.tsys.otr.cnbc[record.standardName];
                }
            }

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tsys: {
                        ...state.daily.tsys,
                        otr: {
                            ...state.daily.tsys.otr,
                            cnbc: newOtrTsys
                        }
                    }
                }
            };
        }

        default:
            return state;
    }
}
