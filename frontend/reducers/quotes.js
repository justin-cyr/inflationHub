import { RECEIVE_TIPS_PRICES, RECEIVE_TIPS_PRICES_MW, RECEIVE_OTR_TIPS_QUOTES_CNBC, RECEIVE_OTR_TSY_QUOTES_WSJ, RECEIVE_OTR_TSY_QUOTES_CNBC, RECEIVE_OTR_TSY_QUOTES_MW, RECEIVE_OTR_TSY_QUOTES_CME, RECEIVE_BOND_FUTURES_QUOTES_CME, RECEIVE_YF_WS_QUOTE, RECEIVE_CTD_OTR_TABLE_CME } from "../actions/quotesDaily";

// default state
const _emptyState = {
    daily: {
        tipsPrices: { priceData: [] },
        tips: { otr: { cnbc: {} }, byCusip: {} },
        tsys: { otr: { wsj: {}, cnbc: {}, mw: {}, cme: {} } },
        ctdOtrTable: [],
        futures: {},
        yfQuotes: {}
    }
}

// helper for updating OTR quotes
const newOtrTsyQuotes = (currentOtrTsys, responseData) => {
    const data = responseData;
    let newOtrTsys = currentOtrTsys;

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
    let newOtrTsys = currentOtrTsys;

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

const newBondFuturesQuotesCme = (currentFutures, responseData) => {
    const data = responseData;
    let newFutures = currentFutures;

    // Update quotes for the first time or replace older quotes
    for (let record of data) {
        const quoteTime = new Date(record.timestamp);
        if (!(record.dataName in currentFutures) || !(record.ticker in currentFutures[record.dataName]) ||
            (quoteTime > currentFutures[record.dataName][record.ticker].timestamp)) {
            
            let priceChange = 0;
            if ((record.dataName in currentFutures) && (record.ticker in currentFutures[record.dataName]) && record.price != '-') {
                priceChange = record.price - currentFutures[record.dataName][record.ticker].price;
            }

            newFutures[record.dataName] = {
                ...newFutures[record.dataName],
                [record.ticker]: {
                    price: record.price,
                    priceChange: priceChange,
                    productName: record.productName,
                    timestamp: quoteTime,
                    volume: record.volume,
                    last: record.last,
                    priorSettle: record.priorSettle,
                    ticker: record.ticker,
                    standardName: record.standardName,
                    month: record.month,
                    expirationDate: record.expirationDate
                } 
            }
        }
        else {
            // keep existing quote
            newFutures[record.dataName][record.ticker] = currentFutures[record.dataName][record.ticker];
            if (quoteTime.getTime() === currentFutures[record.dataName][record.ticker].timestamp.getTime()) {
                // set changes back to 0
                newFutures[record.dataName][record.ticker].priceChange = 0;
            }
        }
    }

    return newFutures;
};

const newCtdOtrTable = (currentCtdOtrTable, responseData) => {

    if (currentCtdOtrTable.length === 0) {
        return responseData;
    }

    let newCtdOtrTabe = currentCtdOtrTable;

    for (let record of responseData) {
        for (let i = 0; i < newCtdOtrTabe.length; ++i) {
            let existingRecord = newCtdOtrTabe[i];
            if (record.futureTicker === existingRecord.futureTicker) {
                const yieldChange = existingRecord.fwdYield - record.fwdYield;
                if (yieldChange !== 0) {
                    existingRecord = record;
                }
                existingRecord.yieldChange = yieldChange;
            }
        }
    }

    return newCtdOtrTabe;
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
        
        case RECEIVE_TIPS_PRICES_MW:
        {
            const newTipsPricesByCusip = newOtrTsyQuotes(state.daily.tips.byCusip, action.response.data);

            return {
                ...state,
                daily: {
                    ...state.daily,
                    tips: {
                        ...state.daily.tips,
                        byCusip: {
                            ...state.daily.tips.byCusip,
                            ...newTipsPricesByCusip
                        }
                    }
                }
            };
        }

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

        case RECEIVE_BOND_FUTURES_QUOTES_CME:
        {
            const newFutures = newBondFuturesQuotesCme(state.daily.futures, action.response.data);

            return {
                ...state,
                daily: {
                    ...state.daily,
                    futures: newFutures
                }
            };
        }

        case RECEIVE_YF_WS_QUOTE:
        {
            const ticker = action.response.id;

            return {
                ...state,
                daily: {
                    ...state.daily,
                    yfQuotes: {
                        ...state.daily.yfQuotes,
                        [ticker]: action.response
                    }
                }
            }
        }

        case RECEIVE_CTD_OTR_TABLE_CME:
        {
            const newCtds = newCtdOtrTable(state.daily.ctdOtrTable, action.response.data);

            return {
                ...state,
                daily: {
                    ...state.daily,
                    ctdOtrTable: newCtds
                }
            }
        }

        default:
            return state;
    }
}
