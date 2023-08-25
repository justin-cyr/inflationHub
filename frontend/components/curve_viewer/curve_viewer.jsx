import React from 'react';
import $ from 'jquery';


import Badge from 'react-bootstrap/Badge'
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Modal from 'react-bootstrap/Modal';
import Nav from 'react-bootstrap/Nav';
import Row from 'react-bootstrap/Row';
import Spinner from 'react-bootstrap/Spinner';
import Table from 'react-bootstrap/Table';

class CurveViewer extends React.Component {

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

        this._isMounted = false;
        this.state = {
            chartConfig: chartConfig,
            chartLayout: chartLayout,
            curveTemplates: {},
            curveData: {},
            curveResults: {},
            curveErrors: {},
            curveIsBuilding: {},
            curveIsBuilt: {},
            curveBuildAttempted: {},
            selectedCurve: '',
            selectedPlotData: {},
            selectedPlots: []
        }

        // bind methods
        this.buildAll = this.buildAll.bind(this);
        this.handleCurveSelect = this.handleCurveSelect.bind(this);
    }

    getCurveTemplates() {
        $.ajax({
            url: '/get_curve_templates',
            method: 'GET',
            success: (response) => {
                this._isMounted && this.setState({
                    curveTemplates: response.curve_templates,
                    curveIsBuilding: Object.fromEntries(Object.keys(response.curve_templates).map( key => [key, false])),
                    curveBuildAttempted: Object.fromEntries(Object.keys(response.curve_templates).map(key => [key, false]))
                })
            }
        });
    }

    buildOneCurve(curveName) {
        let curveIsBuilding = this.state.curveIsBuilding;
        curveIsBuilding[curveName] = true;
        this.setState({
            curveIsBuilding: curveIsBuilding
        },
        () => {
            let payLoad = {
                ...this.state.curveTemplates[curveName],
                handle: curveName
            };
            if ((this.state.curveData[curveName]) && (this.state.curveData[curveName].length > 0)) {
                payLoad['initial_guess'] = JSON.stringify(this.state.curveData[curveName].map(pt => pt[1]));
            }
            $.ajax({
                url: 'build_model',
                method: 'POST',
                data: payLoad,
                success: (response) => {
                    let curveData = this.state.curveData;
                    let curveResults = this.state.curveResults;
                    let curveErrors = this.state.curveErrors;
                    let curveIsBuilding = this.state.curveIsBuilding;
                    let curveIsBuilt = this.state.curveIsBuilt;
                    let curveBuildAttempted = this.state.curveBuildAttempted;

                    curveIsBuilding[curveName] = false;
                    curveIsBuilt[curveName] = false;
                    curveBuildAttempted[curveName] = true;

                    if (response.errors) {
                        curveErrors[curveName] = response.errors;
                    }
                    else if (response.results) {
                        curveData[curveName] = response.training_data
                        curveResults[curveName] = response.results;
                        curveIsBuilt[curveName] = true;
                    }

                    this._isMounted && this.setState({
                        curveData: curveData,
                        curveResults: curveResults,
                        curveErrors: curveErrors,
                        curveIsBuilding: curveIsBuilding,
                        curveIsBuilt: curveIsBuilt,
                        curveBuildAttempted: curveBuildAttempted
                    });
                }
            });
        }
        );
    }

    buildAll() {
        const curveTemplateNames = Object.keys(this.state.curveTemplates);
        if (curveTemplateNames.length > 0) {
            curveTemplateNames.map(key => this.buildOneCurve(key));
        }
    }

    handleCurveSelect(curveName) {
        
        const keys = this.state.curveResults[curveName] ? Object.keys(this.state.curveResults[curveName]) : [];
        let selectedPlotData = {};
        for (let key of keys) {
            selectedPlotData[key] = [];
            if (this.state.curveResults[curveName]) {
                selectedPlotData[key] = [{
                    x: this.state.curveResults[curveName][key].map(p => p[0]),
                    y: this.state.curveResults[curveName][key].map(p => p[1]),
                    type: 'scatter',
                    mode: 'lines',
                    showlegend: true,
                    name: key
                }];
            }
        }

        this.setState({
            showModal: true,
            selectedCurve: curveName,
            selectedPlotData: selectedPlotData,
            selectedPlots: keys
        },
        () => {
            for (let key of this.state.selectedPlots) {
                Plotly.react(key, this.state.selectedPlotData[key], this.state.chartLayout, this.state.chartConfig);
            }
        }
        );

    }

    componentDidMount() {
        this._isMounted = true;
        this.getCurveTemplates();
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render() {

        let curveDetailRows = [<tr key="title">
            <td style={{ textAlign: 'center' }}>
                <center>{'... Loading curve templates ...'}</center>
            </td>
        </tr>];

        const curveTemplateNames = Object.keys(this.state.curveTemplates);
        
        if (curveTemplateNames.length > 0) {
            curveDetailRows = curveTemplateNames.map(key =>
                <tr key={key}>
                    <td style={{ textAlign: 'center' }}>
                        <Row>
                            <Col>
                                <Row>
                                    <Col lg="auto">
                                        <Button
                                            id={"button-build-" + key}
                                            size="sm"
                                            type="submit"
                                            variant="secondary"
                                            onClick={() => this.buildOneCurve(key)}
                                        >
                                            Build
                                        </Button>
                                    </Col>
                                    <Col>
                                        {this.state.curveIsBuilding[key] && <Spinner variant="warning" animation="border" />}
                                        {!this.state.curveIsBuilding[key] && this.state.curveBuildAttempted[key] && <Badge pill
                                                                                bg={this.state.curveIsBuilt[key] ? 'success' : 'danger'}
                                                                            >
                                                                            {this.state.curveIsBuilt[key] ? 'Built' : 'Error'}
                                                                            </Badge>
                                        }
                                    </Col>
                                </Row>
                            </Col>
                            <Col>
                                <Nav
                                    onSelect={this.handleCurveSelect}
                                    fill="true"
                                >
                                    <Nav.Item>
                                        <Nav.Link
                                            eventKey={key}
                                        >
                                            {key}
                                        </Nav.Link>
                                    </Nav.Item>
                                </Nav>
                            </Col>
                        </Row>
                    </td>
                </tr>
            );
        }


        return (
            <Container fluid>
                <Row>
                    <Col lg="auto">
                        <Button
                            id="button-build-all"
                            size="lg"
                            type="submit"
                            variant="primary"
                            onClick={this.buildAll}
                        >
                            Build All
                        </Button>
                    </Col>
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
                                {this.state.selectedCurve}
                            </Modal.Title>
                        </Modal.Header>
                        <Modal.Body
                            style={{
                                backgroundColor: "#1c243b"
                            }}
                        >
                            <Container
                                id="charts-container"
                            >
                                <Row>
                                    <div id="instantaneous_forward_rate"></div>
                                </Row>
                                <Row>
                                    <div id="zero_rate"></div>
                                </Row>
                                <Row>
                                    <div id="df"></div>
                                </Row>
                                <Row>
                                    <div id="time_weighted_zero_rate"></div>
                                </Row>
                            </Container>
                        </Modal.Body>
                    </Modal>
                </Row>
                <Row>
                    <Table style={{ width: '700px'}}>
                        <tbody>
                            {curveDetailRows}
                        </tbody>
                    </Table>
                </Row>
            </Container>
        );
    }

}

export default CurveViewer;
