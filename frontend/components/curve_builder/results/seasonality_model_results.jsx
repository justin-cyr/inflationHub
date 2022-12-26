import React from 'react';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class SeasonalityModelResults extends React.Component {

    constructor(props) {
        super(props);

        const chartLayout = {
            paper_bgcolor: '#0a0e1a',
            plot_bgcolor: '#14171C',
            xaxis: {
                title: 'Date',
                titlefont: {
                    color: '#BDBDBD'
                },
                tickfont: { color: '#BDBDBD' },
                tickcolor: '#BDBDBD'
            },
            yaxis: {
                titlefont: {
                    color: '#BDBDBD'
                },
                autotypenumbers: 'strict',
                minexponent: 9,
                tickfont: { color: '#BDBDBD' },
                tickcolor: '#BDBDBD',
                tickformat: ",.2f",
                hoverformat: ",.3f"
            },
            showLegend: true,
            legend: {
                font: {
                    color: '#BDBDBD',
                }
            }
        };

        const chartConfig = {
            displayModeBar: true,
            scrollZoom: true,
        };

        this.state = {
            instantaneousRatePlotData: [],
            twzrPlotData: [],
            zeroRatePlotData: [],
            // chart options
            chartLayout: chartLayout,
            chartConfig: chartConfig
        }

    }

    componentDidUpdate(prevProps) {

        if (this.props.results !== prevProps.results) {

            let instantaneousRatePlotData = [];
            let twzrPlotData = [];
            let zeroRatePlotData = [];

            const keys = Object.keys(this.props.results);

            if (keys.includes('instantaneous_forward_rate')) {
                instantaneousRatePlotData.push({
                    x: this.props.results.instantaneous_forward_rate.map(p => p[0]),
                    y: this.props.results.instantaneous_forward_rate.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'Inst Fwd Rate'
                });
            }

            if (keys.includes('time_weighted_zero_rate')) {
                twzrPlotData.push({
                    x: this.props.results.time_weighted_zero_rate.map(p => p[0]),
                    y: this.props.results.time_weighted_zero_rate.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'Time-weighted Zero Rate'
                });
            }

            if (keys.includes('zero_rate')) {
                zeroRatePlotData.push({
                    x: this.props.results.zero_rate.map(p => p[0]),
                    y: this.props.results.zero_rate.map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: 'Zero Rate'
                });
            }

            this.setState({
                instantaneousRatePlotData: instantaneousRatePlotData,
                twzrPlotData: twzrPlotData,
                zeroRatePlotData: zeroRatePlotData
            },
                () => {
                    console.log(this.state);
                    Plotly.react('instantaneous-rate-plot', this.state.instantaneousRatePlotData, this.state.chartLayout, this.state.chartConfig);
                    Plotly.react('twzr-plot', this.state.twzrPlotData, this.state.chartLayout, this.state.chartConfig);
                    Plotly.react('zero-rate-plot', this.state.zeroRatePlotData, this.state.chartLayout, this.state.chartConfig);
                });
        }

    }

    render() {

        return (
            <Container>
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

export default SeasonalityModelResults;

