import { RECEIVE_TIPS_CUSIPS, RECEIVE_TIPS_REF_DATA, RECEIVE_TSY_REF_DATA } from "../actions/referenceData";

// default state
const _emptyState = {
    tips: { cusips: [], otr: {}, bonds: {} },
    tsys: { cusips: [], otr: {}, bonds: {} },
}

// Reference data reducer
export default (state = _emptyState, action) => {
    Object.freeze(state);
    switch (action.type) {

        case RECEIVE_TIPS_CUSIPS:
            return {
                ...state,
                tips: {
                    ...state.tips,
                    cusips: action.response.cusips
                }
            };
        
        case RECEIVE_TIPS_REF_DATA:
            const cusip = action.response.referenceData.cusip;
            return {
                ...state,
                tips: {
                    ...state.tips,
                    bonds: {
                        ...state.tips.bonds,
                        [cusip]: action.response.referenceData
                    }
                }
            };

        case RECEIVE_TSY_REF_DATA:
            return {
                ...state,
                tsys: {
                    ...state.tsys,
                    cusips: action.response.referenceData.cusips,
                    bonds: action.response.referenceData.bonds
                }
            }

        default:
            return state;
    }
}
