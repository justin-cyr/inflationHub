import React from 'react';
import $ from 'jquery';

import Button from 'react-bootstrap/Button';
import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import FloatingLabel from 'react-bootstrap/esm/FloatingLabel';
import Form from 'react-bootstrap/Form';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';

import { List, arrayMove } from 'react-movable';

class CurveBuilder extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            curveDataPoints: [],
            numCurveDataPointsToAdd: 1,
            curveDataTypeToAdd: 'Curve Data',
            // selection choices
            supportedCurveDataPointTypes: []
        }

        // bind methods
        this.handleInput = this.handleInput.bind(this);
        this.addDataPoints = this.addDataPoints.bind(this);
        this.buildCurve = this.buildCurve.bind(this);
    }

    handleInput(type) {
        return (e) => {
            this.setState({ [type]: e.target.value });
        };
    }

    addDataPoints() {
        // display more blank data points
        console.log('Add ' + this.state.numCurveDataPointsToAdd.toString() + ' data points')
    }

    buildCurve() {
        // send curve points, build options to backend
        console.log('Build curve')
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

        const curveDataTypeChoices = this.state.supportedCurveDataPointTypes.map(s => <option key={s}>{s}</option>);

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
                                    as={Col}
                                >
                                    <Form.Select
                                        value={this.state.curveDataTypeToAdd}
                                        onChange={this.handleInput('curveDataTypeToAdd')}
                                    >
                                        {curveDataTypeChoices}
                                    </Form.Select>
                                </FloatingLabel>  
                            </Col>
                        </Row>
                    </Col>
                    <Col>
                        <Button
                            id="build-button"
                            size="lg"
                            type="submit"
                            variant="primary"
                            onClick={this.buildCurve}
                        >Build</Button>
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
                            <Col>
                                <Tab.Content>
                                    {/* Curve Data Form */}
                                    <Tab.Pane eventKey="#/curve_builder/curveData">
                                        {'curve data form'}
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
