import React from 'react';

class StateLoader extends React.Component {
    constructor(props) {
        super(props);
    }

    componentDidMount() {
        this.props.updateTipsPrices();
    }

    render() {
        return (<div id="stateLoader"></div>);
    }

}

export default StateLoader;
