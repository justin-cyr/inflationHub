import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';

class DataViewer extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            allDataNames: [],
            chartData: [],
        };

        // bind methods
        this.getData = this.getData.bind(this);
    }

    getData(name) {
        // Request default data
        $.ajax({
            url: '/data/' + name,
            method: 'GET',
            success: (response) => {
                console.log(response.data);
                const dates = response.data.Date;
                let values = [];
                let title = "";
                for (const key of Object.keys(response.data)) {
                    if (key != "Date") {
                        title = key;
                        values = response.data[key];
                        break;
                    }
                }
                
                // add to chart data
                const newSeries = {
                    x: dates,
                    y: values,
                    type: 'scatter',
                    mode: 'lines',
                    name: title,
                }

                this.setState({
                    chartData: this.state.chartData.concat(newSeries)
                });

            }
        })
    }

    componentDidMount() {
        // Request default data
        $.ajax({
            url: '/all_data_names',
            method: 'GET',
            success: (response) => {
                this.setState({
                    allDataNames: response.names
                });
            }
        });

        this.getData('US CPI NSA');
        this.getData('US CPI SA');
    }

    componentDidUpdate() {
        // Chart layout
        const chartLayout = {
            title: 'Data Viewer',
            paper_bgcolor: '#091020',
            plot_bgcolor: '#14171C',
            showLegend: true,
            xaxis: {
                title: 'Date',
                tickfont: { color: '#91ABBD' },
                tickcolor: '#91ABBD'
            },
            yaxis: {
                autotypenumbers: 'strict',
                minexponent: 9,
                tickfont: { color: '#91ABBD' },
                tickcolor: '#91ABBD',
                tickformat: ",.0f",
                hoverformat: ",.3f"
            },
        };

        const chartConfig = {
            displayModeBar: true,
            scrollZoom: true,
        };

        Plotly.react('data-viewer-chart', this.state.chartData, chartLayout, chartConfig);
    }

    render() {


        return (
            <Container fluid>
                <Row>
                    This is the DataViewer.
                </Row>
                <Row>
                    {/* Chart */}
                    <div id="data-viewer-chart"></div>
                </Row>
            </Container>
        );
    }

}

export default DataViewer;

