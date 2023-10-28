import React from 'react';
import $, { merge } from 'jquery';

import Container from 'react-bootstrap/Container';
import Modal from 'react-bootstrap/Modal';
import Nav from 'react-bootstrap/Nav';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';

class TipsData extends React.Component {
    
    constructor(props) {
        super(props);

        const today = new Date();
        const year = today.getFullYear().toString();
        const month = (1 + today.getMonth()).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        const todayStr = year + '-' + month + '-' + day;

        let referenceData = Object.values(this.props.referenceData.tips.bonds);
        referenceData = referenceData.sort((a, b) => a.tenor - b.tenor );

        const priceData = this.props.quotes.daily.tipsPrices.priceData;
        for (let i = 0; i < referenceData.length; ++i) {
            referenceData[i] = this.mergePriceToReferenceData(priceData, referenceData[i]);
        }

        const series = {
            x: priceData.map(record => record.TENOR),
            y: priceData.map(record => record.YIELD / 100),
            text: priceData.map(record => record.MATURITY),
            type: 'scatter',
            mode: 'markers',
            showlegend: false,
            name: 'Real Yields'
        }

        this._isMounted = false;
        this.state = {
            chartData: [series],
            cusips: this.props.referenceData.tips.cusips,
            priceData: [],
            referenceData: referenceData,
            yieldData: [],
            todayStr: todayStr,
            showModal: false,
            // selected for display in modal
            selectedCUSIP: '',
            selectedReferenceData: {},
            selectedYieldData: {},
            selectedYieldChartData: {},
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
        this.handleCusipSelect = this.handleCusipSelect.bind(this);
        this.liveYieldColor = this.liveYieldColor.bind(this);
    }

    getTipsCusips() {
        // Request TIPS CUSIPs
        this.state.cusips.map((cusip) => {
            this.getTipsYields(cusip);
        });
        const newReferenceData = this.state.referenceData.map(refData => this.mergePriceToReferenceData(this.state.priceData, refData));
        this._isMounted && this.setState({
            referenceData: newReferenceData
        });
    }

    getTipsData(cusip) {
        // Request TIPS reference data
        $.ajax({
            url: '/tips_reference_data/' + cusip,
            method: 'GET',
            success: (response) => {
                let responseData = response.referenceData;

                // merge prices
                responseData = this.mergePriceToReferenceData(this.state.priceData, responseData);

                // insert into list in order of increasing maturity date
                const insertIndex = this.state.referenceData.findIndex((record) => record['tenor'] > responseData['tenor']);
                let newReferenceData = this.state.referenceData;
                if (insertIndex >= 0) {
                    newReferenceData.splice(insertIndex, 0, responseData);
                }
                else {
                    newReferenceData.push(responseData);
                }

                this._isMounted && this.setState({
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

                if (response.data) {
                    this._isMounted && this.setState({
                        yieldData: { ...this.state.yieldData, ...{ [cusip]: response.data } }
                    });
                }
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

                this._isMounted && this.setState({
                    chartData: [series],
                    priceData: priceData
                });

                this.mapPricesToBonds(priceData);
            }
        });
    }

    mergePriceToReferenceData(priceData, record) {
        const i = priceData.findIndex((priceRecord) => (
                    (record['maturityDate'] === priceRecord['MATURITY']) &&
                    (Number(record['interestRate']) === priceRecord['COUPON']))
        );
        if (i >= 0) {
            record = {...record, ...priceData[i]};
        }
        return record;
    }

    mapPricesToBonds(priceData) {
        let newReferenceData = this.state.referenceData;
        for (let i = 0; i < newReferenceData.length; ++i) {
            newReferenceData[i] = this.mergePriceToReferenceData(priceData, newReferenceData[i]);
        }
        
        this._isMounted && this.setState({
            referenceData: newReferenceData
        },
            // () => console.log(this.state.referenceData)
        );
    }

    getReferenceDataForCusip(cusip) {
        const i = this.state.referenceData.findIndex((record) => record['cusip'] === cusip);
        if (i >= 0) {
            return this.state.referenceData[i];
        } else {
            return {};
        }
    }

    handleCusipSelect(cusip) {

        let yieldData = {};
        yieldData = this.state.yieldData[cusip];
        
        const referenceDataForCusip = this.getReferenceDataForCusip(cusip);

        // Append YTM from price data
        if (yieldData && yieldData.Date && yieldData['Real Yield'] && referenceDataForCusip.YIELD) {
            // TODO: use the last market close date instead of today
            yieldData.Date.push(this.state.todayStr);
            yieldData['Real Yield'].push(referenceDataForCusip.YIELD);
        }
        else if (referenceDataForCusip.YIELD) {
            // use as yield data
            yieldData = {
                'Date': [this.state.todayStr],
                'Real Yield': [referenceDataForCusip.YIELD]
            };
        }

        let chartData = {};
        if (yieldData && yieldData.Date && yieldData['Real Yield']) {
            const mode = yieldData.Date.length > 1 ? 'lines' : 'markers';
            chartData = {
                x: yieldData['Date'],
                y: yieldData['Real Yield'],
                type: 'scatter',
                mode: mode,
                showlegend: false,
                name: 'Real Yield'
            };
        }

        this.setState({
            showModal: true,
            selectedCUSIP: cusip,
            selectedReferenceData: referenceDataForCusip,
            selectedYieldData: yieldData,
            selectedYieldChartData: chartData
        },
        () => {
            const chartLayout = {
                paper_bgcolor: '#0a0e1a',
                plot_bgcolor: '#14171C',
                title: 'Real Yield to Maturity',
                titlefont: {
                    color: '#BDBDBD'
                },
                xaxis: {
                    title: 'Date',
                    titlefont: {
                        color: '#BDBDBD'
                    },
                    tickfont: { color: '#BDBDBD' },
                    tickcolor: '#BDBDBD',
                },
                yaxis: {
                    title: 'YTM (%)',
                    titlefont: {
                        color: '#BDBDBD'
                    },
                    autotypenumbers: 'strict',
                    minexponent: 9,
                    tickfont: { color: '#BDBDBD' },
                    tickcolor: '#BDBDBD',
                    tickformat: ",.1",
                    hoverformat: ",.3"
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

            Plotly.react('cusip-yield-time-series-chart', [this.state.selectedYieldChartData], chartLayout, chartConfig);
        }
        );
    }

    liveYieldColor(record) {
        const hasCloseYield = ('YIELD' in record);
        const hasLiveYield = (record['cusip'] in this.props.quotes.daily.tips.byCusip) && ('yield' in this.props.quotes.daily.tips.byCusip[record['cusip']]);
        if (hasCloseYield && hasLiveYield) {
            const closeYield = record['YIELD'];
            const liveYield = this.props.quotes.daily.tips.byCusip[record['cusip']].yield;

            return (liveYield > closeYield) ? this.state.downColor : this.state.upColor;
        }
        else {
            return this.state.bbgColor;
        }
    }

    componentDidMount() {
        this._isMounted = true;
        this.getTipsPrices();
        this.getTipsCusips();
    }

    componentWillUnmount() {
        this._isMounted = false;
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
                        <td style={{ textAlign: 'center' }}>{
                            <Nav
                                onSelect={this.handleCusipSelect}
                                fill="true"
                            >
                                <Nav.Item>
                                    <Nav.Link
                                        eventKey={record['cusip']}
                                    >
                                        {record['cusip']}
                                    </Nav.Link>
                                </Nav.Item>
                            </Nav>
                        }</td>
                        <td style={{ textAlign: 'center' }}>{Number(record['tenor']).toFixed(2) + "Y"}</td>
                        <td style={{ textAlign: 'center' }}>{record['term']}</td>
                        <td style={{ textAlign: 'center',
                                     color: record['CHANGE'] >= 0 ? this.state.upColor : this.state.downColor
                                                         }}>{'YIELD' in record ? Number(record['YIELD']).toFixed(3) + '%' : ''}</td>
                        <td style={{ textAlign: 'center',
                                    color: this.liveYieldColor(record)
                        }}>{record['cusip'] in this.props.quotes.daily.tips.byCusip ? Number(this.props.quotes.daily.tips.byCusip[record['cusip']].yield).toFixed(3) + '%' : ''}</td>
                        <td style={ numberStyle }>{'BID' in record ? Number(record['BID']).toFixed(2) : ''}</td>
                        <td style={ numberStyle }>{'ASK' in record ? Number(record['ASK']).toFixed(2) : ''}</td>
                    </tr>    
                );

            data_table = <div
                style={{ height: '500px', overflow: 'auto' }}
            >
            <Table
                id="tips-data-table"
                responsive
                hover
            >
                <thead>
                    <tr style={{ color: '#bdbdbd'}}>
                        <th style={{ textAlign: 'center' }}>Maturity Date</th>
                        <th style={{ textAlign: 'center' }}>Coupon</th>
                        <th style={{ textAlign: 'center' }}>CUSIP</th>
                        <th style={{ textAlign: 'center' }}>Tenor</th>
                        <th style={{ textAlign: 'center' }}>Term</th>
                        <th style={{ textAlign: 'center' }}>Close Yield</th>
                        <th style={{ textAlign: 'center' }}>Live Yield</th>
                        <th style={{ textAlign: 'center' }}>Bid</th>
                        <th style={{ textAlign: 'center' }}>Ask</th>
                    </tr>
                </thead>
                <tbody
                    style={{ color: '#bdbdbd' }}
                >
                    {table_rows}
                </tbody>
            </Table>
            </div>;
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
                    <Modal
                        show={this.state.showModal}
                        centered={true}
                        size="lg"
                        onHide={() => this.setState({ showModal: false })}
                    >
                        <Modal.Header
                            closeButton
                            style={{
                                backgroundColor: "#1c243b",
                            }}
                        >
                            <Modal.Title
                                style={{
                                    paddingTop: "5px",
                                    paddingLeft: "5px",
                                    backgroundColor: "#1c243b",
                                }}
                            >
                                {
                                    this.state.selectedReferenceData['term'] + ' '
                                    + Number(this.state.selectedReferenceData['interestRate']).toFixed(3) + '% TIPS due '
                                    + this.state.selectedReferenceData['maturityDate'] + ' '
                                    + '(' + this.state.selectedCUSIP + ')'
                                }
                            </Modal.Title>
                        </Modal.Header>
                        <Modal.Body
                            style={{
                                backgroundColor: "#1c243b"
                            }}
                        >
                            <div id="cusip-yield-time-series-chart"></div>
                        </Modal.Body>
                    </Modal>
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
