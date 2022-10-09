import { connect } from 'react-redux';

import TipsData from './tips_data';

const mapStateToProps = state => ({
    quotes: state.quotes
});

export default connect(mapStateToProps)(TipsData);
