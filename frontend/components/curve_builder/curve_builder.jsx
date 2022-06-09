import React from 'react';
import $ from 'jquery';

import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import FloatingLabel from 'react-bootstrap/esm/FloatingLabel';
import Form from 'react-bootstrap/Form';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';

import { List, arrayMove } from 'react-movable';

import CpiLevelDataPointForm from './data_points/cpileveldatapoint_container';


class CurveBuilder extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            curveDataPoints: [{ type: 'CpiLevelDataPoint', date: '2022-03-01', value: 287.505 }, { type: 'CpiLevelDataPoint', date: '2022-04-01', value: 289.109 },],
            numCurveDataPointsToAdd: 1,
            curveDataTypeToAdd: '',
            selectedCurveType: '',
            // selection choices
            supportedCurveTypes: ['None supported'],
            supportedCurveDataPointTypes: []
        }

        // bind methods
        this.handleInput = this.handleInput.bind(this);
        this.handleCurveDataInput = this.handleCurveDataInput.bind(this);
        this.addDataPoints = this.addDataPoints.bind(this);
        this.buildCurve = this.buildCurve.bind(this);
    }

    handleInput(type) {
        return (e) => {
            this.setState({ [type]: e.target.value });
        };
    }

    handleCurveDataInput(index, type, value) {
        let newCurveDataPoints = this.state.curveDataPoints;
        let point = newCurveDataPoints[index];
        point[type] = value;
        
        this.setState({
            curveDataPoints: newCurveDataPoints
        },
        () => { console.log(newCurveDataPoints) }
        );
    }

    addDataPoints() {
        // display more blank data points
        console.log('Add ' + this.state.numCurveDataPointsToAdd.toString() + ' data points')
    }

    buildCurve() {
        // send curve points, build options to backend
        console.log('Build curve')
    }

    curveDataPointToForm(curveDataPoint, index) {
        switch (curveDataPoint.type) {

            case 'CpiLevelDataPoint':
                return <CpiLevelDataPointForm
                    key={index.toString()}
                    date={curveDataPoint.date}
                    onDateChange={(d) => { this.handleCurveDataInput(index, 'date', d) }}
                    value={curveDataPoint.value}
                    onValueChange={(v) => { this.handleCurveDataInput(index, 'value', v) }}
                        />;

            default:
                console.log('Unhandled type in ', curveDataPoint)
        }
    }

    componentDidMount() {
        // Request selection list choices
        $.ajax({
            url: '/supported_curve_data_point_types',
            method: 'GET',
            success: (response) => {
                this.setState({
                    supportedCurveDataPointTypes: response.choices
                })
            }
        });
    }

    render() {

        const curveDataPoints = this.state.curveDataPoints.map((point, i) => this.curveDataPointToForm(point, i));

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
                                        value={this.state.curveDataTypeToAdd}
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
                                        onChange={this.handleInput('selectedCurveType')}
                                    >
                                        {this.state.supportedCurveTypes.map(s => <option key={s}>{s}</option>)}
                                    </Form.Select>
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
                    <Tab.Container id="curve-builder-tabs" defaultActiveKey="#/curve_builder/curveData">
                        <Row>
                            <Col>
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
                                        {'build settings form'}
                                    </Tab.Pane>

                                    {/* Results */}
                                    <Tab.Pane eventKey="#/curve_builder/results">
                                        {'results display'}
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
