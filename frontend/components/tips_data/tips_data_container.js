import { connect } from 'react-redux';

import TipsData from './tips_data';

const mapStateToProps = state => ({
    quotes: state.quotes,
    referenceData: state.referenceData
});

export default connect(mapStateToProps)(TipsData);
