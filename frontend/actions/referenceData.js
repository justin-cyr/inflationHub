import { getTipsCusips, getTipsRefData, getTsyRefData } from "../requests/referenceData";

export const RECEIVE_TIPS_CUSIPS = 'RECEIVE_TIPS_CUSIPS';
export const RECEIVE_TIPS_REF_DATA = 'RECEIVE_TIPS_REF_DATA';
export const RECEIVE_TSY_REF_DATA = 'RECEIVE_TSY_REF_DATA';

const receiveTipsCusips = response => ({
    type: RECEIVE_TIPS_CUSIPS,
    response
})

const receiveTipsRefData = response => ({
    type: RECEIVE_TIPS_REF_DATA,
    response
});

const receiveTsyRefData = response => ({
    type: RECEIVE_TSY_REF_DATA,
    response
});

export const updateTipsCusips = () => dispatch => getTipsCusips()
    .then(response => dispatch(receiveTipsCusips(response)));

export const updateTipsRefData = cusip => dispatch => getTipsRefData(cusip)
    .then(response => dispatch(receiveTipsRefData(response)));

export const updateTsyRefData = cusip => dispatch => getTsyRefData(cusip)
    .then(response => dispatch(receiveTsyRefData(response)));
