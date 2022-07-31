import React from 'react';
import $ from 'jquery';

import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import ListGroup from 'react-bootstrap/ListGroup';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

import FuzzySearch from 'react-fuzzy';

class DataViewer extends React.Component {

    constructor(props) {
        super(props);
        
        const today = new Date();
        const year = today.getFullYear().toString();
        const month = (1 + today.getMonth()).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        const todayStr = year + '-' + month + '-' + day;

        this._isMounted = false;
        this.state = {
            allDataNames: [],
            chartData: [],
            marketDataDate: todayStr,
        };

        // bind methods
        this.getData = this.getData.bind(this);
        this.handleInput = this.handleInput.bind(this);
        this.removeData = this.removeData.bind(this);
    }

    handleInput(type) {
        return (e) => {
            this.setState({ [type]: e.target.value });
        };
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
                    showlegend: true,
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
                
                this._isMounted && this.setState({
                    chartData: newChartData
                });

            }
        })
    }

    removeData(name) {
        // Delete this data series from chartData
        const index = this.state.chartData.findIndex((series) => series.name === name);
        if (index === -1) {
            // do nothing if series is not plotted
            return;
        }
        let newChartData = this.state.chartData;
        newChartData.splice(index, 1);
        this.setState({
            chartData: newChartData
        });
    }

    latestDataPointToDate(chartData, cutoffDate) {
        const dates = chartData.x;
        const values = chartData.y;

        if (cutoffDate < dates[0]) {
            return { date: undefined, value: undefined };
        }

        let i = dates.length - 1;
        while (i >= 0 && dates[i] > cutoffDate) { --i; }

        // dates[i] is max such that dates[i] <= cutoffDate
        return { date: dates[i], value: values[i] };
    }

    componentDidMount() {
        // Request default data
        this._isMounted = true;
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
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    componentDidUpdate() {
        // Chart layout
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
                tickformat: ",.1f",
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

        // selected data series
        let selectedDataSeries = Array();

        if (this.state.chartData.length > 0) {
            selectedDataSeries = this.state.chartData.map(chartData => 
                <ListGroup.Item
                    key={chartData.name}
                >
                    <Container fluid className="selected-data-series-container">
                        <Row>
                            <Col className="data-series-name-text">
                                {chartData.name}
                            </Col>
                            <Col xs md="1">
                                <CloseButton
                                    className="data-series-clear-btn"
                                    onClick={(e) => this.removeData(chartData.name) }
                                />
                            </Col>
                        </Row>
                    </Container>
                </ListGroup.Item>);
        }

        // Styles for data series fuzzy search
        const fsInputStyle = {
            color: "black",
            marginTop: "0px",
            marginBottom: "0px",
        };
        const fsInputWrapperStyle = {
            borderRadius: "5px",
            padding: "0px",
        };
        const fsListItemStyle = fsInputStyle;
        const fsListWrapperStyle = {};
        const fsSelectedListItemStyle = { ...fsInputStyle, ...{ backgroundColor: "#36A0C9" } };

        // Define latest data point table rows
        let latest_data_table = <center>{'No series selected'}</center>;
        if (this.state.chartData.length > 0) {

            const points = this.state.chartData.map(chartData => 
                this.latestDataPointToDate(chartData, this.state.marketDataDate)
            );

            const latest_data_rows = this.state.chartData.map((chartData, i) => 
                <tr key={chartData.name}>
                    <td>{chartData.name}</td>
                    <td>{points[i].value || ''}</td>
                    <td>{points[i].date || ''}</td>
                </tr>
            );

            latest_data_table = <Table
                id="latest-data-table"
                responsive
                hover
            >
                <tbody>
                    {latest_data_rows}
                </tbody>
            </Table>
        }

        return (
            <Container fluid>
                <Row>
                    <Col>
                    {/* Chart */}
                    <div id="data-viewer-chart"></div>
                    </Col>
                </Row>
                <Row>
                    <Col lg="auto">
                        <Row>
                            <FuzzySearch
                                className="data-series-search"
                                list={this.state.allDataNames.map(t => Object({name: t}))}
                                keys={['name']}
                                onSelect={(object) => this.getData(object.name)}
                                keyForDisplayName={'name'}
                                maxResults={7}
                                placeholder={'Search data series'}
                                inputStyle={fsInputStyle}
                                inputWrapperStyle={fsInputWrapperStyle}
                                listItemStyle={fsListItemStyle}
                                listWrapperStyle={fsListWrapperStyle}
                                selectedListItemStyle={fsSelectedListItemStyle}
                            />
                        </Row>
                        <Row>
                            <Form.Group
                                as={Col}
                                md
                            >
                            <Form.Label column md>Selected data series:</Form.Label>
                                <ListGroup>
                                    {selectedDataSeries}
                                </ListGroup>
                            </Form.Group>
                        </Row>
                    </Col>
                    <Col lg="auto">
                        {/* Latest values */}
                        Values up to
                        <Form.Control
                            style={{ width: "150px" }}
                            type="date"
                            value={this.state.marketDataDate || ''}
                            onChange={this.handleInput('marketDataDate')}
                        />
                        {latest_data_table}
                    </Col>
                    <Col>
                        {/* blank column to fill space to the right */}
                    </Col>
                </Row>
            </Container>
        );
    }

}

export default DataViewer;

