import React from 'react';

import CloseButton from 'react-bootstrap/CloseButton';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';

class YoYDataPointForm extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {

        return (
            <Container>
                <Row
                    className="curve-data-form"
                >
                    <Col md="auto">
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">Start Date:</Form.Label>
                            <Col
                                style={{ textAlign: "center" }}
                            >
                                <Form.Control
                                    style={{ width: "150px" }}
                                    type="date"
                                    value={this.props.start_date || ''}
                                    onChange={(e) => this.props.onDateChange(e.target.value)}
                                    disabled={!this.props.isActive}
                                >
                                </Form.Control>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col md="auto">
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">Tenor:</Form.Label>
                            <Col>
                                <Form.Control
                                    style={{ width: "60px" }}
                                    type="text"
                                    value={this.props.tenor || ''}
                                    onChange={(e) => this.props.onTenorChange(e.target.value)}
                                    disabled={!this.props.isActive}
                                >
                                </Form.Control>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col md="auto">
                        <Form.Group
                            as={Row}
                        >
                            <Form.Label column md="auto">YoY %:</Form.Label>
                            <Col>
                                <Form.Control
                                    style={{ width: "125px" }}
                                    type="number"
                                    value={this.props.value || ''}
                                    onChange={(e) => this.props.onValueChange(e.target.value)}
                                    step="0.01"
                                    disabled={!this.props.isActive}
                                >
                                </Form.Control>
                            </Col>
                        </Form.Group>
                    </Col>
                    <Col md="auto">
                        <Form.Check
                            type="checkbox"
                            checked={this.props.isActive}
                            onChange={() => this.props.onBoxCheck()}
                        />
                    </Col>
                    <Col md="auto">
                        <CloseButton
                            variant="white"
                            onClick={() => this.props.onCloseButton()}
                        />
                    </Col>
                </Row>
            </Container>
        );
    }

}

export default YoYDataPointForm;
