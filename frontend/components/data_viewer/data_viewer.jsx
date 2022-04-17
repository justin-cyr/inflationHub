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
        if (this.state.chartData.findIndex((series) => series.name === name) >= 0) {
            // do nothing if series already is already plotted
            return;
        }

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

                // insert new series in alphabetical order by title
                const insertIndex = this.state.chartData.findIndex((series) => series.name > title);
                let newChartData = this.state.chartData;
                if (insertIndex >= 0) {
                    // insert at index
                    newChartData.splice(insertIndex, 0, newSeries);
                }
                else {
                    // append
                    newChartData.push(newSeries);
                }
                
                this.setState({
                    chartData: newChartData
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
            titlefont: {
                color: '#BDBDBD'
            },
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
                tickformat: ",.0f",
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

