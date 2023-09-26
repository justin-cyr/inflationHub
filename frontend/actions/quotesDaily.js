import { getTipsPrices, getOtrTsyQuotesWsj, getOtrTsyQuotesCnbc, getOtrTsyQuotesMw, getOtrTsyQuotesCme, getOtrTipsQuotesCnbc, getBondFuturesQuotesCme } from "../requests/quotesDaily";
import { decodePricingData } from "../protobuf/pricingData";

export const RECEIVE_TIPS_PRICES = 'RECEIVE_TIPS_PRICES';
export const RECEIVE_OTR_TIPS_QUOTES_CNBC = 'RECEIVE_OTR_TIPS_QUOTES_CNBC';

export const RECEIVE_OTR_TSY_QUOTES_WSJ = 'RECEIVE_OTR_TSY_QUOTES_WSJ';
export const RECEIVE_OTR_TSY_QUOTES_CNBC = 'RECEIVE_OTR_TSY_QUOTES_CNBC';
export const RECEIVE_OTR_TSY_QUOTES_MW = 'RECEIVE_OTR_TSY_QUOTES_MW';
export const RECEIVE_OTR_TSY_QUOTES_CME = 'RECEIVE_OTR_TSY_QUOTES_CME';
export const RECEIVE_BOND_FUTURES_QUOTES_CME = 'RECEIVE_BOND_FUTURES_QUOTES_CME';
export const RECEIVE_YF_WS_QUOTE = 'RECEIVE_YF_WS_QUOTE';

const quoteUpdateFreq = 10000;

const receiveTipsPrices = response => ({
    type: RECEIVE_TIPS_PRICES,
    response
});

const receiveOtrTipsQuotesCnbc = response => ({
    type: RECEIVE_OTR_TIPS_QUOTES_CNBC,
    response
});

const receiveOtrTsyQuotesWsj = response => ({
    type: RECEIVE_OTR_TSY_QUOTES_WSJ,
    response
});

const receiveOtrTsyQuotesCnbc = response => ({
    type: RECEIVE_OTR_TSY_QUOTES_CNBC,
    response
});

const receiveOtrTsyQuotesMw = response => ({
    type: RECEIVE_OTR_TSY_QUOTES_MW,
    response
});

const receiveOtrTsyQuotesCme = response => ({
    type: RECEIVE_OTR_TSY_QUOTES_CME,
    response
});

const receiveBondFuturesQuotesCme = response => ({
    type: RECEIVE_BOND_FUTURES_QUOTES_CME,
    response
});

const receiveYfWsQuote = response => ({
    type: RECEIVE_YF_WS_QUOTE,
    response
});

export const updateTipsPrices = () => dispatch => getTipsPrices()
    .then(response => dispatch(receiveTipsPrices(response)));

export const updateOtrTipsQuotesCnbc = () => dispatch => getOtrTipsQuotesCnbc()
    .then(response => dispatch(receiveOtrTipsQuotesCnbc(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTipsQuotesCnbc()), quoteUpdateFreq) });

export const updateOtrTsyQuotesWsj = () => dispatch => getOtrTsyQuotesWsj()
    .then(response => dispatch(receiveOtrTsyQuotesWsj(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesWsj()), quoteUpdateFreq) });

export const updateOtrTsyQuotesCnbc = () => dispatch => getOtrTsyQuotesCnbc()
    .then(response => dispatch(receiveOtrTsyQuotesCnbc(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesCnbc()), quoteUpdateFreq) });

export const updateOtrTsyQuotesMw = () => dispatch => getOtrTsyQuotesMw()
    .then(response => dispatch(receiveOtrTsyQuotesMw(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesMw()), quoteUpdateFreq) });

export const updateOtrTsyQuotesCme = () => dispatch => getOtrTsyQuotesCme()
    .then(response => dispatch(receiveOtrTsyQuotesCme(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesCme()), quoteUpdateFreq) });

export const updateBondFuturesQuotesCme = (dataName) => dispatch => getBondFuturesQuotesCme(dataName)
    .then(response => dispatch(receiveBondFuturesQuotesCme(response)))
    .then(() => { setTimeout(() => dispatch(updateBondFuturesQuotesCme(dataName)), quoteUpdateFreq) });

export const updateYfWsQuote = (e) => dispatch => decodePricingData(e.data)
    .then(response => dispatch(receiveYfWsQuote(response)));
