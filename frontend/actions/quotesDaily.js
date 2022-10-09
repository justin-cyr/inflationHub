import { getTipsPrices } from "../requests/quotesDaily";

export const RECEIVE_TIPS_PRICES = 'RECEIVE_TIPS_PRICES';

const receiveTipsPrices = response => ({
    type: RECEIVE_TIPS_PRICES,
    response
});

export const updateTipsPrices = () => dispatch => getTipsPrices()
    .then(response => dispatch(receiveTipsPrices(response)));
