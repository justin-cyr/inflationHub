import { getTipsPrices, getOtrTsyQuotesWsj, getOtrTsyQuotesCnbc } from "../requests/quotesDaily";

export const RECEIVE_TIPS_PRICES = 'RECEIVE_TIPS_PRICES';
export const RECEIVE_OTR_TSY_QUOTES_WSJ = "RECEIVE_OTR_TSY_QUOTES_WSJ";
export const RECEIVE_OTR_TSY_QUOTES_CNBC = "RECEIVE_OTR_TSY_QUOTES_CNBC";

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

export const updateTipsPrices = () => dispatch => getTipsPrices()
    .then(response => dispatch(receiveTipsPrices(response)));

export const updateOtrTsyQuotesWsj = () => dispatch => getOtrTsyQuotesWsj()
    .then(response => dispatch(receiveOtrTsyQuotesWsj(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesWsj()), quoteUpdateFreq) });

export const updateOtrTsyQuotesCnbc = () => dispatch => getOtrTsyQuotesCnbc()
    .then(response => dispatch(receiveOtrTsyQuotesCnbc(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesCnbc()), quoteUpdateFreq) });
