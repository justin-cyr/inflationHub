import React from 'react';
import $ from 'jquery';

import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import FloatingLabel from 'react-bootstrap/esm/FloatingLabel';
import Form from 'react-bootstrap/Form';
import ListGroup from 'react-bootstrap/ListGroup';
import Modal from 'react-bootstrap/Modal';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';

import { List, arrayMove } from 'react-movable';

import { defaultDataPoint } from './data_points/data_points';
import CpiLevelDataPointForm from './data_points/cpileveldatapoint';
import YoYDataPointForm from './data_points/yoydatapoint';

import CpiModelResults from './results/cpi_model_results';

class CurveBuilder extends React.Component {

    constructor(props) {
        super(props);

        const today = new Date();
        const year = today.getFullYear().toString();
        const month = (1 + today.getMonth()).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        const todayStr = year + '-' + month + '-' + day;

        this._isMounted = false;
        this.state = {
            curveDataPoints: [],
            numCurveDataPointsToAdd: 1,
            curveDataTypeToAdd: 'CpiLevelDataPoint',
            modelBaseDate: todayStr,
            selectedCurveType: undefined,
            showModal: true,
            // build settings
            selectedDomainX: undefined,
            selectedDomainY: undefined,
            selectedFittingMethod: undefined,
            // selection choices
            supportedCurveTypes: ['CPI', 'Seasonality'],
            supportedCurveDataPointTypes: [],
            buildSettingsUsage: { domainX:[], domainY:[], fitting_method_str:[] },
            // results
            buildResults: {}
        }

        // bind methods
        this.handleCurveType = this.handleCurveType.bind(this);
        this.handleInput = this.handleInput.bind(this);
        this.handleCurveDataInput = this.handleCurveDataInput.bind(this);
        this.flipSwitch = this.flipSwitch.bind(this);
        this.addDataPoints = this.addDataPoints.bind(this);
        this.removeDataPoint = this.removeDataPoint.bind(this);
        this.buildCurve = this.buildCurve.bind(this);
    }

    handleInput(type) {
        return (e) => {
            this.setState({ [type]: e.target.value },
                () => {console.log(type + ": " + e.target.value.toString())}
                );
        };
    }

    handleCurveDataInput(index, type, value) {
        let newCurveDataPoints = this.state.curveDataPoints;
        let point = newCurveDataPoints[index];
        point[type] = value;
        
        this.setState({
            curveDataPoints: newCurveDataPoints
        });
    }

    handleCurveType(curveType) {
        // Special input handler for curve type, which triggers async requests for supported options.
        this.setState({
            selectedCurveType: curveType,
            showModal: false
        },
        // callback
        () => {
            // clear curve data points
            this.setState({
                curveDataPoints: []
            });

            // get supported data tyes
            this.getCurveDataPointTypes(curveType);

            // get supported build methods
            this.getBuildSettingsUsage(curveType);
        }
        );
    }

    getCurveDataPointTypes(curveType) {
        $.ajax({
            url: '/supported_curve_data_point_types/' + curveType,
            method: 'GET',
            success: (response) => {
                this._isMounted && this.setState({
                    supportedCurveDataPointTypes: response.choices
                })
            }
        });
    }

    getBuildSettingsUsage(curveType) {
        $.ajax({
            url: '/get_build_settings_usage/' + curveType,
            method: 'GET',
            success: (response) => {
                // set initial build settings to defaults
                this._isMounted && this.setState({
                    buildSettingsUsage: response.usage,
                    selectedDomainX: response.usage.domainX[0],
                    selectedDomainY: response.usage.domainY[0],
                    selectedFittingMethod: response.usage.fitting_method_str[0]
                })
            }
        });
    }

    flipSwitch(index, type) {
        // Change boolean value this.state.[type] to !this.state.[type]
        let newCurveDataPoints = this.state.curveDataPoints;
        let point = newCurveDataPoints[index];
        point[type] = !point[type];

        this.setState({
            curveDataPoints: newCurveDataPoints
        });
    }

    addDataPoints() {
        // display more blank data points
        let newCurveDataPoints = this.state.curveDataPoints;
        for (let i = 0; i < this.state.numCurveDataPointsToAdd; ++i) {
            newCurveDataPoints.push(
                defaultDataPoint(this.state.curveDataTypeToAdd)
            );
        }
        
        this.setState({
            curveDataPoints: newCurveDataPoints
        },
            () => { console.log('Added ' + this.state.numCurveDataPointsToAdd.toString() 
                                + ' ' + this.state.curveDataTypeToAdd + ' data points')}
        );
    }

    removeDataPoint(index) {
        let newCurveDataPoints = this.state.curveDataPoints;
        newCurveDataPoints.splice(index, 1);
        this.setState({
            curveDataPoints: newCurveDataPoints
        });
    }

    buildCurve() {
        // send curve points, build options to backend
        $.ajax({
            url: 'build_model',
            method: 'POST',
            data: {
                model_type: this.state.selectedCurveType,
                base_date: this.state.modelBaseDate,
                model_data: JSON.stringify(this.state.curveDataPoints.filter(p => p.isActive)),
                domainX: this.state.selectedDomainX,
                domainY: this.state.selectedDomainY,
                fitting_method_str: this.state.selectedFittingMethod
            },
            success: (response) => {
                this._isMounted && this.setState({
                    buildResults: response.results
                },
                    () => console.log('Build curve')
                );
            }
        });
    }

    curveDataPointToForm(curveDataPoint, index) {
        switch (curveDataPoint.type) {

            case 'CpiLevelDataPoint':
                return <CpiLevelDataPointForm
                    key={index.toString()}
                    date={curveDataPoint.date}
                    isActive={curveDataPoint.isActive}
                    onDateChange={(d) => { this.handleCurveDataInput(index, 'date', d) }}
                    value={curveDataPoint.value}
                    onValueChange={(v) => { this.handleCurveDataInput(index, 'value', v) }}
                    onBoxCheck={() => { this.flipSwitch(index, 'isActive') }}
                    onCloseButton={() => { this.removeDataPoint(index) }}
                />;

            case 'YoYDataPoint':
                return <YoYDataPointForm 
                    key={index.toString()}
                    start_date={curveDataPoint.start_date}
                    isActive={curveDataPoint.isActive}
                    onDateChange={(d) => { this.handleCurveDataInput(index, 'start_date', d) }}
                    tenor={curveDataPoint.tenor}
                    onTenorChange={(t) => { this.handleCurveDataInput(index, 'tenor', t) }}
                    value={curveDataPoint.value}
                    onValueChange={(v) => { this.handleCurveDataInput(index, 'value', v) }}
                    onBoxCheck={() => { this.flipSwitch(index, 'isActive') }}
                    onCloseButton={() => { this.removeDataPoint(index) }}
                />;

            default:
                console.log('Unhandled type in ', curveDataPoint)
        }
    }

    componentDidMount() {
        // Request selection list choices
        this._isMounted = true;
    }

    componentWillUnmount() {
        this._isMounted = false;
    }

    render() {

        //const curveDataPoints = this.state.curveDataPoints.map((point, i) => this.curveDataPointToForm(point, i));
        const curveDataPoints = (
            <List
                values={ [...Array(this.state.curveDataPoints.length).keys()] }
                onChange={ ({ oldIndex, newIndex }) => { this.setState({ curveDataPoints: arrayMove(this.state.curveDataPoints, oldIndex, newIndex)}) } }
                transitionDuration={0}
                renderList={ ({ children, props }) => <ul {...props} style={{ listStyleType: "none", margin: 0, padding: 0 }}>{children}</ul> }
                renderItem={({ index, props }) => 
                    <li {...props} style={{ ...props.style, listStyleType: "none" }}>
                        { this.curveDataPointToForm(this.state.curveDataPoints[index], index) }
                    </li>
                }
            />
        );

        let resultsComponent = <div></div>;
        switch (this.state.selectedCurveType) {

            case 'CPI':
                resultsComponent = <CpiModelResults results={this.state.buildResults} />
                break;

            default:
                // unexpected
                console.log('Unexpected curve type: ' + this.state.selectedCurveType);
        }

        return (
            <Container fluid>
                <Row
                    style={{padding: "3px"}}
                >
                    <Col lg="auto">
                        <Row>
                            <Col lg="auto">
                                <Button
                                    id="add-curve-data-point-button"
                                    size="lg"
                                    variant="secondary"
                                    onClick={this.addDataPoints}
                                >Add</Button>
                            </Col>
                            <Col
                                style={{width: "137px"}}
                            >
                                <FloatingLabel
                                    controlId="numCurveDataPointsToAdd-Input"
                                    label="How many"
                                >
                                    <Form.Control
                                        type="number"
                                        step="1"
                                        min="1"
                                        max="30"
                                        value={this.state.numCurveDataPointsToAdd}
                                        isInvalid={this.state.numCurveDataPointsToAdd < 1 || this.state.numCurveDataPointsToAdd > 30}
                                        onChange={this.handleInput('numCurveDataPointsToAdd')}
                                    />
                                </FloatingLabel>
                            </Col>
                            <Col lg="auto">
                                <FloatingLabel
                                    controlId="curveDataTypeToAdd-Input"
                                    label="Data type"
                                >
                                    <Form.Select
                                        value={this.state.curveDataTypeToAdd || ''}
                                        onChange={this.handleInput('curveDataTypeToAdd')}
                                    >
                                        {this.state.supportedCurveDataPointTypes.map(s => <option key={s}>{s}</option>)}
                                    </Form.Select>
                                </FloatingLabel>  
                            </Col>
                        </Row>
                    </Col>
                    <Col
                        style={{textAlign: "center"}}
                    >
                        <Row className="justify-content-md-center">
                            <Col lg="auto">
                                <FloatingLabel
                                    controlId="curveType-Input"
                                    label="Curve type"
                                >
                                    <Form.Select
                                        value={this.state.selectedCurveType}
                                        onChange={(e) => { this.handleCurveType(e.target.value) }}
                                    >
                                        {this.state.supportedCurveTypes.map(s => <option key={s}>{s}</option>)}
                                    </Form.Select>
                                </FloatingLabel>  
                            </Col>
                            <Col lg="auto">
                                <FloatingLabel
                                    controlId="modelBaseDate-Input"
                                    label="Base date"
                                >
                                    <Form.Control
                                        style={{ width: "150px"}}
                                        type="date"
                                        value={this.state.modelBaseDate || ''}
                                        onChange={ this.handleInput('modelBaseDate') }
                                    >
                                    </Form.Control>
                                </FloatingLabel>  
                            </Col>
                            <Col lg="2">
                                <Button
                                    id="build-button"
                                    size="lg"
                                    type="submit"
                                    variant="primary"
                                    onClick={this.buildCurve}
                                >Build</Button>
                            </Col>
                        </Row>
                    </Col>
                </Row>
                <Row>
                    <Modal
                        show={this.state.showModal}
                        centered={true}
                    >
                        <Modal.Title
                            style={{
                                paddingTop: "10px",
                                paddingLeft: "10px",
                                color: "white",
                                backgroundColor: "#0d6efd"
                            }}
                        >Select Curve Type</Modal.Title>
                        <Modal.Body
                            style={{
                                backgroundColor: "#91ABBD"
                            }}
                        >
                            <Row className="justify-content-md-center">
                                <Col lg="auto">
                                    <FloatingLabel
                                        controlId="curveType-Modal-Input"
                                        label="Curve type"
                                    >
                                        <Form.Select
                                            value={this.state.selectedCurveType}
                                            onChange={(e) => { this.handleCurveType(e.target.value) }}
                                        >
                                            {['None'].concat(this.state.supportedCurveTypes).map(s => <option key={s}>{s}</option>)}
                                        </Form.Select>
                                    </FloatingLabel>
                                </Col>
                            </Row>
                        </Modal.Body>
                    </Modal>
                    <Tab.Container id="curve-builder-tabs" defaultActiveKey="#/curve_builder/curveData">
                        <Row>
                            <Col
                                md="auto"
                            >
                                <ListGroup>
                                    <ListGroup.Item action href="#/curve_builder/curveData">Curve Data</ListGroup.Item>
                                    <ListGroup.Item action href="#/curve_builder/buildSettings">Build Settings</ListGroup.Item>
                                    <ListGroup.Item action href="#/curve_builder/results">Results</ListGroup.Item>
                                </ListGroup>
                            </Col>
                            <Col
                                style={{ textAlign: "center" }}
                            >
                                <Tab.Content>
                                    {/* Curve Data Form */}
                                    <Tab.Pane eventKey="#/curve_builder/curveData">
                                        <h3>{'Curve data points'}</h3>
                                        {curveDataPoints}
                                    </Tab.Pane>

                                    {/* Build Settings Form */}
                                    <Tab.Pane eventKey="#/curve_builder/buildSettings">
                                        <h3>{'Build settings'}</h3>
                                        {/* Build settings selection inputs */}
                                        <Col>
                                            <Row className="justify-content-md-center">
                                                <Col lg="auto">
                                                    <FloatingLabel
                                                        controlId="domainX-Input"
                                                        label="Time domain"
                                                    >
                                                        <Form.Select
                                                            value={this.state.selectedDomainX}
                                                            onChange={this.handleInput('selectedDomainX')}
                                                        >
                                                            {this.state.buildSettingsUsage.domainX.map(s => <option key={s}>{s}</option>)}
                                                        </Form.Select>
                                                    </FloatingLabel>
                                                </Col>
                                                <Col lg="auto">
                                                    <FloatingLabel
                                                        controlId="domainY-Input"
                                                        label="Interpolation domain"
                                                    >
                                                        <Form.Select
                                                            value={this.state.selectedDomainY}
                                                            onChange={this.handleInput('selectedDomainY') }
                                                        >
                                                            {this.state.buildSettingsUsage.domainY.map(s => <option key={s}>{s}</option>)}
                                                        </Form.Select>
                                                    </FloatingLabel>
                                                </Col>
                                                <Col lg="auto">
                                                    <FloatingLabel
                                                        controlId="fittingMethod-Input"
                                                        label="Fitting method"
                                                    >
                                                        <Form.Select
                                                            value={this.state.selectedFittingMethod}
                                                            onChange={this.handleInput('selectedFittingMethod')}
                                                        >
                                                            {this.state.buildSettingsUsage.fitting_method_str.map(s => <option key={s}>{s}</option>)}
                                                        </Form.Select>
                                                    </FloatingLabel>
                                                </Col>
                                            </Row>
                                        </Col>
                                    </Tab.Pane>

                                    {/* Results */}
                                    <Tab.Pane eventKey="#/curve_builder/results">
                                        {resultsComponent}
                                    </Tab.Pane>

                                </Tab.Content>
                            </Col>
                        </Row>
                    </Tab.Container>
                </Row>
            </Container>
        );
    }

}

export default CurveBuilder;
