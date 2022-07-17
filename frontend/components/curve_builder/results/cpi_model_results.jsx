import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class CpiModelResults extends React.Component {
    
    constructor(props) {
        super(props);

        let cpiPlotData = [];
        let instantaneousRatePlotData = [];
        let twzrPlotData = [];
        let zeroRatePlotData = [];

        this.state = {
            cpiPlotData: cpiPlotData,
            instantaneousRatePlotData: instantaneousRatePlotData,
            twzrPlotData: twzrPlotData,
            zeroRatePlotData: zeroRatePlotData
        }        

    }

    componentDidUpdate(prevProps) {

        if (this.props.results !== prevProps.results) {

            let cpiPlotData = [];
            let instantaneousRatePlotData = [];
            let twzrPlotData = [];
            let zeroRatePlotData = [];

            const keys = Object.keys(this.props.results);

            if (keys.includes('cpi')) {
                cpiPlotData = [{
                    x: this.props.results.cpi.map(p => p[0]),
                    y: this.props.results.cpi.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'CPI Level'
                }];
            }

            if (keys.includes('instantaneous_forward_rate')) {
                instantaneousRatePlotData = [{
                    x: this.props.results.instantaneous_forward_rate.map(p => p[0]),
                    y: this.props.results.instantaneous_forward_rate.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'Inst Fwd Rate'
                }];
            }

            if (keys.includes('time_weighted_zero_rate')) {
                twzrPlotData = [{
                    x: this.props.results.time_weighted_zero_rate.map(p => p[0]),
                    y: this.props.results.time_weighted_zero_rate.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'Time-weighted Zero Rate'
                }];
            }

            if (keys.includes('zero_rate')) {
                zeroRatePlotData = [{
                    x: this.props.results.zero_rate.map(p => p[0]),
                    y: this.props.results.zero_rate.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'Zero Rate'
                }];
            }

            this.setState({
                cpiPlotData: cpiPlotData,
                instantaneousRatePlotData: instantaneousRatePlotData,
                twzrPlotData: twzrPlotData,
                zeroRatePlotData: zeroRatePlotData
            },
            () => {
                console.log(this.state);
                Plotly.react('cpi-plot', this.state.cpiPlotData);
                Plotly.react('instantaneous-rate-plot', this.state.instantaneousRatePlotData);
                Plotly.react('twzr-plot', this.state.twzrPlotData);
                Plotly.react('zero-rate-plot', this.state.zeroRatePlotData);
            });
        }

    }

    render () {

        return (
            <Container>
                <Row>
                    <div id="cpi-plot"></div>
                </Row>
                <Row>
                    <div id="instantaneous-rate-plot"></div>
                </Row>
                <Row>
                    <div id="twzr-plot"></div>
                </Row>
                <Row >
                    <div id="zero-rate-plot"></div>
                </Row>
            </Container>
        );
    }

}

export default CpiModelResults;
