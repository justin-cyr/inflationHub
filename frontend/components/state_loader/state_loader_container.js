import { connect } from 'react-redux';
import { updateTipsPrices, updateOtrTipsQuotesCnbc, updateOtrTsyQuotesWsj, updateOtrTsyQuotesCnbc, updateOtrTsyQuotesMw, updateOtrTsyQuotesCme } from '../../actions/quotesDaily';
import { updateTipsCusips, updateTipsRefData, updateTsyRefData } from '../../actions/referenceData';
import StateLoader from './state_loader';

const mapStateToProps = state => ({
    referenceData: state.referenceData
});

const mapDispatchToProps = dispatch => ({
    updateTipsPrices: () => dispatch(updateTipsPrices()),
    updateOtrTipsQuotesCnbc: () => dispatch(updateOtrTipsQuotesCnbc()),
    updateOtrTsyQuotesWsj: () => dispatch(updateOtrTsyQuotesWsj()),
    updateOtrTsyQuotesCnbc: () => dispatch(updateOtrTsyQuotesCnbc()),
    updateOtrTsyQuotesMw: () => dispatch(updateOtrTsyQuotesMw()),
    updateOtrTsyQuotesCme: () => dispatch(updateOtrTsyQuotesCme()),
    updateTipsCusips: () => dispatch(updateTipsCusips()),
    updateTipsRefData: cusip => dispatch(updateTipsRefData(cusip)),
    updateTsyRefData: () => dispatch(updateTsyRefData())
});

export default connect(mapStateToProps, mapDispatchToProps)(StateLoader);
