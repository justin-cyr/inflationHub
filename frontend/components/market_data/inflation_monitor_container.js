import { connect } from 'react-redux';
import InflationMonitor from './inflation_monitor';

const mapStateToProps = state => ({
    referenceData: state.referenceData,
    quotes: state.quotes
});

export default connect(mapStateToProps)(InflationMonitor);