import { connect } from 'react-redux';
import BondFuturesMonitor from './bond_futures_monitor';

const mapStateToProps = state => ({
    referenceData: state.referenceData,
    quotes: state.quotes
});

export default connect(mapStateToProps)(BondFuturesMonitor);