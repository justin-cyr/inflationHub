import { connect } from 'react-redux';
import IRFuturesMonitor from './ir_futures_monitor';

const mapStateToProps = state => ({
    referenceData: state.referenceData,
    quotes: state.quotes
});

export default connect(mapStateToProps)(IRFuturesMonitor);