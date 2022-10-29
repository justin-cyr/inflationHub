import { connect } from 'react-redux';
import { updateTipsPrices, updateOtrTsyQuotesWsj, updateOtrTsyQuotesCnbc } from '../../actions/quotesDaily';
import { updateTipsCusips, updateTipsRefData, updateTsyRefData } from '../../actions/referenceData';
import StateLoader from './state_loader';

const mapStateToProps = state => ({
    referenceData: state.referenceData
});

const mapDispatchToProps = dispatch => ({
    updateTipsPrices: () => dispatch(updateTipsPrices()),
    updateOtrTsyQuotesWsj: () => dispatch(updateOtrTsyQuotesWsj()),
    updateOtrTsyQuotesCnbc: () => dispatch(updateOtrTsyQuotesCnbc()),
    updateTipsCusips: () => dispatch(updateTipsCusips()),
    updateTipsRefData: cusip => dispatch(updateTipsRefData(cusip)),
    updateTsyRefData: () => dispatch(updateTsyRefData())
});

export default connect(mapStateToProps, mapDispatchToProps)(StateLoader);
