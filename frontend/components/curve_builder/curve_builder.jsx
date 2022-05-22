import React from 'react';
import $ from 'jquery';

import Button from 'react-bootstrap/Button';
import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';

class CurveBuilder extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            curveDataPoints: [],
            // selection choices
            supportedCurveDataPointTypes: []
        }

        // bind methods
        this.buildCurve = this.buildCurve.bind(this);
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

        return (
            <Container fluid>
                <Row>
                    <div>
                        <Button
                            id="build-button"
                            size="lg"
                            type="submit"
                            variant="primary"
                            onClick={this.buildCurve}
                        >Build</Button>
                    </div>
                   
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
