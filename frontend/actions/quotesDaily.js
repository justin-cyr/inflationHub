import { getTipsPrices, getOtrTsyQuotesWsj, getOtrTsyQuotesCnbc, getOtrTsyQuotesMw } from "../requests/quotesDaily";

export const RECEIVE_TIPS_PRICES = 'RECEIVE_TIPS_PRICES';
export const RECEIVE_OTR_TSY_QUOTES_WSJ = 'RECEIVE_OTR_TSY_QUOTES_WSJ';
export const RECEIVE_OTR_TSY_QUOTES_CNBC = 'RECEIVE_OTR_TSY_QUOTES_CNBC';
export const RECEIVE_OTR_TSY_QUOTES_MW = 'RECEIVE_OTR_TSY_QUOTES_MW';

const quoteUpdateFreq = 10000;

const receiveTipsPrices = response => ({
    type: RECEIVE_TIPS_PRICES,
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

export const updateTipsPrices = () => dispatch => getTipsPrices()
    .then(response => dispatch(receiveTipsPrices(response)));

export const updateOtrTsyQuotesWsj = () => dispatch => getOtrTsyQuotesWsj()
    .then(response => dispatch(receiveOtrTsyQuotesWsj(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesWsj()), quoteUpdateFreq) });

export const updateOtrTsyQuotesCnbc = () => dispatch => getOtrTsyQuotesCnbc()
    .then(response => dispatch(receiveOtrTsyQuotesCnbc(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesCnbc()), quoteUpdateFreq) });

export const updateOtrTsyQuotesMw = () => dispatch => getOtrTsyQuotesMw()
    .then(response => dispatch(receiveOtrTsyQuotesMw(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesMw()), quoteUpdateFreq) });
