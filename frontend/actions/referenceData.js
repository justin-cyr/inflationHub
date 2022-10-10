import { getTipsCusips, getTipsRefData } from "../requests/referenceData";

export const RECEIVE_TIPS_CUSIPS = 'RECEIVE_TIPS_CUSIPS';
export const RECEIVE_TIPS_REF_DATA = 'RECEIVE_TIPS_REF_DATA';

const receiveTipsCusips = response => ({
    type: RECEIVE_TIPS_CUSIPS,
    response
})

const receiveTipsRefData = response => ({
    type: RECEIVE_TIPS_REF_DATA,
    response
});

export const updateTipsCusips = () => dispatch => getTipsCusips()
    .then(response => dispatch(receiveTipsCusips(response)));

export const updateTipsRefData = cusip => dispatch => getTipsRefData(cusip)
    .then(response => dispatch(receiveTipsRefData(response)));
