import { getTipsPrices, getOtrTsyQuotesWsj } from "../requests/quotesDaily";

export const RECEIVE_TIPS_PRICES = 'RECEIVE_TIPS_PRICES';
export const RECEIVE_OTR_TSY_QUOTES_WSJ = "RECEIVE_OTR_TSY_QUOTES_WSJ";

const receiveTipsPrices = response => ({
    type: RECEIVE_TIPS_PRICES,
    response
});

const receiveOtrTsyQuotesWsj = response => ({
    type: RECEIVE_OTR_TSY_QUOTES_WSJ,
    response
});

export const updateTipsPrices = () => dispatch => getTipsPrices()
    .then(response => dispatch(receiveTipsPrices(response)));

export const updateOtrTsyQuotesWsj = () => dispatch => getOtrTsyQuotesWsj()
    .then(response => dispatch(receiveOtrTsyQuotesWsj(response)))
    .then(() => { setTimeout(() => dispatch(updateOtrTsyQuotesWsj()), 10000) });
