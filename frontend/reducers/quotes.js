import { RECEIVE_TIPS_PRICES, RECEIVE_OTR_TIPS_QUOTES_CNBC, RECEIVE_OTR_TSY_QUOTES_WSJ, RECEIVE_OTR_TSY_QUOTES_CNBC, RECEIVE_OTR_TSY_QUOTES_MW, RECEIVE_OTR_TSY_QUOTES_CME } from "../actions/quotesDaily";

// default state
const _emptyState = {
    daily: {
        tipsPrices: { priceData: [] },
        tips: { otr: { cnbc: {} } },
        tsys: { otr: { wsj: {}, cnbc: {}, mw: {}, cme: {} } }
    }
}

// helper for updating OTR quotes
const newOtrTsyQuotes = (currentOtrTsys, responseData) => {
    const data = responseData;
    let newOtrTsys = {};

    // Update quotes for the first time or replace older quotes
    for (let record of data) {
        const quoteTime = new Date(record.timestamp);
        if (!(record.standardName in currentOtrTsys) ||
            (quoteTime > currentOtrTsys[record.standardName].timestamp)) {

            let priceChange = 0;
            let yieldChange = 0;
            if (record.standardName in currentOtrTsys) {
                priceChange = record.price - currentOtrTsys[record.standardName].price;
                yieldChange = record.yield - currentOtrTsys[record.standardName].yield;
            }

            newOtrTsys[record.standardName] = {
                price: Number(record.price),
                priceChange: priceChange,
                timestamp: quoteTime,
                yield: Number(record.yield),
                yieldChange: yieldChange
            }
        }
        else {
            // keep existing quote
            newOtrTsys[record.standardName] = currentOtrTsys[record.standardName];

            if (quoteTime.getTime() === currentOtrTsys[record.standardName].timestamp.getTime()) {
                // set changes back to 0
                newOtrTsys[record.standardName].priceChange = 0;
                newOtrTsys[record.standardName].yieldChange = 0;
            }
        }
    }

    return newOtrTsys;
};

const newOtrTsyQuotesCme = (currentOtrTsys, responseData) => {
    const data = responseData;
    let newOtrTsys = {};

    // Update quotes for the first time or replace older quotes
    for (let record of data) {
        const quoteTime = new Date(record.timestamp);
        if (!(record.standardName in currentOtrTsys) ||
            (quoteTime > currentOtrTsys[record.standardName].timestamp)) {

            let priceChange = 0;
            if (record.standardName in currentOtrTsys) {
                priceChange = record.price - currentOtrTsys[record.standardName].price;
            }

            newOtrTsys[record.standardName] = {
                price: Number(record.price),
                priceChange: priceChange,
                displayPrice: record.displayPrice,
                timestamp: quoteTime,
                volume: record.volume
            }
        }
        else {
            // keep existing quote
            newOtrTsys[record.standardName] = currentOtrTsys[record.standardName];

            if (quoteTime.getTime() === currentOtrTsys[record.standardName].timestamp.getTime()) {
                // set changes back to 0
                newOtrTsys[record.standardName].priceChange = 0;
            }
        }
    }

    return newOtrTsys;
};

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
        
        case RECEIVE_OTR_TIPS_QUOTES_CNBC:
        {
            const newOtrTips = newOtrTsyQuotes(state.daily.tips.otr.cnbc, action.response.data);

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tips: {
                        ...state.daily.tips,
                        otr: {
                            ...state.daily.tips.otr,
                            cnbc: newOtrTips
                        }
                    }
                }
            };
        }

        case RECEIVE_OTR_TSY_QUOTES_WSJ:
        {
            const newOtrTsys = newOtrTsyQuotes(state.daily.tsys.otr.wsj, action.response.data);

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
            const newOtrTsys = newOtrTsyQuotes(state.daily.tsys.otr.cnbc, action.response.data);

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

        case RECEIVE_OTR_TSY_QUOTES_MW:
        {
            const newOtrTsys = newOtrTsyQuotes(state.daily.tsys.otr.mw, action.response.data);

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tsys: {
                        ...state.daily.tsys,
                        otr: {
                            ...state.daily.tsys.otr,
                            mw: newOtrTsys
                        }
                    }
                }
            };
        }

        case RECEIVE_OTR_TSY_QUOTES_CME:
        {
            const newOtrTsys = newOtrTsyQuotesCme(state.daily.tsys.otr.cme, action.response.data);

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tsys: {
                        ...state.daily.tsys,
                        otr: {
                            ...state.daily.tsys.otr,
                            cme: newOtrTsys
                        }
                    }
                }
            };
        }

        default:
            return state;
    }
}