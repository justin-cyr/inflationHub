import React from 'react';
import $ from 'jquery';

import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

class TipsData extends React.Component {
    
    constructor(props) {
        super(props);

        this.state = {
            chartData: [],
            cusips: [],
            referenceData: [],
            // styles
            upColor:    '#198754',  // green
            downColor:  '#dc3545',  // red
            bbgColor:   '#ff6600',  // orange
        }

        // bind methods
        this.getTipsCusips = this.getTipsCusips.bind(this);
        this.getTipsData = this.getTipsData.bind(this);
        this.getTipsYields = this.getTipsYields.bind(this);
        this.getTipsPrices = this.getTipsPrices.bind(this);
    }

    getTipsCusips() {
        // Request TIPS CUSIPs
        $.ajax({
            url: '/tips_cusips',
            method: 'GET',
            success: (response) => {
                this.setState({
                    cusips: response.cusips
                },
                // get reference data for each cusip in callback 
                () => { this.state.cusips.map((cusip) => {
                            this.getTipsData(cusip);
                            this.getTipsYields(cusip)
                        }); 
                    });
            }
        });
    }

    getTipsData(cusip) {
        // Request TIPS reference data
        $.ajax({
            url: '/tips_reference_data/' + cusip,
            method: 'GET',
            success: (response) => {
                const responseData = response.referenceData;

                // insert into list in order of increasing maturity date
                const insertIndex = this.state.referenceData.findIndex((record) => record['tenor'] > responseData['tenor']);
                let newReferenceData = this.state.referenceData;
                if (insertIndex >= 0) {
                    newReferenceData.splice(insertIndex, 0, responseData);
                }
                else {
                    newReferenceData.push(responseData);
                }

                this.setState({
                    referenceData: newReferenceData
                });
            }
        });
    }

    getTipsYields(cusip) {
        $.ajax({
            url: '/tips_yield_data/' + cusip,
            method: 'GET',
            success: (response) => {
                // console.log(response);
            }
        });
    }

    getTipsPrices() {
        // Request TIPS price data
        $.ajax({
            url: '/tips_prices',
            method: 'GET',
            success: (response) => {
                const priceData = response.priceData;

                const series = {
                    x: priceData.map(record => record.TENOR),
                    y: priceData.map(record => record.YIELD / 100),
                    text: priceData.map(record => record.MATURITY),
                    type: 'scatter',
                    mode: 'markers',
                    showlegend: false,
                    name: 'Real Yields'
                }

                this.setState({
                    chartData: [series]
                });

                this.mapPricesToBonds(priceData);
            }
        });
    }

    mapPricesToBonds(priceData) {
        let newReferenceData = this.state.referenceData;
        for (const priceRecord of priceData) {
            const refDataIndex = newReferenceData.findIndex((record) => record['maturityDate'] === priceRecord['MATURITY']);
            if (refDataIndex >= 0) {
                newReferenceData[refDataIndex] = { ...newReferenceData[refDataIndex], ...priceRecord };
            }
        }
        
        this.setState({
            referenceData: newReferenceData
        },
            // () => console.log(this.state.referenceData)
        );
    }

    componentDidMount() {
        this.getTipsPrices();
        this.getTipsCusips();
    }

    componentDidUpdate() {
        // Chart layout
        const chartLayout = {
            paper_bgcolor: '#0a0e1a',
            plot_bgcolor: '#14171C',
            title: 'US TIPS Real Yields',
            titlefont: {
                color: '#BDBDBD'
            },
            xaxis: {
                title: 'Tenor (Y)',
                titlefont: {
                    color: '#BDBDBD'
                },
                tickfont: { color: '#BDBDBD' },
                tickcolor: '#BDBDBD',
                tickformat: ",.1f",
                hoverformat: ",.2f"
            },
            yaxis: {
                title: 'Real Yield',
                titlefont: {
                    color: '#BDBDBD'
                },
                autotypenumbers: 'strict',
                minexponent: 9,
                tickfont: { color: '#BDBDBD' },
                tickcolor: '#BDBDBD',
                tickformat: ",.1%",
                hoverformat: ",.3%"
            },
            showLegend: false,
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

        Plotly.react('real-yield-chart', this.state.chartData, chartLayout, chartConfig);
    }

    render() {

        // Reference data table
        let data_table = <center>{'... Loading data ...'}</center>;
        const numberStyle = {
            textAlign: 'center',
            color: this.state.bbgColor
        };

        if (this.state.referenceData) {

            const table_rows = this.state.referenceData.length === 0
                ? <tr key={'empty'}><td colSpan="7"><center>{'... Loading data ...'}</center></td></tr>
                : this.state.referenceData.map(record => 
                    <tr key={record['cusip']}>
                        <td style={{ textAlign: 'center' }}>{record['maturityDate']}</td>
                        <td style={{ textAlign: 'center' }}>{Number(record['interestRate']).toFixed(3) + '%'}</td>
                        <td style={{ textAlign: 'center' }}>{record['cusip']}</td>
                        <td style={{ textAlign: 'center' }}>{Number(record['tenor']).toFixed(2) + "Y"}</td>
                        <td style={{ textAlign: 'center' }}>{record['term']}</td>
                        <td style={{ textAlign: 'center',
                                     color: record['CHANGE'] >= 0 ? this.state.upColor : this.state.downColor
                                                         }}>{'YIELD' in record ? Number(record['YIELD']).toFixed(3) + '%' : ''}</td>
                        <td style={ numberStyle }>{'BID' in record ? Number(record['BID']).toFixed(2) : ''}</td>
                        <td style={ numberStyle }>{'ASK' in record ? Number(record['ASK']).toFixed(2) : ''}</td>
                        <td style={{ textAlign: 'center', 
                            fontWeight: Math.min(900, Math.max(100, -200 * (Number(record['BID_ASK_SPREAD']) - 2) + 900)) || 400
                                                         }}>{'BID_ASK_SPREAD' in record ? Number(record['BID_ASK_SPREAD']).toFixed(0) : ''}</td>
                    </tr>    
                );

            data_table = <Table
                id="tips-data-table"
                responsive="true"
            >
                <thead>
                    <tr style={{ color: '#bdbdbd'}}>
                        <th style={{ textAlign: 'center' }}>Maturity Date</th>
                        <th style={{ textAlign: 'center' }}>Coupon</th>
                        <th style={{ textAlign: 'center' }}>CUSIP</th>
                        <th style={{ textAlign: 'center' }}>Tenor</th>
                        <th style={{ textAlign: 'center' }}>Term</th>
                        <th style={{ textAlign: 'center' }}>YTM</th>
                        <th style={{ textAlign: 'center' }}>Bid</th>
                        <th style={{ textAlign: 'center' }}>Ask</th>
                        <th style={{ textAlign: 'center' }}>Spread</th>
                    </tr>
                </thead>
                <tbody
                    style={{ color: '#bdbdbd' }}
                >
                    {table_rows}
                </tbody>
            </Table>;
        }

        return (
            <Container fluid>
                <Row>
                    <center>
                        <h2>US Treasury Inflation-Protected Securities</h2>
                    </center>
                </Row>
                <Row>
                    {/* Chart */}
                    <div id="real-yield-chart"></div>
                </Row>
                <Row>
                    {/* Table */}
                    {data_table}
                </Row>
            </Container>
        );
    }

}

export default TipsData;
